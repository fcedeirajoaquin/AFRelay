import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from service.controllers.request_access_token_controller import \
    generate_afip_access_token
from service.utils.jwt_validator import verify_token
from service.utils.logger import logger
from service.xml_management.xml_builder import xml_exists

router = APIRouter()

CERTS_BASE = Path("service/app_certs")
XML_BASE = Path("service/xml_management/app_xml_files")


def _validate_cuit(cuit: str) -> None:
    if not cuit.isdigit() or len(cuit) != 11:
        raise HTTPException(status_code=400, detail="CUIT must be an 11-digit number")


@router.post("/tenants/{cuit}/certs")
async def upload_certs(
    cuit: str,
    private_key: UploadFile = File(...),
    certificate: UploadFile = File(...),
    jwt=Depends(verify_token),
) -> dict:
    """Upload AFIP certificates for a tenant and generate initial token."""
    _validate_cuit(cuit)

    certs_dir = CERTS_BASE / cuit
    xml_dir = XML_BASE / cuit

    os.makedirs(certs_dir, exist_ok=True)
    os.makedirs(xml_dir, exist_ok=True)

    key_path = certs_dir / "PrivateKey.key"
    cert_path = certs_dir / "returned_certificate.pem"

    key_content = await private_key.read()
    cert_content = await certificate.read()

    with open(key_path, "wb") as f:
        f.write(key_content)
    with open(cert_path, "wb") as f:
        f.write(cert_content)

    logger.info(f"Certificates uploaded for CUIT {cuit}")

    try:
        result = await generate_afip_access_token(cuit)
        token_status = result.get("status", "unknown")
    except Exception as e:
        logger.error(f"Failed to generate initial token for CUIT {cuit}: {e}")
        token_status = "error"

    return {
        "status": "ok",
        "cuit": cuit,
        "certs_uploaded": True,
        "initial_token": token_status,
    }


@router.get("/tenants/{cuit}/status")
async def get_tenant_status(cuit: str, jwt=Depends(verify_token)) -> dict:
    """Get the status of a tenant's AFIP configuration."""
    _validate_cuit(cuit)

    certs_dir = CERTS_BASE / cuit
    has_key = (certs_dir / "PrivateKey.key").exists()
    has_cert = (certs_dir / "returned_certificate.pem").exists()
    has_token = xml_exists("loginTicketResponse.xml", cuit)

    return {
        "cuit": cuit,
        "certs_uploaded": has_key and has_cert,
        "has_private_key": has_key,
        "has_certificate": has_cert,
        "token_valid": has_token,
    }


@router.delete("/tenants/{cuit}")
async def delete_tenant(cuit: str, jwt=Depends(verify_token)) -> dict:
    """Delete a tenant's certificates and tokens."""
    _validate_cuit(cuit)

    certs_dir = CERTS_BASE / cuit
    xml_dir = XML_BASE / cuit

    if certs_dir.exists():
        shutil.rmtree(certs_dir)
    if xml_dir.exists():
        shutil.rmtree(xml_dir)

    logger.info(f"Tenant {cuit} deleted")

    return {"status": "deleted", "cuit": cuit}


@router.get("/tenants")
async def list_tenants(jwt=Depends(verify_token)) -> dict:
    """List all registered tenants."""
    tenants = []

    if CERTS_BASE.exists():
        for cuit_dir in sorted(CERTS_BASE.iterdir()):
            if not cuit_dir.is_dir():
                continue
            cuit = cuit_dir.name
            has_key = (cuit_dir / "PrivateKey.key").exists()
            has_cert = (cuit_dir / "returned_certificate.pem").exists()
            has_token = xml_exists("loginTicketResponse.xml", cuit)
            tenants.append({
                "cuit": cuit,
                "certs_uploaded": has_key and has_cert,
                "token_valid": has_token,
            })

    return {"tenants": tenants}
