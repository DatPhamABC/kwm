import configparser
import json
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


POOL_SIZE_DEFAULT = 5


def db(source):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read('application.ini')

    dbs_config = json.loads(config["database"]["sources"])
    db_config = dbs_config.get(source)
    data_source = extract_datasource(db_config)
    pool_size = POOL_SIZE_DEFAULT

    # config_db = config["database default"]
    # data_source = extract_datasource(config_db)
    # # pool_size = config_db.get("pool_size", POOL_SIZE_DEFAULT)
    engine = create_engine(data_source.get_source(), pool_pre_ping=True, pool_size=pool_size, max_overflow=0)
    return scoped_session(sessionmaker(bind=engine, expire_on_commit=True, autocommit=True, autoflush=True))


def extract_datasource(config):
    source = DataSource()
    source.class_driver = config.get("class_driver")
    source.database = config.get("database")
    source.host = config.get("host")
    source.port = config.get("port")
    source.username = config.get("username")
    source.password = config.get("password")
    return source


class DataSource:
    host = None
    port = None
    class_driver = None
    username = None
    password = None
    database = None

    def get_source(self):
        return URL(drivername=self.class_driver,
                   username=self.username,
                   password=self.password,
                   host=self.host,
                   port=self.port,
                   database=self.database)
