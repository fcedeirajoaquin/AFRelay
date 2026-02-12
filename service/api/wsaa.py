from fastapi import APIRouter, Depends

from service.controllers.request_access_token_controller import \
    generate_afip_access_token
from service.utils.jwt_validator import verify_token
from service.utils.logger import logger

router = APIRouter()

@router.post("/wsaa/loginCms/{cuit}")
async def renew_access_token(cuit: str, jwt = Depends(verify_token)) -> dict:

    logger.info(f"Received request to renew access token for CUIT {cuit}")

    response_status = await generate_afip_access_token(cuit)

    return response_status
