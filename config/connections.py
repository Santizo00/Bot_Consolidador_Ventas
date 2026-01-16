import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class MySQLConnectionManager:
    """
    Maneja conexiones MySQL para:
    - Sucursal (SuperPOS)
    - BD agregada local
    - BD agregada en VPS
    """

    @staticmethod
    def _connect(host, user, password, port, database):
        try:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                port=int(port),
                database=database,
                autocommit=False,
                connection_timeout=10
            )

            if not connection.is_connected():
                raise Exception("No se pudo establecer conexión MySQL")

            return connection

        except Error as e:
            raise Exception(f"Error de conexión MySQL: {e}")

    @classmethod
    def connect_sucursal(cls):
        return cls._connect(
            host=os.getenv("ipSucursal"),
            user=os.getenv("userSucursal"),
            password=os.getenv("passSucursal"),
            port=os.getenv("portSucursal"),
            database=os.getenv("dbSucursal")
        )

    @classmethod
    def connect_local(cls):
        return cls._connect(
            host=os.getenv("ipLocal"),
            user=os.getenv("userLocal"),
            password=os.getenv("passLocal"),
            port=os.getenv("portLocal"),
            database=os.getenv("dbLocal")
        )

    @classmethod
    def connect_vps(cls):
        return cls._connect(
            host=os.getenv("ipVps"),
            user=os.getenv("userVps"),
            password=os.getenv("passVps"),
            port=os.getenv("portVps"),
            database=os.getenv("dbVps")
        )
