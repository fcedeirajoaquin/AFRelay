import os
from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from config.paths import AfipPaths


def _mock_paths(tmp_path, cuit):
    return AfipPaths(
        base_xml=tmp_path / f"xml/{cuit}",
        base_crypto=tmp_path / "crypto",
        base_certs=tmp_path / f"certs/{cuit}",
    )


class TestSaveXml:
    def test_saves_to_cuit_directory(self, tmp_path):
        cuit = "20304050607"
        paths = _mock_paths(tmp_path, cuit)

        with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths):
            from service.xml_management.xml_builder import save_xml

            root = etree.Element("test")
            etree.SubElement(root, "data").text = "hello"
            save_xml(root, "test.xml", cuit)

            saved_path = paths.base_xml / "test.xml"
            assert saved_path.exists()

            tree = etree.parse(str(saved_path))
            assert tree.getroot().find("data").text == "hello"

    def test_different_cuits_save_to_different_dirs(self, tmp_path):
        cuit1 = "20304050607"
        cuit2 = "27123456789"

        for cuit in [cuit1, cuit2]:
            paths = _mock_paths(tmp_path, cuit)
            with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths):
                from service.xml_management.xml_builder import save_xml

                root = etree.Element("test")
                etree.SubElement(root, "cuit").text = cuit
                save_xml(root, "data.xml", cuit)

        path1 = tmp_path / f"xml/{cuit1}/data.xml"
        path2 = tmp_path / f"xml/{cuit2}/data.xml"
        assert path1.exists()
        assert path2.exists()

        tree1 = etree.parse(str(path1))
        tree2 = etree.parse(str(path2))
        assert tree1.getroot().find("cuit").text == cuit1
        assert tree2.getroot().find("cuit").text == cuit2


class TestXmlExists:
    def test_returns_true_when_exists(self, tmp_path):
        cuit = "20304050607"
        paths = _mock_paths(tmp_path, cuit)
        os.makedirs(paths.base_xml, exist_ok=True)
        (paths.base_xml / "test.xml").write_text("<xml/>")

        with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths):
            from service.xml_management.xml_builder import xml_exists
            assert xml_exists("test.xml", cuit) is True

    def test_returns_false_when_not_exists(self, tmp_path):
        cuit = "20304050607"
        paths = _mock_paths(tmp_path, cuit)

        with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths):
            from service.xml_management.xml_builder import xml_exists
            assert xml_exists("nonexistent.xml", cuit) is False

    def test_isolated_between_cuits(self, tmp_path):
        cuit1 = "20304050607"
        cuit2 = "27123456789"

        paths1 = _mock_paths(tmp_path, cuit1)
        os.makedirs(paths1.base_xml, exist_ok=True)
        (paths1.base_xml / "test.xml").write_text("<xml/>")

        paths2 = _mock_paths(tmp_path, cuit2)

        with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths1):
            from service.xml_management.xml_builder import xml_exists
            assert xml_exists("test.xml", cuit1) is True

        with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths2):
            from service.xml_management.xml_builder import xml_exists
            assert xml_exists("test.xml", cuit2) is False


class TestExtractTokenAndSign:
    def test_extracts_from_correct_cuit_dir(self, tmp_path):
        cuit = "20304050607"
        paths = _mock_paths(tmp_path, cuit)
        os.makedirs(paths.base_xml, exist_ok=True)

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <loginTicketResponse>
            <credentials>
                <token>test-token-123</token>
                <sign>test-sign-456</sign>
            </credentials>
        </loginTicketResponse>"""
        (paths.base_xml / "loginTicketResponse.xml").write_text(xml_content)

        with patch("service.xml_management.xml_builder.paths.get_afip_paths", return_value=paths):
            from service.xml_management.xml_builder import extract_token_and_sign_from_xml
            token, sign = extract_token_and_sign_from_xml(cuit)
            assert token == "test-token-123"
            assert sign == "test-sign-456"
