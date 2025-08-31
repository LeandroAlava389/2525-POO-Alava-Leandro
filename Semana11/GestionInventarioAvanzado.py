from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import tempfile
from typing import Dict, List, Set, Tuple


#  Excepciones específicas

class InventarioError(Exception):
    """Errores de dominio del inventario."""

class ProductoYaExiste(InventarioError):
    pass

class ProductoNoExiste(InventarioError):
    pass

class ValorInvalido(InventarioError):
    pass


#  Modelo de dominio

@dataclass
class Producto:
    """
    Representa un producto del inventario.
    Atributos:
        id: int 
        nombre: str
        cantidad: int 
        precio: float 
    """
    id: int
    nombre: str
    cantidad: int
    precio: float

    # Validaciones de negocio
    def __post_init__(self):
        self.id = int(self.id)
        if self.id <= 0:
            raise ValorInvalido("El ID debe ser un entero positivo.")

        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise ValorInvalido("El nombre no puede estar vacío.")

        self.cantidad = int(self.cantidad)
        if self.cantidad < 0:
            raise ValorInvalido("La cantidad no puede ser negativa.")

        self.precio = float(self.precio)
        if self.precio < 0:
            raise ValorInvalido("El precio no puede ser negativo.")

    # Getters/Setters con validación (si tu profe pide métodos explícitos)
    def get_id(self) -> int:
        return self.id

    def get_nombre(self) -> str:
        return self.nombre

    def set_nombre(self, nuevo_nombre: str) -> None:
        nuevo_nombre = nuevo_nombre.strip()
        if not nuevo_nombre:
            raise ValorInvalido("El nombre no puede quedar vacío.")
        self.nombre = nuevo_nombre

    def get_cantidad(self) -> int:
        return self.cantidad

    def set_cantidad(self, nueva_cantidad: int) -> None:
        nueva_cantidad = int(nueva_cantidad)
        if nueva_cantidad < 0:
            raise ValorInvalido("La cantidad no puede ser negativa.")
        self.cantidad = nueva_cantidad

    def get_precio(self) -> float:
        return self.precio

    def set_precio(self, nuevo_precio: float) -> None:
        nuevo_precio = float(nuevo_precio)
        if nuevo_precio < 0:
            raise ValorInvalido("El precio no puede ser negativo.")
        self.precio = nuevo_precio

    # Serialización
    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Producto":
        return Producto(
            id=int(data["id"]),
            nombre=str(data["nombre"]),
            cantidad=int(data["cantidad"]),
            precio=float(data["precio"]),
        )


