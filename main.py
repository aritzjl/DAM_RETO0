from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict
import datetime

# Crear el motor de la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base declarativa
Base = declarative_base()

# Definir el modelo User actualizado
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    admin = Column(Boolean, default=False)  # Nuevo atributo admin

# Definir el modelo Planta
class Planta(Base):
    __tablename__ = "plantas"

    id = Column(Integer, primary_key=True, index=True)
    luces = Column(Boolean, default=False)
    routers = Column(Boolean, default=False)
    calefaccion = Column(Boolean, default=False)
    
class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    title = Column(String)
    description = Column(String)
    date = Column(String, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="API Reto 0", description="API para gestionar el estado de los dispositivos de las plantas y el sistema de login.", version="1.0")

# Modelos de respuesta
class PlantaResponse(BaseModel):
    id: int
    luces: bool
    routers: bool
    calefaccion: bool

    class Config:
        orm_mode = True

class SwitchResponse(BaseModel):
    message: str
    planta: PlantaResponse

class LoginResponse(BaseModel):
    message: str
    username: str
    admin: bool
    
    
class LogResponse(BaseModel):
    id: int
    username: str
    title: str
    description: str
    date: str

    class Config:
        orm_mode = True

# Función para inicializar usuarios predeterminados
def init_db():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "usuario").first():
        user = User(username="usuario", password="123", admin=False)
        db.add(user)
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(username="admin", password="123", admin=True)
        db.add(admin_user)
    db.commit()
    db.close()

init_db()  # Inicializar usuarios predeterminados

@app.get("/planos", response_model=List[PlantaResponse], summary="Devuelve la lista de plantas", description="Obtiene la lista de todas las plantas con el estado actual de sus dispositivos (luces, routers, calefacción).", tags=["planos"])
async def get_planos(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todas las plantas en la base de datos junto con el estado actual de sus dispositivos (luces, routers, calefacción).
    
    - **db**: Sesión de base de datos.
    
    Returns:
    - **List[PlantaResponse]**: Lista de objetos Planta con los estados de los dispositivos.
    """
    plantas = db.query(Planta).all()
    return plantas

@app.put("/plantas/{planta_id}/switch", response_model=SwitchResponse, summary="Cambia el estado de un dispositivo", description="Cambia el estado de un dispositivo específico (luces, routers, calefacción) en una planta dada.", tags=["planos"])
async def switch_planta(planta_id: int, attribute: str, db: Session = Depends(get_db)):
    """
    Cambia el estado de un dispositivo específico (luces, routers, calefacción) en una planta dada.
    
    - **planta_id**: ID de la planta en la base de datos.
    - **attribute**: Nombre del atributo del dispositivo cuyo estado se desea cambiar ("luces", "routers", "calefaccion").
    - **db**: Sesión de base de datos.
    
    Raises:
    - **HTTPException**: Si la planta no se encuentra (404) o el atributo no es válido (400).
    
    Returns:
    - **SwitchResponse**: Mensaje de éxito y el estado actualizado de la planta.
    """
    planta = db.query(Planta).filter(Planta.id == planta_id).first()
    
    if not planta:
        save_log(db, "admin", "Cambio de estado fallido", "Planta no encontrada")
        raise HTTPException(status_code=404, detail="Planta no encontrada")

    if attribute == "luces":
        planta.luces = not planta.luces
    elif attribute == "routers":
        planta.routers = not planta.routers
    elif attribute == "calefaccion":
        planta.calefaccion = not planta.calefaccion
    else:
        raise HTTPException(status_code=400, detail="Atributo no válido")

    db.commit()
    db.refresh(planta)
    save_log(db, "admin", f"Cambio de estado de {attribute}", f"Estado de {attribute} cambiado en la planta {planta_id}")
    return {"message": f"Estado de {attribute} cambiado exitosamente.", "planta": planta}

@app.post("/login", response_model=LoginResponse, summary="Autenticación de usuario", description="Autentica a un usuario con el nombre de usuario y contraseña proporcionados.", tags=["usuarios"])
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    Autentica a un usuario con el nombre de usuario y contraseña proporcionados.
    
    - **username**: Nombre de usuario.
    - **password**: Contraseña del usuario.
    - **db**: Sesión de base de datos.
    
    Raises:
    - **HTTPException**: Si las credenciales son inválidas (401).
    
    Returns:
    - **LoginResponse**: Mensaje de éxito y un indicador de si el usuario es administrador.
    """
    user = db.query(User).filter(User.username == username).first()

    if not user or not password == user.password:
        save_log(db, username, "Login fallido", "Credenciales inválidas")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    save_log(db, username, "Login exitoso", "Usuario autenticado")
    return {"message": "Login exitoso", "admin": user.admin, "username":user.username}


def save_log(db: Session, username: str, title: str, description: str):
    log = Log(username=username, title=title, description=description)
    db.add(log)
    db.commit()
    db.refresh(log)

@app.get("/logs", response_model=List[LogResponse], summary="Devuelve la lista de logs", description="Obtiene la lista de todos los logs.", tags=["logs"])
async def get_logs(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todos los logs en la base de datos.
    
    - **db**: Sesión de base de datos.
    
    Returns:
    - **List[LogResponse]**: Lista de objetos Log.
    """
    logs = db.query(Log).all()
    return logs
