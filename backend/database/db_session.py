import sqlalchemy as sa
import sqlalchemy.orm as orm

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("db not init")

    import backend.database.models.users_model
    import backend.database.models.booking_model

    import os
    db_path = db_file.strip()
    folder = os.path.dirname(db_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    conn_str = f'sqlite:///{db_path}?check_same_thread=False'
    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session():
    global __factory
    if __factory is None:
        raise Exception("db not init")
    return __factory()


