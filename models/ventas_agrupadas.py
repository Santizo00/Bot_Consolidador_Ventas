from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class VentasAgrupadas:
    """
    Modelo de datos para la tabla VentasAgrupadas.
    Representa ventas agregadas por día, sucursal y producto (UPC).
    """

    fecha: date
    id_sucursal: int
    upc: str

    id_proveedor: int
    id_departamento: int
    id_categoria: int
    id_subcategoria: int

    unidades: int
    venta_total: float
    costo_total: float

    ultima_sync: datetime | None = None

    def to_tuple_for_upsert(self) -> tuple:
        """
        Devuelve los valores en el orden esperado por el UPSERT SQL.
        (No incluye UltimaSync porque se maneja con NOW() en la query)
        """
        return (
            self.fecha,
            self.id_sucursal,
            self.upc,
            self.id_proveedor,
            self.id_departamento,
            self.id_categoria,
            self.id_subcategoria,
            self.unidades,
            self.venta_total,
            self.costo_total
        )

    @staticmethod
    def from_db_row(row: dict) -> "VentasAgrupadas":
        """
        Crea una instancia del modelo a partir de un row retornado
        por el SELECT agregado (dict o mapping).
        """
        return VentasAgrupadas(
            fecha=row["Fecha"],
            id_sucursal=row["IdSucursal"],
            upc=row["Upc"],

            id_proveedor=row["IdProveedor"],
            id_departamento=row["IdDepartamento"],
            id_categoria=row["IdCategoria"],
            id_subcategoria=row["IdSubcategoria"],

            unidades=row["Unidades"],
            venta_total=row["VentaTotal"],
            costo_total=row["CostoTotal"]
        )

    def validate(self) -> None:
        """
        Validaciones básicas de integridad antes de insertar.
        Lanza ValueError si algo no es válido.
        """
        if not self.upc:
            raise ValueError("UPC no puede ser vacío")

        if self.unidades < 0:
            raise ValueError("Unidades no puede ser negativo")

        if self.venta_total < 0:
            raise ValueError("VentaTotal no puede ser negativo")

        if self.costo_total < 0:
            raise ValueError("CostoTotal no puede ser negativo")

        if self.id_sucursal <= 0:
            raise ValueError("IdSucursal inválido")

        if self.id_proveedor is None or self.id_proveedor < 0:
            raise ValueError("IdProveedor inválido")