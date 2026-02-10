from fastapi import APIRouter, Depends

from service.api.models.fe_comp_consultar import FECompConsultar
from service.api.models.fecae_solicitar import FECAESolicitar
from service.api.models.fecaea_reg_informativo import FECAEARegInformativo
from service.api.models.simple_models import (FECAEAConsultar,
                                              FECAEASinMovimientoConsultar,
                                              FECAEASinMovimientoInformar,
                                              FECAEASolicitar,
                                              FECompTotXRequest,
                                              FECompUltimoAutorizado,
                                              FEParamGetCotizacion)
from service.payload_builder.builder import add_auth_to_payload
from service.soap_client.async_client import WSFEClientManager
from service.soap_client.wsdl.wsdl_manager import get_wsfe_wsdl
from service.soap_client.wsfe import consult_afip_wsfe
from service.utils.jwt_validator import verify_token
from service.utils.logger import logger
from service.xml_management.xml_builder import extract_token_and_sign_from_xml

router = APIRouter()
afip_wsdl = get_wsfe_wsdl()


@router.post("/wsfe/FECAESolicitar")
async def fecae_solicitar(data: FECAESolicitar, jwt = Depends(verify_token)) -> dict:
    
    logger.info("Received request to generate invoice at /wsfe/FECAESolicitar")

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECAESolicitar(**data)

    result = await consult_afip_wsfe(make_request, "FECAESolicitar")
    return result


@router.post("/wsfe/FECompTotXRequest")
async def fecomp_totx_request(data: FECompTotXRequest, jwt = Depends(verify_token)) -> dict:

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECompTotXRequest(**data)
    
    result = await consult_afip_wsfe(make_request, "FECompTotXRequest")
    return result


@router.post("/wsfe/FECompUltimoAutorizado")
async def fe_comp_ultimo_autorizado(data: FECompUltimoAutorizado, jwt = Depends(verify_token)) -> dict:
    logger.info("Received request to generate invoice at /wsfe/FECompUltimoAutorizado")

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECompUltimoAutorizado(**data)

    result = await consult_afip_wsfe(make_request, "FECompUltimoAutorizado")
    return result


@router.post("/wsfe/FECompConsultar")
async def fe_comp_consultar(comp_info: FECompConsultar, jwt = Depends(verify_token)) -> dict:
    logger.info("Received request to query specific invoice at /wsfe/FECompConsultar")

    data = comp_info.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECompConsultar(**data)

    result = await consult_afip_wsfe(make_request, "FECompConsultar")
    return result


@router.post("/wsfe/FECAEARegInformativo")
async def fecaea_reg_informativo(data: FECAEARegInformativo, jwt = Depends(verify_token)) -> dict:
    
    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECAEARegInformativo(**data)

    result = await consult_afip_wsfe(make_request, "FECAEARegInformativo")
    return result


@router.post("/wsfe/FECAEASolicitar")
async def fecaea_solicitar(data: FECAEASolicitar, jwt = Depends(verify_token)) -> dict:

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECAEASolicitar(**data)
    
    result = await consult_afip_wsfe(make_request, "FECAEASolicitar")
    return result


@router.post("/wsfe/FECAEASinMovimientoConsultar")
async def fecaea_sin_movimiento_consultar(data: FECAEASinMovimientoConsultar, jwt = Depends(verify_token)) -> dict:

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECAEASinMovimientoConsultar(**data)
    
    result = await consult_afip_wsfe(make_request, "FECAEASinMovimientoConsultar")
    return result


@router.post("/wsfe/FECAEASinMovimientoInformar")
async def fecaea_sin_movimiento_informar(data: FECAEASinMovimientoInformar, jwt = Depends(verify_token)) -> dict:

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECAEASinMovimientoInformar(**data)
    
    result = await consult_afip_wsfe(make_request, "FECAEASinMovimientoInformar")
    return result


@router.post("/wsfe/FECAEAConsultar")
async def fecaea_consultar(data: FECAEAConsultar, jwt = Depends(verify_token)) -> dict:

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FECAEAConsultar(**data)
    
    result = await consult_afip_wsfe(make_request, "FECAEAConsultar")
    return result


@router.post("/wsfe/FEParamGetCotizacion")
async def fe_param_get_cotization(data: FEParamGetCotizacion, jwt = Depends(verify_token)) -> dict:

    data = data.model_dump(by_alias=True, exclude_none=True)
    token, sign = extract_token_and_sign_from_xml()
    data = add_auth_to_payload(data, token, sign)

    async def make_request():
        manager = WSFEClientManager(afip_wsdl)
        client = manager.get_client()
        return await client.service.FEParamGetCotizacion(**data)
    
    result = await consult_afip_wsfe(make_request, "FEParamGetCotizacion")
    return result