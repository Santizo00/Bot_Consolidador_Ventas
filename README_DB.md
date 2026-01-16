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
    Fecha DATE NOT NULL,
    IdSucursal INT NOT NULL,
    Upc VARCHAR(20) NOT NULL,

    IdProveedor INT NOT NULL,
    IdDepartamento INT NOT NULL,
    IdCategoria INT NOT NULL,
    IdSubcategoria INT NOT NULL,

    Unidades INT NOT NULL,
    VentaTotal DECIMAL(14,2) NOT NULL,
    CostoTotal DECIMAL(14,2) NOT NULL,

    UltimaSync DATETIME NOT NULL,

    PRIMARY KEY (Fecha, IdSucursal, Upc),

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


### Agregar mas particiones (Anual)
```sql
ALTER TABLE VentasAgrupadas
ADD PARTITION (
    PARTITION p2027 VALUES LESS THAN (2028)
);
```
---

## 🔍 Query de Selección / Agregación (Sucursal)

```sql
SELECT
    DATE(v.Fecha)              AS Fecha,
    v.IdSucursales             AS IdSucursal,
    v.Upc                      AS Upc,

    p.IdProveedor              AS IdProveedor,
    v.IdDepartamentos          AS IdDepartamento,
    v.IdCategorias             AS IdCategoria,
    v.IdSubcategorias          AS IdSubcategoria,

    SUM(v.Cantidad)            AS Unidades,
    SUM(v.MontoTotal)          AS VentaTotal,
    SUM(v.CostoTotal)          AS CostoTotal
FROM ventasdiarias v
INNER JOIN productos p
    ON p.Upc = v.Upc
WHERE DATE(v.Fecha) = CURDATE()
GROUP BY
    DATE(v.Fecha),
    v.IdSucursales,
    v.Upc,
    p.IdProveedor,
    v.IdDepartamentos,
    v.IdCategorias,
    v.IdSubcategorias;
```

**Por qué es así**
- El join se hace solo en la sucursal
- Se evita recalcular proveedor en la web
- Se optimizan reportes históricos

---

## 🗑️ Query de Limpieza (Idempotencia)

```sql
DELETE FROM VentasAgrupadas
WHERE Fecha = CURDATE()
  AND IdSucursal = ?;
```

Permite reprocesar el día completo sin duplicados.

---

## 🔁 Query de UPSERT

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

## 🤖 Uso por el Bot

Flujo resumido:

1. Ejecuta SELECT agregado
2. DELETE del día actual
3. UPSERT en base local
4. UPSERT en VPS
5. Auditoría (sumas y conteos)
6. Finaliza o reprocesa

El bot controla:
- integridad
- consistencia
- reintentos
- particiones futuras

---

## ✅ Estado Final

- Modelo de datos cerrado
- Escalable a décadas
- Reportes rápidos por sucursal, producto y proveedor
- Sin dependencias operativas
- Listo para implementación del bot y la web
