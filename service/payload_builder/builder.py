from service.utils.logger import logger
from service.xml_management.xml_builder import extract_token_and_sign_from_xml


# Used in:
    # api.wsfe.fecae_solicitar
    # api.wsfe.fecaea_reg_informativo
def add_auth_to_payload(sale_data: dict, token: str, sign: str) -> dict:

    sale_data['Auth']['Token'] = token
    sale_data['Auth']['Sign'] = sign
    logger.debug("Auth added to payload.")

    return sale_data