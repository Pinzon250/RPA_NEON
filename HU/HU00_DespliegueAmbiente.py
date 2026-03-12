import getpass
import logging
import os
from pathlib import Path
from datetime import datetime
import socket
from Funciones.Database import db


# ─────────────────────────────────────────────
#  CONSTANTES DEL PROYECTO
#  Único lugar que cambia entre robots
# ─────────────────────────────────────────────
SCHEMA       = "AutorizacionesMasivo"
NOMBRE_ROBOT = "ROBOT"
AMBIENTE     = "DEV"   # DEV | QA | PROD


# ─────────────────────────────────────────────
#  LOGGER TEMPORAL
#  Se usa solo durante el despliegue, antes de
#  tener la ruta definitiva desde la BD
# ─────────────────────────────────────────────
def _logger_temporal() -> logging.Logger:
    """Logger de consola para la fase previa a tener las rutas desde BD."""
    logger = logging.getLogger("despliegue_temp")
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG if AMBIENTE == "DEV" else logging.INFO)
    fmt = logging.Formatter(
        rf'%(asctime)s | %(levelname)-8s | %(message)s | {NOMBRE_ROBOT} | %(funcName)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


# ─────────────────────────────────────────────
#  PASO 1 — CARGAR CONFIGURACIÓN DESDE BD
# ─────────────────────────────────────────────
def in_config() -> dict:
    """
    Conecta a la BD y carga toda la tabla Parametros.
    Retorna un dict {Nombre: Valor} con toda la configuración del proyecto.
    Es el primer paso del despliegue: todo lo demás depende de este dict.

    Ejemplo de uso posterior:
        config = in_config()
        ruta_log = config["RUTA_LOG"]
    """
    log = _logger_temporal()
    config = {}
    try:
        query  = f"SELECT Nombre, Valor FROM {SCHEMA}.Parametros"
        filas  = db.fetch_all(query)
        config = {fila["Nombre"]: fila["Valor"] for fila in filas}
        log.info(f"Configuracion cargada desde BD | parametros={len(config)}")
        return config
    except Exception as e:
        log.error(f"Error cargando configuracion desde BD: {e}", exc_info=True)
        return {}

# ─────────────────────────────────────────────
#  PASO 2 — CONFIGURAR LOGGER DEFINITIVO
# ─────────────────────────────────────────────
def _configurar_logger(ruta_logs: Path) -> logging.Logger:
    """
    Crea el logger definitivo con archivo en la ruta que vino de BD.
    Reemplaza al logger temporal.
    """
    ruta_logs.mkdir(parents=True, exist_ok=True)

    maquina  = socket.gethostname()
    usuario  = getpass.getuser()
    ts       = datetime.now().strftime("%d%m%Y")
    log_file = ruta_logs / f"Log_{maquina}_{usuario}_{ts}.txt"

    logger = logging.getLogger(NOMBRE_ROBOT)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if AMBIENTE == "DEV" else logging.INFO)

    fmt = logging.Formatter(
        rf'%(asctime)s | %(levelname)-8s | %(message)-60s | {NOMBRE_ROBOT} | %(funcName)-20s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ─────────────────────────────────────────────
#  PASO 3 — CREAR CARPETAS
# ─────────────────────────────────────────────
def _crear_carpetas(carpetas: dict, logger: logging.Logger):
    """
    Recibe un dict {nombre_legible: Path} y crea cada carpeta.
    Loguea éxito o error por carpeta sin detener el proceso.
    """
    for nombre, ruta in carpetas.items():
        try:
            ruta.mkdir(parents=True, exist_ok=True)
            logger.info(f"Carpeta lista | {nombre} -> {ruta}")
        except Exception as e:
            logger.error(f"Error creando carpeta {nombre}: {e}")


# ─────────────────────────────────────────────
#  PASO 4 — LIMPIAR TEMPORALES
# ─────────────────────────────────────────────
def _limpiar_temp(ruta_temp: Path, logger: logging.Logger):
    """Elimina archivos del run anterior en la carpeta temporal."""
    eliminados = 0
    try:
        for archivo in ruta_temp.glob("*"):
            if archivo.is_file():
                archivo.unlink()
                eliminados += 1
        logger.info(f"Temp limpiada | archivos eliminados={eliminados}")
    except Exception as e:
        logger.error(f"Error limpiando temp: {e}")


# ─────────────────────────────────────────────
#  FUNCIÓN PRINCIPAL
#  Llamar desde el robot: config = desplegar_ambiente()
# ─────────────────────────────────────────────
def desplegar_ambiente() -> dict:
    """
    Orquesta el despliegue completo del ambiente RPA.

    Flujo:
        1. Carga config desde BD  (in_config)
        2. Lee rutas desde config
        3. Inicializa logger definitivo con ruta de BD
        4. Crea todas las carpetas del proyecto
        5. Limpia archivos temporales del run anterior

    Retorna:
        dict con todos los parámetros de la tabla Parametros.
        El dict estará vacío si la BD no estuvo disponible.

    Ejemplo de uso en el robot (HU01, HU02, etc.):
        from HU00_DespliegueAmbiente import desplegar_ambiente

        config = desplegar_ambiente()
        ruta_insumo = Path(config["RUTA_INSUMO"])
        url_sistema = config["URL_SISTEMA"]
    """
    log_temp = _logger_temporal()
    log_temp.info("="*60)
    log_temp.info(f"Iniciando despliegue | Robot={NOMBRE_ROBOT} | Ambiente={AMBIENTE}")

    # ── 1. Config desde BD ──────────────────────────────────────────
    config = in_config()

    if not config:
        log_temp.error("Config vacia: no se pudo conectar a BD. Ambiente parcial.")
        return config

    # ── 2. Resolver rutas desde el config ───────────────────────────
    #   Las claves deben existir en la tabla Parametros del proyecto.
    #   Ajusta los nombres de clave a los que uses en tu tabla.
    try:
        ruta_log      = Path(config["RUTA_LOG"])
        ruta_audit    = Path(config["RUTA_AUDITORIA"])
        ruta_temp     = Path(config["RUTA_TEMP"])
        ruta_insumo   = Path(config["RUTA_INSUMO"])
        ruta_resultado= Path(config["RUTA_RESULTADO"])
    except KeyError as e:
        log_temp.error(f"Clave de ruta faltante en Parametros: {e}")
        return config

    # ── 3. Logger definitivo (ya tiene la ruta real) ─────────────────
    logger = _configurar_logger(ruta_log)
    logger.info("Logger definitivo inicializado")

    # ── 4. Crear carpetas ────────────────────────────────────────────
    carpetas = {
        "Logs":       ruta_log,
        "Auditoria":  ruta_audit,
        "Temp":       ruta_temp,
        "Insumos":    ruta_insumo,
        "Resultados": ruta_resultado,
    }
    _crear_carpetas(carpetas, logger)

    # ── 5. Limpiar temporales ────────────────────────────────────────
    _limpiar_temp(ruta_temp, logger)

    logger.info("Despliegue completado exitosamente")
    logger.info("="*60)

    return config