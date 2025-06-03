from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

class Proveedor(Base):
    __tablename__ = "proveedores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    nit = Column(String(20), unique=True, nullable=False)
    direccion = Column(String(200))
    telefono = Column(String(20))
    email = Column(String(100))
    compras = relationship("Compra", back_populates="proveedor")

class Compra(Base):
    __tablename__ = "compras"
    
    id = Column(Integer, primary_key=True, index=True)
    proveedorId = Column("proveedor_id", Integer, ForeignKey("proveedores.id"))
    fechaCompra = Column("fecha_compra", DateTime, default=lambda: datetime.now(timezone.utc))
    total = Column(Float, nullable=False)
    estado = Column(String(20), default="pendiente")
    
    proveedor = relationship("Proveedor", back_populates="compras")
    detalles = relationship("DetalleCompra", back_populates="compra")

class DetalleCompra(Base):
    __tablename__ = "detalles_compra"
    
    id = Column(Integer, primary_key=True, index=True)
    compraId = Column("compra_id", Integer, ForeignKey("compras.id"))
    productoId = Column("producto_id", Integer)  # Referencia al microservicio de inventario
    cantidad = Column(Integer, nullable=False)
    precioUnitario = Column("precio_unitario", Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    compra = relationship("Compra", back_populates="detalles") 