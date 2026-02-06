from pydantic import BaseModel


class InvoiceBaseQuery(BaseModel):
    Cuit: int
    PtoVta: int
    CbteTipo: int

class FECompConsultar(InvoiceBaseQuery):
    CbteNro: int

class FECompUltimoAutorizado(InvoiceBaseQuery):
    pass
