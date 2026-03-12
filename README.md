# RPA NEON

Automatizacion en Python orientada a preparar ambiente, gestionar configuracion y conectarse a SQL Server para soportar procesos del proyecto NEON.

## Objetivo del proyecto

El repositorio contiene la base de un flujo RPA con componentes para:

- Cargar credenciales y parametros desde variables de entorno.
- Conectarse a SQL Server mediante `pyodbc` y `SQLAlchemy`.
- Crear estructura de carpetas de trabajo, logs, auditoria, temporales, insumos y resultados.
- Centralizar utilidades reutilizables para el despliegue de ambiente.

## Estructura del repositorio

```text
RPA_NEON/
|-- MainNEON.py
|-- README.md
|-- requirements.txt
|-- Config/
|   `-- Configuracion.py
|-- Funciones/
|   |-- Database.py
|   `-- Global.py
`-- HU/
	|-- HU00_DespliegueAmbiente.py
	|-- HU01_LecturaInsumos.py
	`-- HU02_SURA.py
```

## Requisitos previos

Antes de instalar el proyecto, asegure lo siguiente:

- Python 3.11 o superior disponible en el equipo.
- `pip` habilitado.
- Microsoft ODBC Driver 17 for SQL Server instalado en Windows.
- Acceso a la base de datos SQL Server configurada para el proyecto.
- Credenciales SAP y base de datos disponibles como variables de entorno.

## Instalacion

### 1. Clonar o ubicarse en el proyecto

```powershell
cd C:\Users\revol\OneDrive\Documentos\NET\NEON\Masiva\RPA_NEON
```

### 2. Crear un entorno virtual

```powershell
python -m venv .venv
```

### 3. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Si usa `cmd` en lugar de PowerShell:

```bat
.venv\Scripts\activate.bat
```

### 4. Instalar dependencias Python

```powershell
pip install -r requirements.txt
```

## Dependencias

El proyecto fija sus dependencias en `requirements.txt`. Las mas relevantes para el funcionamiento actual son:

- `pydantic` y `pydantic-settings`: carga y validacion de configuracion.
- `pyodbc`: conexion directa a SQL Server.
- `SQLAlchemy`: motor de conexion y operaciones tabulares.
- `pandas` y `numpy`: manejo de datos y dataframes.
- `python-dotenv`: soporte para variables desde archivo `.env`.

Dependencias declaradas actualmente:

```text
annotated-types==0.7.0
greenlet==3.3.2
numpy==2.4.3
pandas==3.0.1
pydantic==2.12.5
pydantic-settings==2.13.1
pydantic_core==2.41.5
pyodbc==5.3.0
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
six==1.17.0
SQLAlchemy==2.0.48
typing-inspection==0.4.2
typing_extensions==4.15.0
tzdata==2025.3
```

## Configuracion

La configuracion se define en `Config/Configuracion.py` usando `pydantic-settings`. El codigo espera las siguientes variables:

| Variable | Descripcion |
|---|---|
| `SAP_USER` | Usuario de acceso SAP |
| `SAP_PASSWORD` | Contrasena de acceso SAP |
| `DB_USER` | Usuario de base de datos |
| `DB_PASSWORD` | Contrasena de base de datos |
| `DB_SERVER` | Servidor SQL Server |
| `DB_NAME` | Nombre de la base de datos |

### Archivo `.env`

Segun la configuracion actual del codigo, las variables se cargan desde:

```text
Configuracion/.env
```

Ejemplo de contenido:

```env
SAP_USER=usuario_sap
SAP_PASSWORD=contrasena_sap
DB_USER=usuario_bd
DB_PASSWORD=contrasena_bd
DB_SERVER=servidor_sql
DB_NAME=base_neon
```

## Ejecucion

En el estado actual del repositorio, `MainNEON.py` no contiene logica implementada y no se encontro un punto de entrada productivo definido con `if __name__ == "__main__"`.

Por eso, la ejecucion operativa del robot aun no queda completamente documentada desde el codigo fuente. Aun asi, el flujo previsto por la estructura actual parece apoyarse en estos componentes:

- `HU/HU00_DespliegueAmbiente.py`: utilidades para crear carpetas, configurar logs, auditoria y limpieza temporal.
- `Funciones/Database.py`: cliente reutilizable para conexion, consultas, escritura e insercion de dataframes en SQL Server.
- `Config/Configuracion.py`: carga de configuracion desde variables de entorno.

Cuando el punto de entrada principal quede implementado, la ejecucion probablemente seguira una forma similar a esta:

```powershell
python MainNEON.py
```

## Logs y carpetas de trabajo

La clase `Reutilizables` en `HU/HU00_DespliegueAmbiente.py` contempla la creacion de carpetas para:

- Proyecto
- Auditoria
- Logs
- Temporal
- Insumos
- Resultados

Tambien configura logging en archivo y consola con nombres de log construidos a partir de:

- Nombre de la maquina
- Usuario del sistema
- Fecha actual

## Conexion a base de datos

La conexion a SQL Server usa:

- `pyodbc` con `ODBC Driver 17 for SQL Server`
- `SQLAlchemy` con cadena `mssql+pyodbc`
- `TrustServerCertificate=yes`

Operaciones actualmente disponibles en `Funciones/Database.py`:

- Conexion y cierre de recursos.
- Ejecucion de sentencias SQL.
- Lectura de resultados completos.
- Lectura a `pandas.DataFrame`.
- Insercion de dataframes en tablas.
- Creacion de tablas a partir de un dataframe.

## Estado actual

El proyecto ya tiene una base de configuracion y conexion, pero todavia presenta puntos que conviene cerrar para una puesta en marcha completa:

- `MainNEON.py` esta vacio.
- No existe un archivo `.env.example` en el repositorio.
- No hay un flujo principal de ejecucion claramente implementado.
- `Funciones/Global.py` no contiene logica utilizable en este momento.

## Siguientes pasos recomendados

1. Definir el flujo principal en `MainNEON.py`.
2. Agregar un `.env.example` sin credenciales reales.
3. Documentar el proceso exacto de ejecucion del robot cuando quede implementado.
4. Incorporar ejemplos de insumos y resultados esperados.
