-- Auditoría en ventasagrupadas (local / VPS)

SELECT
    COUNT(*)        AS TotalFilas,
    SUM(Unidades)   AS TotalUnidades,
    SUM(VentaTotal) AS TotalVenta,
    SUM(CostoTotal) AS TotalCosto
FROM ventasagrupadas
WHERE Fecha = %s
  AND IdSucursal = %s;
