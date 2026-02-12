from pathlib import Path


class AfipPaths:
    """
    Centralizes AFIP file paths using the Path Object pattern.
    Allows injection of different base directories for testing.
    """
    def __init__(self, base_xml: Path, base_crypto: Path, base_certs: Path) -> None:
        self.base_xml = base_xml
        self.base_crypto = base_crypto
        self.base_certs = base_certs

    @property
    def login_request(self) -> Path:
        return self.base_xml / "loginTicketRequest.xml"

    @property
    def login_response(self) -> Path:
        return self.base_xml / "loginTicketResponse.xml"

    @property
    def certificate(self) -> Path:
        return self.base_certs / "returned_certificate.pem"

    @property
    def private_key(self) -> Path:
        return self.base_certs / "PrivateKey.key"


def get_afip_paths(cuit: str) -> AfipPaths:
    return AfipPaths(
        base_xml = Path(f"service/xml_management/app_xml_files/{cuit}"),
        base_crypto = Path("service/crypto"),
        base_certs = Path(f"service/app_certs/{cuit}"),
    )

def get_as_bytes(cuit: str) -> tuple[bytes, bytes, bytes]:
    paths = get_afip_paths(cuit)

    with open(paths.login_request, 'rb') as file:
        login_ticket_request_bytes = file.read()

    with open(paths.private_key, 'rb') as file:
        private_key_bytes = file.read()

    with open(paths.certificate, 'rb') as file:
        certificate_bytes = file.read()

    return login_ticket_request_bytes, private_key_bytes, certificate_bytes
