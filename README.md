# Bot_Consolidador_Ventas

## 📌 Descripción General

**Bot_Consolidador_Ventas** es un bot de sincronización diseñado para consolidar ventas agregadas desde múltiples sucursales hacia una base de datos centralizada en una VPS pública.

El bot se ejecuta **localmente en cada sucursal**, procesa la información desde la base operativa (SuperPOS), genera resúmenes diarios y los envía de forma segura a la base central, **sin exponer servidores internos, sin VPN y sin acceso directo desde Internet**.

Este proyecto está enfocado en rendimiento, seguridad, escalabilidad histórica y facilidad de auditoría.

---

## 🎯 Objetivos del Bot

- Consolidar ventas agregadas por:
  - Fecha
  - Sucursal
  - Producto (UPC)
  - Proveedor
  - Departamento, categoría y subcategoría
- Evitar consultas directas a bases operativas desde Internet
- Eliminar la necesidad de VPN para usuarios finales
- Garantizar procesos idempotentes y auditables
- Soportar crecimiento de datos por décadas

---

## 🧠 Principios de Diseño

- **Push de datos**: la sucursal envía, la VPS nunca consulta
- **Datos agregados**: no se replican tickets ni movimientos
- **Procesamiento local**: la carga pesada ocurre en la sucursal
- **Idempotencia**: el bot puede ejecutarse múltiples veces sin duplicar datos
- **Seguridad por diseño**: mínimo privilegio y sin puertos abiertos

---

## 🏗️ Estructura del Proyecto

```
Bot_Consolidador_Ventas/
├─ config/
│   ├─ connections.py           # Gestión centralizada de conexiones MySQL
│   └─ settings.py              # Configuración de comportamiento del bot
│
├─ logs/
│   ├─ bot.log                  # Registro de ejecución, errores y auditoría del bot
│   └─ bitacora_extraccion.csv  # Bitácora CSV con resumen de cada procesamiento
│
├─ models/
│   └─ ventas_agrupadas.py      # Modelo de datos para VentasAgrupadas (mapeo y validación)
│
├─ queries/
│   └─ upsert_ventas.sql        # Inserción/actualización idempotente
│
├─ services/
│   ├─ auditor.py               # Validación de consistencia entre BD local y VPS
│   ├─ extractor.py             # Ejecución del SP de agregación desde la sucursal
│   ├─ loader.py                # UPSERT idempotente en BD local y VPS
│   └─ reprocessor.py           # Limpieza de datos para reprocesamiento
│
├─ utils/
│   ├─ bitacora_csv.py          # Registro de bitácora en formato CSV
│   ├─ helpers.py               # Funciones auxiliares reutilizables
│   └─ logger.py                # Configuración centralizada de logging
│
├─ .env.example                 # Ejemplo de variables de entorno (credenciales y conexiones)
├─ .gitignore                   # Archivos y carpetas excluidos del control de versiones
├─ main.py                      # Punto de entrada y orquestación del bot
├─ README_DB.md                 # Documentación técnica de la base de datos y stored procedures
├─ README.md                    # Documentación general del proyecto
├─ requirements.txt             # Dependencias necesarias para ejecutar el bot
└─ run.sh                       # Script de ejecución manual o automatizada (cron/systemd)
```

---

## 📂 Descripción de Carpetas y Archivos

### 🔹 `main.py`
Punto de entrada del bot.

Responsabilidades:
- Orquestar el flujo completo del proceso
- Ejecutar los servicios en orden
- Manejar errores globales
- Registrar eventos críticos

---

### 🔹 `config/`
Configuración general del proyecto.

- `connections.py`: manejo de conexiones a:
  - Base operativa (SuperPOS)
  - Base agregada local
  - Base agregada en VPS
- `settings.py`: parámetros globales (timeouts, reintentos, flags)

Las credenciales se cargan desde variables de entorno (.env).

---

### 🔹 `logs/`
Almacena los logs de ejecución del bot.

