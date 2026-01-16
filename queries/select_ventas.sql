SELECT DATE(v.fecha) AS fecha,
       p.upc AS upc,
       p.proveedor_id AS proveedor_id,
       p.departamento_id AS departamento_id,
       p.categoria_id AS categoria_id,
       p.subcategoria_id AS subcategoria_id,
       SUM(v.cantidad) AS cantidad,
       SUM(v.total) AS total
FROM ventasdiarias v
JOIN productos p ON p.id = v.producto_id
WHERE DATE(v.fecha) = %s
GROUP BY DATE(v.fecha), p.upc, p.proveedor_id, p.departamento_id, p.categoria_id, p.subcategoria_id;
