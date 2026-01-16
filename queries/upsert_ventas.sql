-- upsert_ventas.sql
-- Inserción / actualización idempotente en VentasAgrupadas

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