- `bot.log`: eventos, errores y auditorías en formato detallado
- `bitacora_extraccion.csv`: resumen de cada procesamiento (fecha, estado, intentos, filas)
- No se registran datos sensibles

---

### 🔹 `models/`
Define la estructura lógica de los datos que maneja el bot.

- `ventas_agrupadas.py`: representación del modelo VentasAgrupadas para validaciones y mapeo desde stored procedures

---

### 🔹 `queries/`
Contiene consultas SQL separadas del código.

- `upsert_ventas.sql`: inserción/actualización en tablas agregadas

**Nota:** Las demás operaciones (SELECT, DELETE, auditorías) se ejecutan mediante **stored procedures** directamente en las bases de datos.

Separar las queries permite:
- mantenimiento sencillo
- auditoría clara
- cambios sin tocar lógica Python

---

### 🔹 `services/`
Contiene la lógica principal del bot.

- `auditor.py`  
  Ejecuta stored procedures de auditoría para comparar conteos y sumas entre base operativa, local y VPS.

- `extractor.py`  
  Ejecuta el stored procedure `sp_select_ventas_diarias` y obtiene los datos consolidados.

- `loader.py`  
  Ejecuta UPSERT tanto en base local como en la VPS.

- `reprocessor.py`  
  Ejecuta el stored procedure `sp_delete_ventas_agrupadas` para limpiar datos antes de reprocesar.

---

### 🔹 `utils/`
Utilidades compartidas.

- `bitacora_csv.py`: registro de resumen de procesamiento en formato CSV
- `helpers.py`: funciones comunes reutilizables (cálculo de fechas a procesar)
- `logger.py`: configuración de logs estructurados

---

### 🔹 `run.sh`
Script de ejecución manual o para uso con cron/systemd.

---

## Flujo de Ejecución del Bot

1. Ejecuta el **stored procedure** `sp_select_ventas_diarias` en la sucursal para obtener ventas agregadas
2. Valida y mapea los datos al modelo `VentasAgrupadas`
3. Ejecuta **UPSERT** idempotente en base local
4. Ejecuta **UPSERT** idempotente en la VPS
5. Ejecuta **stored procedures de auditoría** para validar consistencia:
   - `sp_audit_operativa` en base operativa
   - `sp_audit_ventas_agrupadas` en base local y VPS
6. Si la auditoría falla, ejecuta `sp_delete_ventas_agrupadas` y reprocesa
7. Registra el resultado en `bitacora_extraccion.csv`
8. Maneja reintentos automáticos en caso de error

---

## 🛠️ Instalación y Ejecución (Modo Desarrollo)

### Requisitos
- Python 3.10 o superior
- MySQL / MariaDB
- Acceso a las bases de datos configuradas

---

### 1️⃣ Clonar el repositorio

```bash
git https://github.com/Santizo00/Bot_Consolidador_Ventas.git
cd Bot_Consolidador_Ventas
```

---

### 2️⃣ Crear entorno virtual (recomendado)

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configurar variables de entorno

Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Editar el archivo `.env` con los valores correctos para el entorno local.

---

### 5️⃣ Ejecutar el bot en modo desarrollo

```bash
./run.sh
```

O directamente:

```bash
python3 main.py
```

---

### 🧪 Recomendaciones para Modo Desarrollo

Se recomienda configurar en `config/settings.py`:

- `DRY_RUN = True`
- `RUN_LOCAL_ONLY = True`

Esto permite validar:
- conexiones
- queries
- extracción de datos
- flujo completo del bot
sin afectar la base de datos en producción.

---

## 🚀 Ejecución en Producción

En producción, el bot se ejecuta como un proceso en segundo plano,
programado mediante:

- `cron` (ejecución periódica)
- o `systemd` (servicio persistente)

Características del modo producción:
- Ejecución automática
- Sin intervención manual
- Logs persistentes
- Monitoreo mediante códigos de salida

El despliegue en producción **no utiliza `run.sh` manualmente**, sino una
tarea programada que invoca `main.py` de forma controlada.

---


## 👨‍💻 Autor

Desarrollado por [Axel Santizo](https://github.com/Santizo00)