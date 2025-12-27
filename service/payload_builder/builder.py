from service.utils.logger import logger


# Used in controllers.request_invoice_controller.py
def add_auth_to_payload(sale_data: dict, token: str, sign: str) -> dict:

    sale_data['Auth']['Token'] = token
    sale_data['Auth']['Sign'] = sign
    logger.debug("Auth added to payload.")

    return sale_data

def build_auth(token: str, sign: str, cuit: int) -> dict:

    auth = {
        "Token" : token,
        "Sign" : sign,
        "Cuit" : cuit,
    }

    return auth