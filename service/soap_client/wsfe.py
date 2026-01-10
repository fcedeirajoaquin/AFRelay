import logging
from builtins import ConnectionResetError

import httpx
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)
from zeep.exceptions import Fault, TransportError, XMLSyntaxError
from zeep.helpers import serialize_object

from service.soap_client.async_client import WSFEClientManager
from service.soap_client.format_error import build_error_response
from service.soap_client.wsdl.wsdl_manager import get_wsfe_wsdl
from service.utils.logger import logger

afip_wsdl = get_wsfe_wsdl()


@retry(
        retry=retry_if_exception_type(( ConnectionResetError, httpx.ConnectError, TransportError )),
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
async def fecae_solicitar(full_built_invoice: dict) -> dict:

    logger.info(f"Generating invoice...")
    METHOD = "FECAESolicitar"
    manager = WSFEClientManager(afip_wsdl)
    client = manager.get_client()

    try:
        invoice_result = await client.service.FECAESolicitar(full_built_invoice['Auth'], full_built_invoice['FeCAEReq'])

        # Zeep returns an object of type '<class 'zeep.objects.[service response]'>'.
        # To work with the returned data, this object needs to be converted into a dictionary using serialize_object().
        invoice_result = serialize_object(invoice_result)

        return {
                "status" : "success",
                "response" : invoice_result
                }
    
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return build_error_response(METHOD, "Network error", str(e))
    
    except TransportError as e:
        return build_error_response(METHOD, "HTTP Error", str(e))

    except Fault as e:
        # SOAP Faults here are not caused by user input.
        # Zeep owns the XML generation, so any structural or datatype issue leading to a
        # SOAP Fault originates from Zeep or the remote service, not from this layer.
        
        logger.debug(f"SOAP FAULT in fecae_solicitar: {e}")
        return build_error_response(METHOD, "SOAPFault", str(e))
    
    except XMLSyntaxError as e:
        return build_error_response(METHOD, "Invalid AFIP response", str(e))

    except Exception as e:
        logger.error(f"General exception in fecae_solicitar: {e}")
        return build_error_response(METHOD, "unknown", str(e))


@retry(
        retry=retry_if_exception_type(( ConnectionResetError, httpx.ConnectError, TransportError )),
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
async def fe_comp_ultimo_autorizado(auth: dict, ptovta: int, cbtetipo: int) -> dict:
    
    logger.info(f"Consulting last authorized invoice...")
    METHOD = "FECompUltimoAutorizado"
    manager = WSFEClientManager(afip_wsdl)
    client = manager.get_client()

    try:
        last_authorized_invoice = await client.service.FECompUltimoAutorizado(auth, ptovta, cbtetipo)
        logger.debug(f"Response: {last_authorized_invoice}")

        # Zeep returns an object of type '<class 'zeep.objects.[service response]'>'.
        # To work with the returned data, this object needs to be converted into a dictionary using serialize_object().
        last_authorized_invoice = serialize_object(last_authorized_invoice)

        return {
                "status" : "success",
                "response" : last_authorized_invoice
                }
    
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return build_error_response(METHOD, "Network error", str(e))
    
    except TransportError as e:
        return build_error_response(METHOD, "HTTP Error", str(e))

    except Fault as e:
        # SOAP Faults here are not caused by user input.
        # Zeep owns the XML generation, so any structural or datatype issue leading to a
        # SOAP Fault originates from Zeep or the remote service, not from this layer.
        
        logger.debug(f"SOAP FAULT in fe_comp_ultimo_autorizado: {e}")
        return build_error_response(METHOD, "SOAPFault", str(e))
    
    except XMLSyntaxError as e:
        return build_error_response(METHOD, "Invalid AFIP response", str(e))

    except Exception as e:
        logger.error(f"General exception in fe_comp_ultimo_autorizado: {e}")
        return build_error_response(METHOD, "unknown", str(e))
    

@retry(
        retry=retry_if_exception_type(( ConnectionResetError, httpx.ConnectError, TransportError )),
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
async def fe_comp_consultar(auth: dict, fecomp_req: dict) -> dict:
        
    METHOD = "FECompConsultar"
    manager = WSFEClientManager(afip_wsdl)
    client = manager.get_client()

    try:
        invoice_info = await client.service.FECompConsultar(auth, fecomp_req)
        logger.debug(f"Response: {invoice_info}")

        # Zeep returns an object of type '<class 'zeep.objects.[service response]'>'.
        # To work with the returned data, this object needs to be converted into a dictionary using serialize_object().
        invoice_info = serialize_object(invoice_info)

        return {
                "status" : "success",
                "response" : invoice_info
                }
    
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return build_error_response(METHOD, "Network error", str(e))
    
    except TransportError as e:
        return build_error_response(METHOD, "HTTP Error", str(e))

    except Fault as e:
        # SOAP Faults here are not caused by user input.
        # Zeep owns the XML generation, so any structural or datatype issue leading to a
        # SOAP Fault originates from Zeep or the remote service, not from this layer.
        
        logger.debug(f"SOAP FAULT in fe_comp_consultar: {e}")
        return build_error_response(METHOD, "SOAPFault", str(e))
    
    except XMLSyntaxError as e:
        return build_error_response(METHOD, "Invalid AFIP response", str(e))

    except Exception as e:
        logger.error(f"General exception in fe_comp_consultar: {e}")
        return build_error_response(METHOD, "unknown", str(e))


# ===================
# == HEALTH CHECK ===
# ===================

async def wsfe_dummy():
    """
    WSFE health cheack
    """
    logger.info(f"Consulting WSFE dummy method (health check)...")
    manager = WSFEClientManager(afip_wsdl)
    client = manager.get_client()
    try:
        health_info = await client.service.FEDummy()
        return health_info

    except Exception as e:
        logger.error(f"General exception in wsfe_dummy: {e}")
        return health_info