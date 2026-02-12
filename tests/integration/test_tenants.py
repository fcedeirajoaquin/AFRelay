import io
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("service.api.tenants.CERTS_BASE", tmp_path / "certs")
    monkeypatch.setattr("service.api.tenants.XML_BASE", tmp_path / "xml")

    with patch("service.utils.afip_token_scheduler.start_scheduler"), \
         patch("service.utils.afip_token_scheduler.stop_scheduler"), \
         patch("service.utils.jwt_validator.verify_token", return_value="test"):
        from service.api.app import app
        yield TestClient(app)


@pytest.fixture
def certs_base(tmp_path):
    return tmp_path / "certs"


@pytest.fixture
def xml_base(tmp_path):
    return tmp_path / "xml"


class TestUploadCerts:
    @patch("service.api.tenants.generate_afip_access_token", new_callable=AsyncMock, return_value={"status": "success"})
    def test_upload_creates_directories_and_files(self, mock_gen, client, certs_base, xml_base):
        cuit = "20304050607"
        response = client.post(
            f"/tenants/{cuit}/certs",
            files={
                "private_key": ("PrivateKey.key", io.BytesIO(b"key-data"), "application/octet-stream"),
                "certificate": ("cert.pem", io.BytesIO(b"cert-data"), "application/x-pem-file"),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["certs_uploaded"] is True
        assert data["cuit"] == cuit

        assert (certs_base / cuit / "PrivateKey.key").exists()
        assert (certs_base / cuit / "returned_certificate.pem").exists()
        assert (xml_base / cuit).exists()

    def test_upload_rejects_invalid_cuit(self, client):
        response = client.post(
            "/tenants/abc/certs",
            files={
                "private_key": ("key.key", io.BytesIO(b"data"), "application/octet-stream"),
                "certificate": ("cert.pem", io.BytesIO(b"data"), "application/x-pem-file"),
            },
        )
        assert response.status_code == 400


class TestGetTenantStatus:
    def test_status_no_certs(self, client):
        response = client.get("/tenants/20304050607/status")
        assert response.status_code == 200
        data = response.json()
        assert data["certs_uploaded"] is False

    @patch("service.api.tenants.generate_afip_access_token", new_callable=AsyncMock, return_value={"status": "success"})
    def test_status_after_upload(self, mock_gen, client, certs_base):
        cuit = "20304050607"
        client.post(
            f"/tenants/{cuit}/certs",
            files={
                "private_key": ("key.key", io.BytesIO(b"key"), "application/octet-stream"),
                "certificate": ("cert.pem", io.BytesIO(b"cert"), "application/x-pem-file"),
            },
        )
        response = client.get(f"/tenants/{cuit}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["certs_uploaded"] is True


class TestDeleteTenant:
    @patch("service.api.tenants.generate_afip_access_token", new_callable=AsyncMock, return_value={"status": "success"})
    def test_delete_removes_dirs(self, mock_gen, client, certs_base, xml_base):
        cuit = "20304050607"
        client.post(
            f"/tenants/{cuit}/certs",
            files={
                "private_key": ("key.key", io.BytesIO(b"key"), "application/octet-stream"),
                "certificate": ("cert.pem", io.BytesIO(b"cert"), "application/x-pem-file"),
            },
        )

        response = client.delete(f"/tenants/{cuit}")
        assert response.status_code == 200
        assert not (certs_base / cuit).exists()
        assert not (xml_base / cuit).exists()


class TestListTenants:
    @patch("service.api.tenants.generate_afip_access_token", new_callable=AsyncMock, return_value={"status": "success"})
    def test_lists_uploaded_tenants(self, mock_gen, client):
        for cuit in ["20304050607", "27123456789"]:
            client.post(
                f"/tenants/{cuit}/certs",
                files={
                    "private_key": ("key.key", io.BytesIO(b"key"), "application/octet-stream"),
                    "certificate": ("cert.pem", io.BytesIO(b"cert"), "application/x-pem-file"),
                },
            )

        response = client.get("/tenants")
        assert response.status_code == 200
        data = response.json()
        cuits = [t["cuit"] for t in data["tenants"]]
        assert "20304050607" in cuits
        assert "27123456789" in cuits
