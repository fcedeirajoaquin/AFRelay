from pathlib import Path

import pytest

from config.paths import AfipPaths, get_afip_paths, get_as_bytes


class TestGetAfipPaths:
    def test_returns_correct_paths_for_cuit(self):
        cuit = "20304050607"
        paths = get_afip_paths(cuit)

        assert paths.base_xml == Path(f"service/xml_management/app_xml_files/{cuit}")
        assert paths.base_certs == Path(f"service/app_certs/{cuit}")
        assert paths.base_crypto == Path("service/crypto")

    def test_different_cuits_return_different_paths(self):
        paths1 = get_afip_paths("20304050607")
        paths2 = get_afip_paths("27123456789")

        assert paths1.base_xml != paths2.base_xml
        assert paths1.base_certs != paths2.base_certs

    def test_login_request_path(self):
        paths = get_afip_paths("20304050607")
        assert paths.login_request == Path("service/xml_management/app_xml_files/20304050607/loginTicketRequest.xml")

    def test_login_response_path(self):
        paths = get_afip_paths("20304050607")
        assert paths.login_response == Path("service/xml_management/app_xml_files/20304050607/loginTicketResponse.xml")

    def test_certificate_path(self):
        paths = get_afip_paths("20304050607")
        assert paths.certificate == Path("service/app_certs/20304050607/returned_certificate.pem")

    def test_private_key_path(self):
        paths = get_afip_paths("20304050607")
        assert paths.private_key == Path("service/app_certs/20304050607/PrivateKey.key")


class TestGetAsBytes:
    def test_reads_files_for_correct_cuit(self, tmp_path, monkeypatch):
        cuit = "20304050607"
        xml_dir = tmp_path / f"service/xml_management/app_xml_files/{cuit}"
        certs_dir = tmp_path / f"service/app_certs/{cuit}"
        xml_dir.mkdir(parents=True)
        certs_dir.mkdir(parents=True)

        (xml_dir / "loginTicketRequest.xml").write_bytes(b"<xml>request</xml>")
        (certs_dir / "PrivateKey.key").write_bytes(b"private-key-data")
        (certs_dir / "returned_certificate.pem").write_bytes(b"certificate-data")

        def mock_get_paths(c):
            return AfipPaths(
                base_xml=tmp_path / f"service/xml_management/app_xml_files/{c}",
                base_crypto=tmp_path / "service/crypto",
                base_certs=tmp_path / f"service/app_certs/{c}",
            )

        monkeypatch.setattr("config.paths.get_afip_paths", mock_get_paths)

        req, key, cert = get_as_bytes(cuit)
        assert req == b"<xml>request</xml>"
        assert key == b"private-key-data"
        assert cert == b"certificate-data"
