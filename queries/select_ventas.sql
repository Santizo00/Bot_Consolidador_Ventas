-- select_ventas.sql
-- Consulta de agregación diaria de ventas con resolución de proveedor
-- Se ejecuta SOLO en la sucursal (base operativa)

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
