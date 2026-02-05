from service.utils.logger import logger
from service.xml_management.xml_builder import extract_token_and_sign_from_xml


# Used in api.wsfe.generate_invoice
def add_auth_to_payload(sale_data: dict, token: str, sign: str) -> dict:

    sale_data['Auth']['Token'] = token
    sale_data['Auth']['Sign'] = sign
    logger.debug("Auth added to payload.")

    return sale_data

def build_auth(sale_data: dict) -> dict:
    token, sign = extract_token_and_sign_from_xml()
    cuit = sale_data["Cuit"]

    return {
        "Token" : token,
        "Sign" : sign,
        "Cuit" : cuit,
    }

def build_fecomp_req(comp_info: dict) -> dict:

    return {
        'PtoVta': comp_info["PtoVta"],
        'CbteTipo': comp_info["CbteTipo"],
        'CbteNro': comp_info["CbteNro"],
    }