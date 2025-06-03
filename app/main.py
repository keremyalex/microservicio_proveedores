from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .graphql import schema
from .database import engine, Base
import uvicorn
from dotenv import load_dotenv
import os

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(title="Microservicio de Proveedores")

# Configurar el router de GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Microservicio de Proveedores y Abastecimiento"}

if __name__ == "__main__":
    load_dotenv()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8003))
    uvicorn.run("app.main:app", host=host, port=port, reload=True) 