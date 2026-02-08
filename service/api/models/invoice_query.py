from pydantic import BaseModel


class InvoiceBaseQuery(BaseModel):
    Cuit: int

class FECompTotXRequest(InvoiceBaseQuery):
    pass

class FECompUltimoAutorizado(InvoiceBaseQuery):
    PtoVta: int
    CbteTipo: int

class FECompConsultar(InvoiceBaseQuery):
    PtoVta: int
    CbteTipo: int
    CbteNro: int

class FECAEAConsultar(InvoiceBaseQuery):
    Periodo: int
    Orden: int