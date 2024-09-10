from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


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

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

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

@app.get("/planos", summary="Devuelve la lista de plantas, con el estado de sus respectivos dispositivos", tags=["planos"])
async def get_planos(db: Session = Depends(get_db)):
    # Consulta para obtener todas las plantas
    plantas = db.query(Planta).all()
    return plantas

"""@app.get("/plantas-init")
async def plantas_init(db: Session = Depends(get_db)):
    # Crear tres plantas con todos los atributos booleanos en False
    planta1 = Planta(luces=False, routers=False, calefaccion=False)
    planta2 = Planta(luces=False, routers=False, calefaccion=False)
    planta3 = Planta(luces=False, routers=False, calefaccion=False)

    # Añadir las plantas a la base de datos
    db.add_all([planta1, planta2, planta3])
    db.commit()

    # Retornar un mensaje de éxito
    return {"message": "Tres plantas creadas con todos los valores en False."}"""


@app.put("/plantas/{planta_id}/switch", summary="Altera el estado de los dispositivos dada la planta y el tipo de dispositivo", tags=["planos"])
async def switch_planta(planta_id: int, attribute: str, db: Session = Depends(get_db)):
    # Buscar la planta por ID
    planta = db.query(Planta).filter(Planta.id == planta_id).first()
    
    if not planta:
        raise HTTPException(status_code=404, detail="Planta no encontrada")

    # Cambiar el estado del atributo específico
    if attribute == "luces":
        planta.luces = not planta.luces
    elif attribute == "routers":
        planta.routers = not planta.routers
    elif attribute == "calefaccion":
        planta.calefaccion = not planta.calefaccion
    else:
        raise HTTPException(status_code=400, detail="Atributo no válido")

    # Guardar cambios en la base de datos
    db.commit()
    db.refresh(planta)

    return {"message": f"Estado de {attribute} cambiado exitosamente.", "planta": planta}

# Ruta de login para autenticación de usuario
@app.post("/login", summary="Autenticación de usuario", tags=["ususarios"])
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not password == user.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"message": "Login exitoso", "admin": user.admin}
