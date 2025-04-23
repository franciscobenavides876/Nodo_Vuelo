from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from TDA_Vuelos import ListaVuelos, Vuelo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models import Base, VueloDB

# Configuración de SQLite
DATABASE_URL = "sqlite:///./vuelos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enum de estado de vuelo
class EstadoVuelo(str, Enum):
    programado = "Programado"
    emergencia = "Emergencia"
    retrasado = "Retrasado"

# Modelo de entrada para los vuelos (usado con FastAPI)
class VueloIn(BaseModel):
    codigo: str
    estado: EstadoVuelo
    hora: datetime
    origen: str
    destino: str

# Instancia global de la lista de vuelos
lista_vuelos = ListaVuelos()

# POST /vuelos - Añadir vuelo
@app.post("/vuelos")
def agregar_vuelo(vuelo: VueloIn):
    db = SessionLocal()
    try:
        vuelo_db = VueloDB(
            codigo=vuelo.codigo,
            estado=vuelo.estado,
            hora=vuelo.hora,
            origen=vuelo.origen,
            destino=vuelo.destino
        )
        db.add(vuelo_db)
        db.commit()
        db.refresh(vuelo_db)

        nuevo_vuelo = Vuelo(
            codigo=vuelo.codigo,
            estado=vuelo.estado,
            hora=vuelo.hora,
            origen=vuelo.origen,
            destino=vuelo.destino
        )
        if vuelo.estado == EstadoVuelo.emergencia:
            lista_vuelos.insertar_al_frente(nuevo_vuelo)
        else:
            lista_vuelos.insertar_al_final(nuevo_vuelo)

        return {"mensaje": "Vuelo añadido correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# GET /vuelos/total
@app.get("/vuelos/total")
def obtener_total():
    return {"total_vuelos": lista_vuelos.longitud()}

# GET /vuelos/proximo
@app.get("/vuelos/proximo")
def obtener_proximo():
    vuelo = lista_vuelos.obtener_primero()
    if vuelo:
        return vuelo.__dict__
    raise HTTPException(status_code=404, detail="No hay vuelos.")

# GET /vuelos/ultimo
@app.get("/vuelos/ultimo")
def obtener_ultimo():
    vuelo = lista_vuelos.obtener_ultimo()
    if vuelo:
        return vuelo.__dict__
    raise HTTPException(status_code=404, detail="No hay vuelos.")

# POST /vuelos/insertar
@app.post("/vuelos/insertar")
def insertar_en_posicion(vuelo: VueloIn, posicion: int):
    db = SessionLocal()
    try:
        vuelo_db = VueloDB(
            codigo=vuelo.codigo,
            estado=vuelo.estado,
            hora=vuelo.hora,
            origen=vuelo.origen,
            destino=vuelo.destino
        )
        db.add(vuelo_db)
        db.commit()

        nuevo_vuelo = Vuelo(
            codigo=vuelo.codigo,
            estado=vuelo.estado,
            hora=vuelo.hora,
            origen=vuelo.origen,
            destino=vuelo.destino
        )
        lista_vuelos.insertar_en_posicion(nuevo_vuelo, posicion)
        return {"mensaje": f"Vuelo insertado en la posición {posicion}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# DELETE /vuelos/extraer
@app.delete("/vuelos/extraer")
def extraer_de_posicion(posicion: int):
    db = SessionLocal()
    try:
        vuelo = lista_vuelos.extraer_de_posicion(posicion)
        if vuelo:
            vuelo_en_db = db.query(VueloDB).filter(VueloDB.codigo == vuelo.codigo).first()
            if vuelo_en_db:
                db.delete(vuelo_en_db)
                db.commit()
            return {"mensaje": f"Vuelo {vuelo.codigo} eliminado correctamente."}
        raise HTTPException(status_code=404, detail="Posición inválida o lista vacía.")
    finally:
        db.close()

# GET /vuelos/lista
@app.get("/vuelos/lista")
def obtener_lista_vuelos():
    return [v.__dict__ for v in lista_vuelos.obtener_lista()]

# PATCH /vuelos/reordenar
@app.patch("/vuelos/reordenar")
def reordenar(posicion_origen: int, posicion_destino: int):
    vuelo = lista_vuelos.extraer_de_posicion(posicion_origen)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Posición origen inválida.")
    lista_vuelos.insertar_en_posicion(vuelo, posicion_destino)
    return {"mensaje": f"Vuelo reubicado de {posicion_origen} a {posicion_destino}."}

# Ejecutar el servidor automáticamente si se ejecuta este script directamente
if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    # Abrir la documentación Swagger en el navegador automáticamente
    def abrir_docs():
        webbrowser.open("http://127.0.0.1:8000/docs")

    threading.Timer(1.5, abrir_docs).start()

    uvicorn.run("Vuelos_API:app", host="127.0.0.1", port=8000, reload=True)
