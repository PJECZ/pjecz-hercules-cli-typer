"""
Database
"""

from collections.abc import Generator, Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from pjecz_hercules_cli_typer.config.setttings import Settings


class Base(DeclarativeBase):
    """Clase base declarativa de la que heredan todos los modelos."""


@lru_cache
def get_engine() -> Engine:
    """Crea y recuerda el engine de SQLAlchemy (evita recrearlo entre peticiones)."""
    return create_engine(Settings().database_uri)


engine = get_engine()


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Crea y recuerda el factory de sesiones sobre el engine."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


session_factory = get_session_factory()


@contextmanager
def session() -> Generator[Session]:
    """Context manager síncrono que devuelve una sesión y la limpia al salir."""
    db_session = session_factory()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def get_db() -> Iterator[Session]:
    """
    Dependencia de FastAPI que provee una sesión.

    Uso en las rutas: `DB: get_db`. Compromete la transacción al final y, en
    caso de error, la revierte.
    """
    with session() as db_session:
        yield db_session
