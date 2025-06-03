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
        return db.query(ProveedorModel).all()

    @strawberry.field
    def compra(self, info, id: int) -> Optional[Compra]:
        db = next(get_db())
        compra = db.query(CompraModel).filter(CompraModel.id == id).first()
        if not compra:
            raise HTTPException(
                status_code=404,
                detail=f"Error: No se encontró la compra con ID {id}"
            )
        return compra

    @strawberry.field
    def compras(self, info) -> List[Compra]:
        db = next(get_db())
        compras = db.query(CompraModel).all()
        if not compras:
            raise HTTPException(
                status_code=404,
                detail="Error: No hay compras registradas en el sistema"
            )
        return compras

@strawberry.type
class Mutation:
    @strawberry.mutation
    def crear_proveedor(self, info, input: ProveedorInput) -> Proveedor:
        db = next(get_db())
        try:
            if not input.nombre:
                raise Exception("El nombre del proveedor es requerido")
            if not input.nit:
                raise Exception("El NIT del proveedor es requerido")
            
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
            return proveedor
        except IntegrityError:
            db.rollback()
            raise Exception(f"Ya existe un proveedor registrado con el NIT {input.nit}")
        except Exception as e:
            db.rollback()
            raise Exception(str(e))

    @strawberry.mutation
    def actualizar_proveedor(self, info, id: int, input: ProveedorUpdateInput) -> Proveedor:
        db = next(get_db())
        try:
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == id).first()
            if not proveedor:
                raise Exception(f"No se encontró el proveedor con ID {id}")
            
            if all(v is None for v in [input.nombre, input.direccion, input.telefono, input.email]):
                raise Exception("Debe proporcionar al menos un campo para actualizar")
            
            if input.nombre is not None:
                if not input.nombre.strip():
                    raise Exception("El nombre no puede estar vacío")
                proveedor.nombre = input.nombre
            if input.direccion is not None:
                proveedor.direccion = input.direccion
            if input.telefono is not None:
                proveedor.telefono = input.telefono
            if input.email is not None:
                proveedor.email = input.email
            
            db.commit()
            db.refresh(proveedor)
            return proveedor
        except Exception as e:
            db.rollback()
            raise Exception(str(e))

    @strawberry.mutation
    def eliminar_proveedor(self, info, id: int) -> bool:
        db = next(get_db())
        try:
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == id).first()
            if not proveedor:
                raise Exception(f"No se encontró el proveedor con ID {id}")
            
            if proveedor.compras:
                raise Exception("No se puede eliminar el proveedor porque tiene compras asociadas. Elimine primero las compras.")
            
            db.delete(proveedor)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(str(e))

    @strawberry.mutation
    def crear_compra(self, info, input: CompraInput) -> Compra:
        db = next(get_db())
        try:
            # Verificar que el proveedor existe
            proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == input.proveedorId).first()
            if not proveedor:
                raise Exception(f"No existe un proveedor con ID {input.proveedorId}")

            # Validar que hay detalles en la compra
            if not input.detalles:
                raise Exception("La compra debe tener al menos un detalle")

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
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error: La cantidad en el detalle {i} debe ser mayor a 0"
                    )
                if detalle.precioUnitario <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error: El precio unitario en el detalle {i} debe ser mayor a 0"
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
            return compra
        except HTTPException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    @strawberry.mutation
    def actualizar_compra(self, info, id: int, input: CompraUpdateInput) -> Compra:
        db = next(get_db())
        try:
            compra = db.query(CompraModel).filter(CompraModel.id == id).first()
            if not compra:
                raise HTTPException(
                    status_code=404,
                    detail=f"Error: No se encontró la compra con ID {id}"
                )
            
            # Validar el estado
            estados_validos = ["pendiente", "completada", "cancelada"]
            if input.estado not in estados_validos:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error: Estado no válido. Los estados permitidos son: {', '.join(estados_validos)}"
                )
            
            compra.estado = input.estado
            db.commit()
            db.refresh(compra)
            return compra
        except HTTPException as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    @strawberry.mutation
    def eliminar_compra(self, info, id: int) -> bool:
        db = next(get_db())
        try:
            compra = db.query(CompraModel).filter(CompraModel.id == id).first()
            if not compra:
                raise HTTPException(
                    status_code=404,
                    detail=f"Error: No se encontró la compra con ID {id}"
                )
            
            # Eliminar primero los detalles de la compra
            for detalle in compra.detalles:
                db.delete(detalle)
            
            db.delete(compra)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True
) 