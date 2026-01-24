from service.crypto.sign import sign_login_ticket_request

from ..conftest import generate_test_files


def test_sign_login_ticket_request():

    login_ticket_request_bytes, private_key_bytes, certificate_bytes = generate_test_files()
    b64_cms = sign_login_ticket_request(login_ticket_request_bytes, private_key_bytes, certificate_bytes)

    assert len(b64_cms) > 0
