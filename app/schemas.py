from typing import List, Optional
import strawberry
from datetime import datetime
from strawberry.federation import Schema
from strawberry.federation.schema_directives import Key
from .models import Proveedor as ProveedorModel
from .models import Compra as CompraModel
from .models import DetalleCompra as DetalleCompraModel

@strawberry.federation.type(keys=["id"])
class Proveedor:
    id: int
    nombre: str
    nit: str
    direccion: str
    telefono: str
    email: str

    @classmethod
    def resolve_reference(cls, id: int):
        # Implementar resolución de referencias para federation
        return cls(id=id)

@strawberry.input
class ProveedorInput:
    nombre: str
    nit: str
    direccion: str
    telefono: str
    email: str

@strawberry.input
class ProveedorUpdateInput:
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

@strawberry.type
class DetalleCompra:
    id: int
    productoId: int
    cantidad: int
    precioUnitario: float
    subtotal: float

@strawberry.input
class DetalleCompraInput:
    productoId: int
    cantidad: int
    precioUnitario: float

@strawberry.type
class Compra:
    id: int
    proveedorId: int
    fechaCompra: datetime
    total: float
    estado: str
    detalles: List[DetalleCompra]

@strawberry.input
class CompraInput:
    proveedorId: int
    detalles: List[DetalleCompraInput]

@strawberry.input
class CompraUpdateInput:
    estado: str 