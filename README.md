# Reto 0 API

## Tabla de Contenidos

- [Reto 0 API](#reto-0-api)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Introducción](#introducción)
  - [Características](#características)
  - [Instalación](#instalación)
  - [Uso](#uso)
  - [Puntos de API](#puntos-de-api)
    - [Puntos de Usuario](#puntos-de-usuario)
    - [Puntos de Plantas](#puntos-de-plantas)
  - [Modelos de Base de Datos](#modelos-de-base-de-datos)
    - [Modelo de Usuario](#modelo-de-usuario)
    - [Modelo de Planta](#modelo-de-planta)
    - [Modelo PlantaResponse](#modelo-plantaresponse)
  - [Configuración](#configuración)
  - [Desarrollo](#desarrollo)
  - [Despliegue](#despliegue)

## Introducción

Este proyecto es una aplicación web construida con FastAPI y SQLAlchemy. Proporciona una API RESTful para gestionar usuarios y dispositivos de plantas.

## Características

- Autenticación y gestión de usuarios
- Gestión de dispositivos de plantas
- Actualizaciones en tiempo real con Uvicorn
- Registro detallado

## Instalación

Para instalar el proyecto, sigue estos pasos:

1. Clona el repositorio:
    
    ```
    git clone <url-del-repositorio>
    cd <directorio-del-repositorio
    ```
    
2. Crea y activa un entorno virtual:
    
    ```
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    
    ```
    
3. Instala las dependencias:
    
    ```
    pip install -r requirements.txt
    ```
    

## Uso

Para ejecutar la aplicación, utiliza el siguiente comando:

```go
```sh
uvicorn main:app --reload
```

Alternativamente, puedes usar los scripts proporcionados:

- En Windows:
    
    `restart.bat`
    
- En sistemas basados en Unix:
    
    `./restart.sh`
    

## Puntos de API
Puedes encontrar la documentaicón detallada de los endpoints en https://retocero.api.tenbeltz.com/docs
### Puntos de Usuario

- `GET /users`: Recupera una lista de usuarios.
- `POST /users`: Crea un nuevo usuario.
- `GET /users/{id}`: Recupera un usuario por ID.
- `PUT /users/{id}`: Actualiza un usuario por ID.
- `DELETE /users/{id}`: Elimina un usuario por ID.

### Puntos de Plantas

- `GET /plantas`: Recupera una lista de plantas.
- `POST /plantas`: Crea una nueva planta.
- `GET /plantas/{id}`: Recupera una planta por ID.
- `PUT /plantas/{id}`: Actualiza una planta por ID.
- `DELETE /plantas/{id}`: Elimina una planta por ID.

## Modelos de Base de Datos

### Modelo de Usuario

Definido en `main.py`:

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    admin = Column(Boolean, default=False)
```

### Modelo de Planta

Definido en `main.py`:

```python
class Planta(Base):
    __tablename__ = "plantas"
    id = Column(Integer, primary_key=True, index=True)
    luces = Column(Boolean, default=False)
    routers = Column(Boolean, default=False)
    calefaccion = Column(Boolean, default=Fals
```

### Modelo PlantaResponse

Definido en `main.py`:

```python
class PlantaResponse(BaseModel):
    id: int
    luces: bool
    routers: bool
    calefaccion: bool

    class Config:
        orm_mode = True
```

## Configuración

La aplicación utiliza SQLAlchemy para ORM y Pydantic para validación de datos. Asegúrate de tener configurada la URL correcta de la base de datos en tus variables de entorno.

## Desarrollo

Para configurar el entorno de desarrollo, sigue los pasos de instalación y luego ejecuta:

```css
uvicorn main:app --reload
```

## Despliegue

Para el despliegue, asegúrate de tener un servidor listo para producción. Puedes usar el script `restart.sh` proporcionado para sistemas basados en Unix.
