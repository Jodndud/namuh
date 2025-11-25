from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import pymysql


class MySQL:
    def __init__(self, engine):
        self.engine = engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        session = self.SessionLocal()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def ping(self) -> bool:
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
            return True
        except Exception:
            return False


def init_mysql_pool(settings):
    host = (
        settings.mysql_url.split("//")[1].split(":")[0]
        if "://" in settings.mysql_url
        else settings.mysql_url
    )

    database_url = f"mysql+pymysql://{settings.mysql_username}:{settings.mysql_password}@{host}:{settings.mysql_port}/{settings.mysql_db_name}"

    engine = create_engine(
        database_url, pool_pre_ping=True, pool_size=10, max_overflow=20, echo=False
    )

    return engine


def close_mysql_pool(engine):
    engine.dispose()
