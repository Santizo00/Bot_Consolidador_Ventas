-- delete_ventas.sql
-- Limpieza idempotente de ventas agregadas
-- Se ejecuta antes del UPSERT para reprocesar el día completo

DELETE FROM VentasAgrupadas
WHERE Fecha = CURDATE()
  AND IdSucursal = ?;
