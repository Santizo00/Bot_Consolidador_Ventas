# README_DB.md
## Diseño de Base de Datos – Ventas Centralizadas

### 📌 Objetivo
Centralizar ventas agregadas de múltiples sucursales en una base de datos pública (VPS),
sin exponer bases operativas, sin VPN y sin consultas en tiempo real, garantizando:
- alto rendimiento
- escalabilidad histórica 
- consultas rápidas para web y reportes

---

## 🧠 Enfoque General

- No se almacenan movimientos ni tickets
- No se accede a bases operativas desde Internet
- Cada sucursal procesa y envía datos agregados
- La VPS solo recibe información resumida
- El procesamiento pesado ocurre en la sucursal, no en la web
- **Se utilizan stored procedures para todas las operaciones críticas**

---

## 📊 Tabla Principal: VentasAgrupadas

Tabla de hechos agregados a nivel:
- día
- sucursal
- producto (UPC)

Incluye proveedor y jerarquía de producto para evitar joins costosos en reportes.

### Estructura

```sql
CREATE TABLE VentasAgrupadas (
    Fecha DATE,
    IdSucursal INT,
    Upc VARCHAR(20),

    IdProveedor INT,
    IdDepartamento INT,
    IdCategoria INT,
    IdSubcategoria INT,

    Unidades DECIMAL(14,2),
    VentaTotal DECIMAL(14,2),
    CostoTotal DECIMAL(14,2),

    UltimaSync DATETIME NOT NULL,

    INDEX idx_sucursal_fecha (IdSucursal, Fecha),
    INDEX idx_upc_fecha (Upc, Fecha),
    INDEX idx_proveedor_fecha (IdProveedor, Fecha),
    INDEX idx_departamento_fecha (IdDepartamento, Fecha),
    INDEX idx_categoria_fecha (IdCategoria, Fecha),
    INDEX idx_subcategoria_fecha (IdSubcategoria, Fecha)
)
ENGINE=InnoDB
PARTITION BY RANGE (YEAR(Fecha)) (
    PARTITION p1998 VALUES LESS THAN (1999),
    PARTITION p1999 VALUES LESS THAN (2000),
    PARTITION p2000 VALUES LESS THAN (2001),
    PARTITION p2001 VALUES LESS THAN (2002),
    PARTITION p2002 VALUES LESS THAN (2003),
    PARTITION p2003 VALUES LESS THAN (2004),
    PARTITION p2004 VALUES LESS THAN (2005),
    PARTITION p2005 VALUES LESS THAN (2006),
    PARTITION p2006 VALUES LESS THAN (2007),
    PARTITION p2007 VALUES LESS THAN (2008),
    PARTITION p2008 VALUES LESS THAN (2009),
    PARTITION p2009 VALUES LESS THAN (2010),
    PARTITION p2010 VALUES LESS THAN (2011),
    PARTITION p2011 VALUES LESS THAN (2012),
    PARTITION p2012 VALUES LESS THAN (2013),
    PARTITION p2013 VALUES LESS THAN (2014),
    PARTITION p2014 VALUES LESS THAN (2015),
    PARTITION p2015 VALUES LESS THAN (2016),
    PARTITION p2016 VALUES LESS THAN (2017),
    PARTITION p2017 VALUES LESS THAN (2018),
    PARTITION p2018 VALUES LESS THAN (2019),
    PARTITION p2019 VALUES LESS THAN (2020),
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION pMax VALUES LESS THAN MAXVALUE
);
```

### Decisiones clave
- Sin foreign keys (limitación MySQL + particiones)
- Integridad controlada por el bot
- Particionamiento anual para escalar décadas
- Clave primaria idempotente para reprocesos


### Agregar más particiones (Anual)

**Nota:** Actualmente el bot no gestiona particiones automáticamente. Las particiones deben agregarse manualmente según sea necesario.

```sql
ALTER TABLE VentasAgrupadas
ADD PARTITION (
    PARTITION p2027 VALUES LESS THAN (2028)
);
```
---

## � Stored Procedures

El bot utiliza stored procedures para todas las operaciones críticas, garantizando consistencia y rendimiento.

---

### 🟢 1. SP de Extracción – `sp_select_ventas_diarias`

**Propósito:** Extraer y agregar ventas del día desde la base operativa (sucursal).

**Base de datos:** Operativa (SuperPOS)

**Parámetros:**
- `p_fecha` (DATE): Fecha a procesar

**Retorna:** Ventas agregadas por UPC con información de proveedor y jerarquía de producto.

```sql
DELIMITER $$

CREATE PROCEDURE sp_select_ventas_diarias (
    IN p_fecha DATE
)
BEGIN
    SELECT
        v.Fecha AS Fecha,
        v.Upc   AS Upc,

        COALESCE(p.IdProveedores, 0)   AS IdProveedor,
        COALESCE(v.IdDepartamentos, 0) AS IdDepartamento,
        COALESCE(v.IdCategorias, 0)    AS IdCategoria,
        COALESCE(v.IdSubcategorias, 0) AS IdSubcategoria,

        SUM(v.Cantidad)    AS Unidades,
        SUM(v.MontoTotal)  AS VentaTotal,
        SUM(v.CostoTotal)  AS CostoTotal
    FROM ventasdiarias v
    LEFT JOIN productos p
        ON p.Upc = v.Upc
    WHERE v.Fecha = p_fecha
    GROUP BY
        v.Fecha,
        v.Upc,
        COALESCE(p.IdProveedores, 0),
        COALESCE(v.IdDepartamentos, 0),
        COALESCE(v.IdCategorias, 0),
        COALESCE(v.IdSubcategorias, 0);
END$$

DELIMITER ;
```

