import logging
from builtins import ConnectionResetError

import httpx
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)
from zeep.exceptions import Fault, TransportError, XMLSyntaxError

from service.soap_client.format_error import build_error_response
from service.utils.logger import logger


@retry(
        retry=retry_if_exception_type(( ConnectionResetError, httpx.ConnectError, TransportError )),
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
async def consult_afip_wsaa(make_request, METHOD) -> dict:

    logger.info("Starting CMS login request to AFIP")

    try:
        login_ticket_response = await make_request()
        logger.info("CMS login request to AFIP ended successfully.")

        return {
                "status" : "success",
                "response" : login_ticket_response
                }
    
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return build_error_response(METHOD, "Network error", str(e))
    
    except TransportError as e:
        return build_error_response(METHOD, "HTTP Error", str(e))

    except Fault as e:
        # SOAP Faults indicate that the request could not be processed by the service, 
        # often due to invalid input, datatype mismatches, or business rule violations. 
        # These errors are the caller's responsibility to handle.

        logger.debug(f"SOAP FAULT in {METHOD}: {e}")
        return build_error_response(METHOD, "SOAPFault", str(e))
    
    except XMLSyntaxError as e:
        return build_error_response(METHOD, "Invalid AFIP response", str(e))

    except Exception as e:
        logger.error(f"General exception in {METHOD}: {e}")
        return build_error_response(METHOD, "unknown", str(e))