"""Tests for WSFE endpoint validation and error handling."""

import pytest
from httpx import AsyncClient

from service.api.app import app
from service.utils.jwt_validator import verify_token


@pytest.fixture
def override_auth():
    async def fake_verify():
        return {"user": "test-user", "roles": ["test"]}

    app.dependency_overrides[verify_token] = fake_verify
    yield
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture
def client() -> AsyncClient:
    return AsyncClient(app=app, base_url="http://test")


# --- Tests ---


@pytest.mark.asyncio
async def test_fecae_solicitar_invalid_payload_returns_422(override_auth, client):
    """Sending an empty/invalid payload should return 422 from Pydantic validation."""
    response = await client.post("/wsfe/FECAESolicitar", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_fecae_solicitar_missing_cuit_returns_422(override_auth, client):
    """Payload with Auth but missing Cuit should return 422."""
    payload = {
        "Auth": {},
        "FeCAEReq": {
            "FeCabReq": {"CantReg": 1, "PtoVta": 1, "CbteTipo": 6},
            "FeDetReq": {
                "FECAEDetRequest": [
                    {
                        "Concepto": 1,
                        "DocTipo": 80,
                        "DocNro": 20304050607,
                        "CbteDesde": 1,
                        "CbteHasta": 1,
                        "CbteFch": "20260305",
                        "ImpTotal": 1210.0,
                        "ImpTotConc": 0,
                        "ImpNeto": 1000.0,
                        "ImpOpEx": 0,
                        "ImpTrib": 0,
                        "ImpIVA": 210.0,
                        "MonId": "PES",
                        "MonCotiz": 1,
                        "CondicionIVAReceptorId": 5,
                        "Iva": {
                            "AlicIva": [{"Id": 5, "BaseImp": 1000.0, "Importe": 210.0}]
                        },
                    }
                ]
            },
        },
    }
    response = await client.post("/wsfe/FECAESolicitar", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_fe_comp_ultimo_autorizado_invalid_payload_returns_422(
    override_auth, client
):
    """FECompUltimoAutorizado with empty payload should return 422."""
    response = await client.post("/wsfe/FECompUltimoAutorizado", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_fecae_solicitar_without_auth_returns_403(client):
    """Request without Bearer token should be rejected."""
    # Don't use override_auth — real auth should reject
    response = await client.post(
        "/wsfe/FECAESolicitar",
        json={},
    )
    # FastAPI HTTPBearer returns 403 when no credentials provided
    assert response.status_code == 403
