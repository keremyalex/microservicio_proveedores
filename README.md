# Microservicio de Proveedores y Abastecimiento

Este microservicio forma parte de un sistema distribuido y se encarga de la gestión de proveedores y compras. Está construido con FastAPI, GraphQL (Strawberry) y MySQL.

## Requisitos

- Python 3.8+
- MySQL
- pip (gestor de paquetes de Python)

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Crear archivo .env con la siguiente configuración:
```
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/proveedores_db
HOST=0.0.0.0
PORT=8003
```

4. Crear la base de datos en MySQL:
```sql
CREATE DATABASE proveedores_db;
```

## Ejecución

Para ejecutar el servidor:

```bash
python -m app.main
```

El servidor estará disponible en:
- API REST: http://localhost:8003
- GraphQL Playground: http://localhost:8003/graphql

## Ejemplos de Queries GraphQL

### Consultar todos los proveedores:
```graphql
query {
  proveedores {
    id
    nombre
    nit
    direccion
    telefono
    email
  }
}
```

### Consultar un proveedor específico:
```graphql
query {
  proveedor(id: 1) {
    id
    nombre
    nit
    direccion
    telefono
    email
  }
}
```

### Crear un nuevo proveedor:
```graphql
mutation {
  crearProveedor(
    input: {
      nombre: "Proveedor Test"
      nit: "901234567"
      direccion: "Av. Test 123"
      telefono: "123456789"
      email: "test@proveedor.com"
    }
  ) {
    id
    nombre
    nit
  }
}
```

### Actualizar un proveedor:
```graphql
mutation {
  actualizarProveedor(
    id: 1,
    input: {
      nombre: "Proveedor Test Actualizado"
      direccion: "Nueva Dirección 456"
      telefono: "987654321"
      email: "nuevo@proveedor.com"
    }
  ) {
    id
    nombre
    nit
    direccion
    telefono
    email
  }
}
```

### Eliminar un proveedor:
```graphql
mutation {
  eliminarProveedor(id: 1)
}
```

### Crear una nueva compra:
```graphql
mutation {
  crearCompra(
    input: {
      proveedor_id: 1
      detalles: [
        {
          producto_id: 1
          cantidad: 10
          precio_unitario: 100.0
        }
      ]
    }
  ) {
    id
    total
    estado
    detalles {
      producto_id
      cantidad
      subtotal
    }
  }
}
```

### Actualizar estado de una compra:
```graphql
mutation {
  actualizarCompra(
    id: 1,
    input: {
      estado: "completada"
    }
  ) {
    id
    estado
    total
  }
}
```

### Eliminar una compra:
```graphql
mutation {
  eliminarCompra(id: 1)
}
```

### Consultar todas las compras:
```graphql
query {
  compras {
    id
    proveedor_id
    fecha_compra
    total
    estado
    detalles {
      producto_id
      cantidad
      precio_unitario
      subtotal
    }
  }
}
```

### Consultar una compra específica:
```graphql
query {
  compra(id: 1) {
    id
    proveedor_id
    fecha_compra
    total
    estado
    detalles {
      producto_id
      cantidad
      precio_unitario
      subtotal
    }
  }
}
```

## Ejemplos de Queries y Errores Comunes

### 1. Operaciones con Proveedores

#### Crear Proveedor
```graphql
mutation {
  crearProveedor(
    input: {
      nombre: "Distribuidora ABC"
      nit: "123456789"
      direccion: "Calle 123 #45-67"
      telefono: "3001234567"
      email: "contacto@abc.com"
    }
  ) {
    proveedor {
      id
      nombre
      nit
    }
    error {
      message
      code
    }
  }
}
```

**Posibles respuestas de error**:
```json
{
  "data": {
    "crearProveedor": {
      "proveedor": null,
      "error": {
        "message": "Ya existe un proveedor registrado con el NIT 123456789",
        "code": "DUPLICATE_NIT"
      }
    }
  }
}
```

#### Consultar Proveedores
```graphql
query {
  proveedores {
    id
    nombre
    nit
    direccion
    telefono
    email
  }
}
```

**Posibles errores**:
- No hay proveedores: "Error: No hay proveedores registrados en el sistema"

#### Actualizar Proveedor
```graphql
mutation {
  actualizarProveedor(
    id: 1,
    input: {
      direccion: "Nueva Dirección 456"
      telefono: "3009876543"
      email: "nuevo@abc.com"
    }
  ) {
    proveedor {
      id
      nombre
      nit
      direccion
      telefono
      email
    }
    error {
      message
      code
    }
  }
}
```

**Posibles errores**:
- Proveedor no existe: "Error: No se encontró el proveedor con ID 1"
- Sin campos para actualizar: "Error: Debe proporcionar al menos un campo para actualizar"
- Nombre vacío: "Error de validación: El nombre no puede estar vacío"