class Inventario:

    def __init__(self):
        self._items: Dict[int, Producto] = {}
        self._indice_nombres: Dict[str, Set[int]] = {}

    # ---- Operaciones de dominio ----
    def agregar(self, p: Producto) -> None:
        if p.id in self._items:
            raise ProductoYaExiste(f"Ya existe un producto con ID {p.id}.")
        self._items[p.id] = p
        self._idx_add(p)

    def eliminar(self, id_: int) -> None:
        id_ = int(id_)
        if id_ not in self._items:
            raise ProductoNoExiste(f"No existe el producto con ID {id_}.")
        p = self._items.pop(id_)
        self._idx_remove(p)

    def actualizar_cantidad(self, id_: int, nueva_cantidad: int) -> None:
        id_ = int(id_)
        if id_ not in self._items:
            raise ProductoNoExiste(f"No existe el producto con ID {id_}.")
        self._items[id_].set_cantidad(nueva_cantidad)

    def actualizar_precio(self, id_: int, nuevo_precio: float) -> None:
        id_ = int(id_)
        if id_ not in self._items:
            raise ProductoNoExiste(f"No existe el producto con ID {id_}.")
        self._items[id_].set_precio(nuevo_precio)

    def buscar_por_nombre(self, patron: str) -> List[Producto]:
        """
        Búsqueda por subcadena (case-insensitive). Complejidad O(n).
        """
        patron = patron.strip().lower()
        if not patron:
            return []
        resultado: List[Producto] = []
        for p in self._items.values():
            if patron in p.nombre.lower():
                resultado.append(p)
        return resultado

    def buscar_exactos(self, nombre_exact: str) -> List[Producto]:
        """
        Usa set para IDs de nombre exacto -> O(k).
        """
        key = nombre_exact.strip().lower()
        ids = self._indice_nombres.get(key, set())
        return [self._items[i] for i in ids]

    def listar_todos(self) -> List[Tuple[int, str, int, float]]:
        """
        Devuelve una lista de tuplas inmutables para presentar o exportar:
        (id, nombre, cantidad, precio)
        """
        filas = [(p.id, p.nombre, p.cantidad, p.precio) for p in self._items.values()]
        # Ordenar por ID para impresión estable
        return sorted(filas, key=lambda t: t[0])

    def bajo_stock(self, umbral: int = 5) -> Set[int]:
        """Conjunto de IDs con stock por debajo del umbral (ejemplo de uso de set)."""
        return {p.id for p in self._items.values() if p.cantidad < umbral}

    # Persistencia (archivos)
    @staticmethod
    def _atomic_write_json(path: Path, data: Dict) -> None:
        """
        Escritura atómica cross-platform:
        1) Escribe en un archivo temporal dentro del mismo directorio
        2) os.replace para mover sobre el archivo final
        Evita archivos corruptos si el programa se interrumpe a mitad.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        # NamedTemporaryFile en el MISMO directorio para que os.replace sea seguro en Windows
        with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            temp_name = tmp.name
        os.replace(temp_name, path)

    def guardar(self, path: Path) -> None:
        payload = {
            "version": 1,
            "productos": [p.to_dict() for p in self._items.values()],
        }
        self._atomic_write_json(path, payload)

    def cargar(self, path: Path) -> None:
        if not path.exists():
            # Inventario vacío si no hay archivo
            self._items.clear()
            self._indice_nombres.clear()
            return
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        productos = data.get("productos", [])
        self._items.clear()
        self._indice_nombres.clear()
        for d in productos:
            p = Producto.from_dict(d)
            self._items[p.id] = p
            self._idx_add(p)

    # Índices auxiliares
    def _idx_add(self, p: Producto) -> None:
        key = p.nombre.strip().lower()
        bucket = self._indice_nombres.setdefault(key, set())
        bucket.add(p.id)

    def _idx_remove(self, p: Producto) -> None:
        key = p.nombre.strip().lower()
        bucket = self._indice_nombres.get(key)
        if not bucket:
            return
        bucket.discard(p.id)
        if not bucket:
            self._indice_nombres.pop(key, None)


#  Interfaz de Usuario (CLI)

def _input_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg).strip())
        except ValueError:
            print("Ingresa un número entero válido.")


def _input_float(msg: str) -> float:
    while True:
        try:
            return float(input(msg).strip().replace(",", "."))
        except ValueError:
            print("Ingresa un número (usa punto para decimales).")


def _input_str(msg: str) -> str:
    s = input(msg).strip()
    while not s:
        print("No puede estar vacío.")
        s = input(msg).strip()
    return s


def mostrar_menu() -> None:
    print("\n=== SISTEMA DE GESTIÓN DE INVENTARIO ===")
    print("1) Añadir producto")
    print("2) Eliminar producto por ID")
    print("3) Actualizar CANTIDAD por ID")
    print("4) Actualizar PRECIO por ID")
    print("5) Buscar productos por nombre")
    print("6) Mostrar todos los productos")
    print("7) Mostrar IDs con bajo stock")
    print("8) Guardar inventario")
    print("9) Cargar inventario desde archivo")
    print("0) Salir (guarda automáticamente)\n")


def imprimir_tabla(filas: List[Tuple[int, str, int, float]]) -> None:
    if not filas:
        print("Inventario vacío.")
        return
    print(f"{'ID':>4}  {'NOMBRE':<30}  {'CANT':>5}  {'PRECIO($)':>10}")
    print("-" * 56)
    for id_, nombre, cant, precio in filas:
        print(f"{id_:>4}  {nombre:<30.30s}  {cant:>5}  {precio:>10.2f}")


def main():
    # Ruta de datos: ./data/inventario.json (junto al script)
    script_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    data_file = script_dir / "data" / "inventario.json"

    inv = Inventario()
    # Carga inicial (si el archivo existe)
    try:
        inv.cargar(data_file)
        print(f"Datos cargados desde: {data_file}")
    except Exception as e:
        print(f"No se pudo cargar el inventario: {e}")

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        try:
            if opcion == "1":
                id_ = _input_int("ID: ")
                nombre = _input_str("Nombre: ")
                cantidad = _input_int("Cantidad: ")
                precio = _input_float("Precio: ")
                inv.agregar(Producto(id_, nombre, cantidad, precio))
                inv.guardar(data_file)
                print("Producto añadido y guardado.")

            elif opcion == "2":
                id_ = _input_int("ID a eliminar: ")
                inv.eliminar(id_)
                inv.guardar(data_file)
                print("Producto eliminado y cambios guardados.")

            elif opcion == "3":
                id_ = _input_int("ID a actualizar cantidad: ")
                cantidad = _input_int("Nueva cantidad: ")
                inv.actualizar_cantidad(id_, cantidad)
                inv.guardar(data_file)
                print("Cantidad actualizada y guardada.")

            elif opcion == "4":
                id_ = _input_int("ID a actualizar precio: ")
                precio = _input_float("Nuevo precio: ")
                inv.actualizar_precio(id_, precio)
                inv.guardar(data_file)
                print("Precio actualizado y guardado.")

            elif opcion == "5":
                patron = _input_str("Nombre o parte del nombre a buscar: ")
                encontrados = inv.buscar_por_nombre(patron)
                filas = [(p.id, p.nombre, p.cantidad, p.precio) for p in encontrados]
                imprimir_tabla(sorted(filas, key=lambda t: t[0]))

            elif opcion == "6":
                imprimir_tabla(inv.listar_todos())

            elif opcion == "7":
                umbral = _input_int("Cantidad para bajo stock: ")
                ids = inv.bajo_stock(umbral)
                if not ids:
                    print("No hay productos con bajo stock.")
                else:
                    print(f"IDs con bajo stock (< {umbral}): {sorted(list(ids))}")

            elif opcion == "8":
                inv.guardar(data_file)
                print(f"Guardado manual en: {data_file}")

            elif opcion == "9":
                inv.cargar(data_file)
                print(f"Cargado desde: {data_file}")

            elif opcion == "0":
                inv.guardar(data_file)
                print("Saliendo. Inventario guardado.")
                break

            else:
                print("Opción inválida. Intenta de nuevo.")

        except InventarioError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()
