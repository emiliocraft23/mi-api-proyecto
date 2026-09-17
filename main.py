from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import List, Optional

# --- 1. MODELOS DE BASE DE DATOS ---
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str

class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    # Clave foránea para relacionar el libro con un usuario
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")

# --- 2. CONFIGURACIÓN DE LA BASE DE DATOS ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- 3. INICIALIZAR FASTAPI ---
app = FastAPI(
    title="API de Usuarios y Libros",
    description="Operaciones CRUD para una entrega universitaria",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- 4. ENDPOINTS PARA USUARIOS ---
@app.post("/usuarios/", response_model=Usuario)
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@app.get("/usuarios/", response_model=List[Usuario])
def leer_usuarios(session: Session = Depends(get_session)):
    return session.exec(select(Usuario)).all()

@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(usuario)
    session.commit()
    return {"mensaje": "Usuario eliminado correctamente"}

# --- 5. ENDPOINTS PARA LIBROS ---
@app.post("/libros/", response_model=Libro)
def crear_libro(libro: Libro, session: Session = Depends(get_session)):
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

@app.get("/libros/", response_model=List[Libro])
def leer_libros(session: Session = Depends(get_session)):
    return session.exec(select(Libro)).all()

@app.delete("/libros/{libro_id}")
def eliminar_libro(libro_id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    session.delete(libro)
    session.commit()
    return {"mensaje": "Libro eliminado correctamente"}
