from typing import List, Optional, Union
import strawberry
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import timezone
from strawberry.federation import Schema
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from .database import get_db
from .models import Proveedor as ProveedorModel
from .models import Compra as CompraModel
from .models import DetalleCompra as DetalleCompraModel
from .schemas import (
    Proveedor, ProveedorInput, ProveedorUpdateInput,
    Compra, CompraInput, CompraUpdateInput,
    DetalleCompra
)

@strawberry.type
class Error:
    message: str
    code: str

@strawberry.type
class ProveedorResponse:
    proveedor: Optional[Proveedor] = None
    error: Optional[Error] = None

@strawberry.type
class CompraResponse:
    compra: Optional[Compra] = None
    error: Optional[Error] = None

@strawberry.type
class DeleteResponse:
    success: bool
    error: Optional[Error] = None

@strawberry.type
class Query:
    @strawberry.field
    def proveedor(self, info, id: int) -> ProveedorResponse:
        db = next(get_db())
        try:
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == id).first()
            if not proveedor:
                return ProveedorResponse(
                    error=Error(
                        message=f"No se encontró el proveedor con ID {id}",
                        code="NOT_FOUND"
                    )
                )
            return ProveedorResponse(proveedor=proveedor)
        except Exception as e:
            return ProveedorResponse(
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.field
    def proveedores(self, info) -> List[Proveedor]:
        db = next(get_db())
        try:
            return db.query(ProveedorModel).all()
        except Exception as e:
            raise Exception(f"Error al obtener proveedores: {str(e)}")

    @strawberry.field
    def compra(self, info, id: int) -> CompraResponse:
        db = next(get_db())
        try:
            compra = db.query(CompraModel).filter(CompraModel.id == id).first()
            if not compra:
                return CompraResponse(
                    error=Error(
                        message=f"No se encontró la compra con ID {id}",
                        code="NOT_FOUND"
                    )
                )
            return CompraResponse(compra=compra)
        except Exception as e:
            return CompraResponse(
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.field
    def compras(self, info) -> List[Compra]:
        db = next(get_db())
        try:
            compras = db.query(CompraModel).all()
            if not compras:
                return []
            return compras
        except Exception as e:
            raise Exception(f"Error al obtener compras: {str(e)}")

@strawberry.type
class Mutation:
    @strawberry.mutation
    def crear_proveedor(self, info, input: ProveedorInput) -> ProveedorResponse:
        db = next(get_db())
        try:
            if not input.nombre:
                return ProveedorResponse(
                    error=Error(
                        message="El nombre del proveedor es requerido",
                        code="VALIDATION_ERROR"
                    )
                )
            if not input.nit:
                return ProveedorResponse(
                    error=Error(
                        message="El NIT del proveedor es requerido",
                        code="VALIDATION_ERROR"
                    )
                )
            
            proveedor = ProveedorModel(
                nombre=input.nombre,
                nit=input.nit,
                direccion=input.direccion,
                telefono=input.telefono,
                email=input.email
            )
            db.add(proveedor)
            db.commit()
            db.refresh(proveedor)
            return ProveedorResponse(proveedor=proveedor)
        except IntegrityError:
            db.rollback()
            return ProveedorResponse(
                error=Error(
                    message=f"Ya existe un proveedor registrado con el NIT {input.nit}",
                    code="DUPLICATE_ERROR"
                )
            )
        except Exception as e:
            db.rollback()
            return ProveedorResponse(
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.mutation
    def actualizar_proveedor(self, info, id: int, input: ProveedorUpdateInput) -> ProveedorResponse:
        db = next(get_db())
        try:
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == id).first()
            if not proveedor:
                return ProveedorResponse(
                    error=Error(
                        message=f"No se encontró el proveedor con ID {id}",
                        code="NOT_FOUND"
                    )
                )
            
            if all(v is None for v in [input.nombre, input.direccion, input.telefono, input.email]):
                return ProveedorResponse(
                    error=Error(
                        message="Debe proporcionar al menos un campo para actualizar",
                        code="VALIDATION_ERROR"
                    )
                )
            
            if input.nombre is not None:
                if not input.nombre.strip():
                    return ProveedorResponse(
                        error=Error(
                            message="El nombre no puede estar vacío",
                            code="VALIDATION_ERROR"
                        )
                    )
                proveedor.nombre = input.nombre
            if input.direccion is not None:
                proveedor.direccion = input.direccion
            if input.telefono is not None:
                proveedor.telefono = input.telefono
            if input.email is not None:
                proveedor.email = input.email
            
            db.commit()
            db.refresh(proveedor)
            return ProveedorResponse(proveedor=proveedor)
        except Exception as e:
            db.rollback()
            return ProveedorResponse(
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.mutation
    def eliminar_proveedor(self, info, id: int) -> DeleteResponse:
        db = next(get_db())
        try:
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == id).first()
            if not proveedor:
                return DeleteResponse(
                    success=False,
                    error=Error(
                        message=f"No se encontró el proveedor con ID {id}",
                        code="NOT_FOUND"
                    )
                )
            
            if proveedor.compras:
                return DeleteResponse(
                    success=False,
                    error=Error(
                        message="No se puede eliminar el proveedor porque tiene compras asociadas. Elimine primero las compras.",
                        code="CONSTRAINT_ERROR"
                    )
                )
            
            db.delete(proveedor)
            db.commit()
            return DeleteResponse(success=True)
        except Exception as e:
            db.rollback()
            return DeleteResponse(
                success=False,
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.mutation
    def crear_compra(self, info, input: CompraInput) -> CompraResponse:
        db = next(get_db())
        try:
            # Verificar que el proveedor existe
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == input.proveedorId).first()
            if not proveedor:
                return CompraResponse(
                    error=Error(
                        message=f"No existe un proveedor con ID {input.proveedorId}",
                        code="NOT_FOUND"
                    )
                )

            # Validar que hay detalles en la compra
            if not input.detalles:
                return CompraResponse(
                    error=Error(
                        message="La compra debe tener al menos un detalle",
                        code="VALIDATION_ERROR"
                    )
                )

            # Calcular el total de la compra
            total = sum(detalle.cantidad * detalle.precioUnitario for detalle in input.detalles)
            
            # Crear la compra
            compra = CompraModel(
                proveedorId=input.proveedorId,
                fechaCompra=datetime.now(timezone.utc),
                total=total,
                estado="pendiente"
            )
            db.add(compra)
            db.flush()
            
            # Crear los detalles de la compra
            for i, detalle in enumerate(input.detalles, 1):
                if detalle.cantidad <= 0:
                    return CompraResponse(
                        error=Error(
                            message=f"La cantidad en el detalle {i} debe ser mayor a 0",
                            code="VALIDATION_ERROR"
                        )
                    )
                if detalle.precioUnitario <= 0:
                    return CompraResponse(
                        error=Error(
                            message=f"El precio unitario en el detalle {i} debe ser mayor a 0",
                            code="VALIDATION_ERROR"
                        )
                    )
                
                detalle_compra = DetalleCompraModel(
                    compraId=compra.id,
                    productoId=detalle.productoId,
                    cantidad=detalle.cantidad,
                    precioUnitario=detalle.precioUnitario,
                    subtotal=detalle.cantidad * detalle.precioUnitario
                )
                db.add(detalle_compra)
            
            db.commit()
            db.refresh(compra)
            return CompraResponse(compra=compra)
        except Exception as e:
            db.rollback()
            return CompraResponse(
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.mutation
    def actualizar_compra(self, info, id: int, input: CompraUpdateInput) -> CompraResponse:
        db = next(get_db())
        try:
            compra = db.query(CompraModel).filter(CompraModel.id == id).first()
            if not compra:
                return CompraResponse(
                    error=Error(
                        message=f"No se encontró la compra con ID {id}",
                        code="NOT_FOUND"
                    )
                )
            
            # Validar el estado
            estados_validos = ["pendiente", "completada", "cancelada"]
            if input.estado not in estados_validos:
                return CompraResponse(
                    error=Error(
                        message=f"Estado no válido. Los estados permitidos son: {', '.join(estados_validos)}",
                        code="VALIDATION_ERROR"
                    )
                )
            
            compra.estado = input.estado
            db.commit()
            db.refresh(compra)
            return CompraResponse(compra=compra)
        except Exception as e:
            db.rollback()
            return CompraResponse(
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

    @strawberry.mutation
    def eliminar_compra(self, info, id: int) -> DeleteResponse:
        db = next(get_db())
        try:
            compra = db.query(CompraModel).filter(CompraModel.id == id).first()
            if not compra:
                return DeleteResponse(
                    success=False,
                    error=Error(
                        message=f"No se encontró la compra con ID {id}",
                        code="NOT_FOUND"
                    )
                )
            
            # Eliminar primero los detalles de la compra
            for detalle in compra.detalles:
                db.delete(detalle)
            
            db.delete(compra)
            db.commit()
            return DeleteResponse(success=True)
        except Exception as e:
            db.rollback()
            return DeleteResponse(
                success=False,
                error=Error(
                    message=str(e),
                    code="INTERNAL_ERROR"
                )
            )

schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True
)