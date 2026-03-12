import getpass 
import logging
import os
from pathlib import Path
from datetime import datetime
import socket
import traceback
from Funciones.Database import db

class Reutilizables:
    """Clase para manejo de ambiente y logging del proyecto"""
    
    def __init__(self, path_proyecto, path_audit, path_logs, path_temp, path_insumo, path_resultado, schema):
        self.path_proyecto = Path(path_proyecto)
        self.path_audit = Path(path_audit)
        self.path_logs = Path(path_logs)
        self.path_temp = Path(path_temp)
        self.path_insumo = Path(path_insumo)
        self.path_resultado = Path(path_resultado)
        
        # Schema del proyecto
        self.schema = schema

        # Configurar logger
        self._configurar_logger()

    
    def _configurar_logger(self):
        """Configura el sistema de logging"""
        # Crear carpeta de logs si no existe
        self.path_logs.mkdir(parents=True, exist_ok=True)
        maquina = socket.gethostname()
        usuario = getpass.getuser()
        # Nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%d%m%Y")
        log_file = self.path_logs / f"Log_{maquina}_{usuario}_{timestamp}.txt"
        robbot = "ROBOT"
        
        # Configuración del logger
        logging.basicConfig(
            level=logging.INFO,
            # FECHA HORA | ESTADO | MENSAJE | CODIGOROBOT | TASKNAME   
            format=rf'%(asctime)s | %(levelname)-2s | %(message)-10s | {robbot} | %(funcName)-20s ',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # También mostrar en consola
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def crear_carpetas(self):
        """Crea todas las carpetas necesarias para el proyecto"""
        try:
            carpetas = {
                'Proyecto': self.path_proyecto,
                'Auditoría': self.path_audit,
                'Logs': self.path_logs,
                'Temporal': self.path_temp,
                'Insumos': self.path_insumo,
                'Resultados': self.path_resultado
            }
            
            for nombre, carpeta in carpetas.items():
                if not carpeta.exists():
                    carpeta.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"✓ Carpeta creada: {nombre} -> {carpeta}")
                else:
                    self.logger.debug(f"Carpeta ya existe: {nombre} -> {carpeta}")
            
            self.logger.info("Despliegue de ambiente completado exitosamente")
            return True
            
        except Exception as e:
            self.logger.exception(f"Error al crear carpetas: ", exc_info=True)
            return False
    
    def limpiar_carpeta_temp(self):
        """Limpia archivos temporales"""
        try:
            archivos_eliminados = 0
            for archivo in self.path_temp.glob('*'):
                if archivo.is_file():
                    archivo.unlink()
                    archivos_eliminados += 1
            
            self.logger.info(f"Carpeta temporal limpiada. {archivos_eliminados} archivos eliminados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al limpiar carpeta temporal: {str(e)}")
            return False
        
    def get_config(self):
        """Obtiene configuración desde base de datos"""
        try:
            query = f"SELECT Nombre, Valor FROM {self.schema}.Parametros"
            self.logger.debug("Ejecutando consulta para obtener configuración")
            resultado = db.fetch_all(query)
            config = {fila['Nombre']: fila['Valor'] for fila in resultado}
            self.logger.info("Configuración obtenida exitosamente")
            return config
        except Exception as e:
            self.logger.error(f"Error al obtener configuración: {str(e)}", exc_info=True)
            return {}
        
