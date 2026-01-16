-- Auditoría en base operativa (ventasdiarias)

SELECT
    COUNT(*)        AS TotalFilas,
    SUM(Cantidad)   AS TotalUnidades,
    SUM(MontoTotal) AS TotalVenta,
    SUM(CostoTotal) AS TotalCosto
FROM ventasdiarias
WHERE DATE(Fecha) = %s
  AND IdSucursales = %s;