### 2. Operaciones con Compras

#### Crear Compra
```graphql
mutation {
  crearCompra(
    input: {
      proveedorId: 1
      detalles: [
        {
          productoId: 1
          cantidad: 5
          precioUnitario: 100000
        }
      ]
    }
  ) {
    id
    proveedorId
    fechaCompra
    total
    estado
    detalles {
      productoId
      cantidad
      precioUnitario
      subtotal
    }
  }
}
```

**Posibles errores**:
- Proveedor no existe: "Error: No existe un proveedor con ID 1"
- Sin detalles: "Error: La compra debe tener al menos un detalle"
- Cantidad inválida: "Error: La cantidad en el detalle 1 debe ser mayor a 0"
- Precio inválido: "Error: El precio unitario en el detalle 1 debe ser mayor a 0"

#### Actualizar Estado de Compra
```graphql
mutation {
  actualizarCompra(
    id: 1,
    input: {
      estado: "completada"
    }
  ) {
    id
    estado
    total
  }
}
```

**Posibles errores**:
- Compra no existe: "Error: No se encontró la compra con ID 1"
- Estado inválido: "Error: Estado no válido. Los estados permitidos son: pendiente, completada, cancelada"

#### Eliminar Compra
```graphql
mutation {
  eliminarCompra(id: 1)
}
```

**Posibles errores**:
- Compra no existe: "Error: No se encontró la compra con ID 1"

#### Eliminar Proveedor
```graphql
mutation {
  eliminarProveedor(id: 1) {
    success
    error {
      message
      code
    }
  }
}
```

**Posibles errores**:
- Proveedor no existe: "Error: No se encontró el proveedor con ID 1"
- Tiene compras asociadas: "Error: No se puede eliminar el proveedor porque tiene compras asociadas. Elimine primero las compras."

## Flujo de Pruebas Recomendado

1. Crear varios proveedores
2. Intentar crear un proveedor con NIT duplicado (debe fallar)
3. Consultar todos los proveedores
4. Actualizar datos de un proveedor
5. Crear compras para diferentes proveedores
6. Actualizar estados de las compras
7. Intentar eliminar un proveedor con compras (debe fallar)
8. Eliminar una compra
9. Eliminar el proveedor (ahora sí debe funcionar)

## Validaciones implementadas

El microservicio incluye las siguientes validaciones:

### Para Proveedores:
- NIT único (no se permiten duplicados)
- No se puede eliminar un proveedor con compras asociadas
- Campos requeridos: nombre, NIT

### Para Compras:
- El proveedor debe existir
- Debe tener al menos un detalle
- Cantidades y precios deben ser mayores a 0
- Estados válidos: "pendiente", "completada", "cancelada"
- Al eliminar una compra, se eliminan automáticamente sus detalles

## Integración con Gateway NestJS

Este microservicio está configurado como un subgraph de GraphQL Federation v2, lo que permite su integración con un gateway NestJS. Para integrarlo:

1. Asegúrate de que el gateway NestJS tenga configurado Apollo Federation:

```typescript
// gateway/src/app.module.ts
import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloGatewayDriver, ApolloGatewayDriverConfig } from '@nestjs/apollo';
import { IntrospectAndCompose } from '@apollo/gateway';

@Module({
  imports: [
    GraphQLModule.forRoot<ApolloGatewayDriverConfig>({
      driver: ApolloGatewayDriver,
      gateway: {
        supergraphSdl: new IntrospectAndCompose({
          subgraphs: [
            // ... otros subgraphs ...
            {
              name: 'proveedores',
              url: 'http://localhost:8003/graphql',
            },
          ],
        }),
      },
    }),
  ],
})
export class AppModule {}
```

2. Asegúrate de que el microservicio esté ejecutándose antes de iniciar el gateway.

3. Los tipos federados disponibles son:
   - `Proveedor`: Identificado por el campo `id`
   - Las relaciones con otros microservicios se pueden establecer usando las referencias de Federation.

## Manejo de Errores

El microservicio incluye validaciones para:
- NIT duplicado en proveedores
- Proveedor no encontrado
- Cantidades y precios negativos o cero
- Compras sin detalles
- Errores generales de base de datos

Los errores retornan códigos HTTP apropiados y mensajes descriptivos.

## Códigos de Error

El sistema utiliza los siguientes códigos de error:

- `NOT_FOUND`: El recurso solicitado no existe
- `VALIDATION_ERROR`: Error en los datos proporcionados
- `DUPLICATE_NIT`: Intento de crear un proveedor con un NIT que ya existe
- `HAS_RELATED_PURCHASES`: No se puede eliminar un proveedor que tiene compras asociadas
- `INTERNAL_ERROR`: Error interno del servidor 