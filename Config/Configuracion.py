from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):

    # Configuración SAP
    sap_user: str = Field(alias="SAP_USER")
    sap_password: str = Field(alias="SAP_PASSWORD")

    # Configuración Base de Datos
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_server: str = Field(alias="DB_SERVER")
    db_name: str = Field(alias="DB_NAME")

    model_config = SettingsConfigDict(
        env_file="Configuracion/.env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Config()