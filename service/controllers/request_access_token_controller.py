from config.paths import get_as_bytes
from service.crypto.sign import sign_login_ticket_request
from service.soap_client.async_client import wsaa_client
from service.soap_client.wsaa import consult_afip_wsaa
from service.soap_client.wsdl.wsdl_manager import get_wsaa_wsdl
from service.time.time_management import generate_ntp_timestamp
from service.utils.logger import logger
from service.xml_management.xml_builder import (
    build_login_ticket_request, parse_and_save_loginticketresponse, save_xml)


async def generate_afip_access_token(cuit: str) -> dict:

    logger.info(f"Generating a new access token for CUIT {cuit}...")

    root = build_login_ticket_request(generate_ntp_timestamp)
    save_xml(root, "loginTicketRequest.xml", cuit)
    login_ticket_request_bytes, private_key_bytes, certificate_bytes = get_as_bytes(cuit)
    b64_cms = sign_login_ticket_request(login_ticket_request_bytes, private_key_bytes, certificate_bytes)

    afip_wsdl = get_wsaa_wsdl()
    client, httpx_client = wsaa_client(afip_wsdl)

    async def login_cms():
        try:
            return await client.service.loginCms(b64_cms)

        finally:
            if client and client.transport:
                await client.transport.aclose()
            else:
                await httpx_client.aclose()

    login_ticket_response = await consult_afip_wsaa(login_cms, "loginCms")

    if login_ticket_response["status"] == "success":
        parse_and_save_loginticketresponse(login_ticket_response["response"], save_xml, cuit)

        logger.info(f"Token generated successfully for CUIT {cuit}.")
        return {
            "status" : "success"
            }

    else:
        logger.error(f"Failed to generate access token for CUIT {cuit}.")
        return {
            "status" : "error generating access token."
            }