---

### 🟢 2. SP de Eliminación – `sp_delete_ventas_agrupadas`

**Propósito:** Limpiar datos de una fecha específica para permitir reprocesamiento idempotente.

**Base de datos:** Local y VPS (VentasAgrupadas)

**Parámetros:**
- `p_fecha` (DATE): Fecha a eliminar
- `p_id_sucursal` (INT): ID de la sucursal

**Retorna:** N/A (operación DELETE)

```sql
DELIMITER $$

CREATE PROCEDURE sp_delete_ventas_agrupadas (
    IN p_fecha DATE,
    IN p_id_sucursal INT
)
BEGIN
    DELETE
    FROM VentasAgrupadas
    WHERE Fecha = p_fecha
      AND IdSucursal = p_id_sucursal;
END$$

DELIMITER ;
```

---

### 🟢 3. SP de Auditoría Operativa – `sp_audit_operativa`

**Propósito:** Obtener totales de ventas desde la base operativa para validación.

**Base de datos:** Operativa (SuperPOS)

**Parámetros:**
- `p_fecha` (DATE): Fecha a auditar

**Retorna:** Totales de Unidades, Venta y Costo.

```sql
DELIMITER $$

CREATE PROCEDURE sp_audit_operativa (
    IN p_fecha DATE
)
BEGIN
    SELECT
        COALESCE(SUM(Cantidad), 0)   AS TotalUnidades,
        COALESCE(SUM(MontoTotal), 0) AS TotalVenta,
        COALESCE(SUM(CostoTotal), 0) AS TotalCosto
    FROM ventasdiarias
    WHERE Fecha = p_fecha;
END$$

DELIMITER ;
```

---

### 🟢 4. SP de Auditoría Agregadas – `sp_audit_ventas_agrupadas`

**Propósito:** Obtener totales desde VentasAgrupadas (local o VPS) para validación.

**Base de datos:** Local y VPS (VentasAgrupadas)

**Parámetros:**
- `p_fecha` (DATE): Fecha a auditar
- `p_id_sucursal` (INT): ID de la sucursal

**Retorna:** Totales de Unidades, Venta y Costo.

```sql
DELIMITER $$

CREATE PROCEDURE sp_audit_ventas_agrupadas (
    IN p_fecha DATE,
    IN p_id_sucursal INT
)
BEGIN
    SELECT
        COALESCE(SUM(Unidades), 0)     AS TotalUnidades,
        COALESCE(SUM(VentaTotal), 0)   AS TotalVenta,
        COALESCE(SUM(CostoTotal), 0)   AS TotalCosto
    FROM VentasAgrupadas
    WHERE Fecha = p_fecha
      AND IdSucursal = p_id_sucursal;
END$$

DELIMITER ;
```

---

## 🔁 Query de UPSERT

**Nota:** Esta es la única operación que **NO** se ejecuta mediante stored procedure, ya que el bot maneja los datos en memoria antes de insertarlos.

```sql
INSERT INTO VentasAgrupadas (
    Fecha,
    IdSucursal,
    Upc,
    IdProveedor,
    IdDepartamento,
    IdCategoria,
    IdSubcategoria,
    Unidades,
    VentaTotal,
    CostoTotal,
    UltimaSync
)
VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW()
)
ON DUPLICATE KEY UPDATE
    IdProveedor    = VALUES(IdProveedor),
    IdDepartamento = VALUES(IdDepartamento),
    IdCategoria    = VALUES(IdCategoria),
    IdSubcategoria = VALUES(IdSubcategoria),
    Unidades       = VALUES(Unidades),
    VentaTotal     = VALUES(VentaTotal),
    CostoTotal     = VALUES(CostoTotal),
    UltimaSync     = NOW();
```

---

## 🤖 Flujo de Procesamiento del Bot

1. **Extracción:** Ejecuta `sp_select_ventas_diarias` en la base operativa (sucursal)
2. **Validación:** Mapea los datos al modelo `VentasAgrupadas` y valida campos
3. **UPSERT Local:** Inserta/actualiza datos en la base agregada local
4. **UPSERT VPS:** Inserta/actualiza datos en la base agregada de la VPS
5. **Auditoría:**
   - Ejecuta `sp_audit_operativa` en base operativa
   - Ejecuta `sp_audit_ventas_agrupadas` en base local
   - Ejecuta `sp_audit_ventas_agrupadas` en VPS
   - Compara totales (Unidades, Venta, Costo)
6. **Reproceso (si falla auditoría):**
   - Ejecuta `sp_delete_ventas_agrupadas` en local y VPS
   - Reintenta el proceso completo
7. **Bitácora:** Registra el resultado en `logs/bitacora_extraccion.csv`

---

## 📊 Bitácora de Procesamiento

El bot mantiene un archivo CSV con el historial de cada procesamiento:

**Archivo:** `logs/bitacora_extraccion.csv`

**Campos:**
- `fecha`: Fecha procesada
- `estado`: OK o ERROR
- `intentos`: Número de intentos necesarios
- `filas`: Cantidad de registros procesados
- `error`: Mensaje de error (si aplica)
- `fecha_registro`: Timestamp del registro

---

## ✅ Estado Final

- Modelo de datos cerrado
- Escalable a décadas mediante particionamiento
- Reportes rápidos por sucursal, producto y proveedor
- Sin dependencias operativas
- Operaciones críticas mediante stored procedures
- Auditoría automática y bitácora de procesamiento
- Listo para producción



