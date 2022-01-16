from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import Config

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
Base = declarative_base(metadata=metadata)
Session_ = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@contextmanager
def session_scope() -> Session:
    session = Session_()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    from src.database import models  # noqa F401

    Base.metadata.create_all(bind=engine)
