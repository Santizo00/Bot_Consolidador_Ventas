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
│   └─ bot.log                  # Registro de ejecución, errores y auditoría del bot
│
├─ models/
│   └─ ventas_agrupadas.py      # Modelo de datos para VentasAgrupadas (mapeo, validación y UPSERT)
│
├─ queries/
│   ├─ delete_ventas.sql        # Limpieza idempotente por día/sucursal
│   ├─ upsert_ventas.sql        # Inserción/actualización idempotente
│   └─ select_ventas.sql        # Agregación diaria + proveedor (solo sucursal)
│
├─ services/
│   ├─ auditor.py
│   ├─ extractor.py
│   ├─ loader.py
│   └─ partition_manager.py
│
├─ utils/
│   ├─ helpers.py
│   ├─ logger.py
│   └─ retry.py
|
├─ .env.example                 # Ejemplo de variables de entorno (credenciales y conexiones)
├─ .gitignore                   # Archivos y carpetas excluidos del control de versiones
├─ main.py                      # Punto de entrada y orquestación del bot
├─ README_DB.md                 # Documentación técnica de la base de datos y queries
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

- `settings.py`: parámetros globales (timeouts, reintentos, flags)
- `connections.py`: manejo de conexiones a:
  - Base operativa (SuperPOS)
  - Base agregada local
  - Base agregada en VPS

Las credenciales se cargan desde variables de entorno.

---

### 🔹 `models/`
Define la estructura lógica de los datos que maneja el bot.

- `ventas_agrupadas.py`: representación del modelo VentasAgrupadas para validaciones y mapeo

---

### 🔹 `queries/`
Contiene las consultas SQL separadas del código.

- `select_ventas.sql`: consulta de agregación desde ventasdiarias + productos
- `delete_ventas.sql`: limpieza idempotente por fecha y sucursal
- `upsert_ventas.sql`: inserción/actualización en tablas agregadas

Separar las queries permite:
- mantenimiento sencillo
- auditoría clara
- cambios sin tocar lógica Python

---

### 🔹 `services/`
Contiene la lógica principal del bot.

- `extractor.py`  
  Ejecuta la consulta de agregación y obtiene los datos consolidados.

- `loader.py`  
  Ejecuta DELETE y UPSERT tanto en base local como en la VPS.

- `auditor.py`  
  Compara conteos y sumas entre base local y VPS para validar consistencia.

- `partition_manager.py`  
  Verifica y crea particiones nuevas cuando se requiere (por año).

---

### 🔹 `utils/`
Utilidades compartidas.

- `logger.py`: configuración de logs estructurados
- `retry.py`: lógica de reintentos controlados
- `helpers.py`: funciones comunes reutilizables

---

### 🔹 `logs/`
Almacena los logs de ejecución del bot.

- `bot.log`: eventos, errores y auditorías
- No se registran datos sensibles

---

### 🔹 `run.sh`
Script de ejecución manual o para uso con cron/systemd.

---

## 🤖 Flujo de Ejecución del Bot

1. Ejecuta la consulta de agregación en la sucursal
2. Elimina datos existentes del día actual (idempotencia)
3. Inserta/actualiza datos agregados en base local
4. Inserta/actualiza datos agregados en la VPS
5. Ejecuta auditoría de consistencia
6. Finaliza o reprocesa si detecta inconsistencias

---

## 🔐 Seguridad

- Credenciales vía variables de entorno
- Usuarios MySQL con privilegios mínimos
- Sin puertos abiertos
- Sin acceso entrante desde Internet
- Sin replicación de información sensible

---

## 🚀 Estado del Proyecto

- Diseño de base de datos cerrado
- Arquitectura validada
- Listo para implementación del bot
- Escalable a 60+ sucursales y décadas de información

---


## 👨‍💻 Autor

Desarrollado por [Axel Santizo](https://github.com/Santizo00)