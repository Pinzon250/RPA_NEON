import pyodbc
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from Config.Configuracion import settings

pyodbc.pooling = True


class SQLServerClient:

    def __init__(self):
        self.connection = None
        self.engine: Engine | None = None

    # =========================
    # CONNECTION
    # =========================
    def _connection_string(self):
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings.db_server};"
            f"DATABASE={settings.db_name};"
            f"UID={settings.db_user};"
            f"PWD={settings.db_password};"
            "TrustServerCertificate=yes;"
        )

    def _alchemy_string(self):
        return (
            f"mssql+pyodbc://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_server}/{settings.db_name}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
        )

    def connect(self):
        if not self.connection:
            self.connection = pyodbc.connect(
                self._connection_string(),
                timeout=10,
                autocommit=False
            )

        if not self.engine:
            self.engine = create_engine(
                self._alchemy_string(),
                fast_executemany=True,
                pool_pre_ping=True
            )

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.engine:
            self.engine.dispose()
            self.engine = None

    # =========================
    # SQL EXECUTION
    # =========================

    def execute(self, query: str, params: tuple | None = None):
        self.connect()
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params or ())
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    # =========================
    # FETCH
    # =========================

    def fetch_all(self, query: str, params: tuple | None = None):
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def fetch_dataframe(self, query: str, params: tuple | None = None):
        self.connect()
        return pd.read_sql(query, self.engine, params=params)

    # =========================
    # DATAFRAME OPERATIONS
    # =========================

    def insert_dataframe(
        self,
        table: str,
        dataframe: pd.DataFrame,
        schema: str | None = None,
        if_exists: str = "append",
        index: bool = False
    ):

        self.connect()
        dataframe.to_sql(
            table,
            self.engine,
            schema=schema,
            if_exists=if_exists,
            index=index,
            method="multi",
            chunksize=1000
        )

    def create_table_from_dataframe(
        self,
        table: str,
        dataframe: pd.DataFrame,
        schema: str | None = None
    ):
        self.connect()
        dataframe.head(0).to_sql(
            table,
            self.engine,
            schema=schema,
            if_exists="replace",
            index=False
        )


db = SQLServerClient()