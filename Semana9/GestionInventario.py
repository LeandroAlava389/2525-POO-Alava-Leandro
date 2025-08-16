from typing import Any, List, Optional

# Clases (Estructura de datos + validaciones)

class Producto:
    def __init__(self, id_: int, nombre: str, cantidad: int, precio: float) -> None:
        self._id = None
        self._nombre = None
        self._cantidad = None
        self._precio = None
        # Inicialización usando setters para validar
        self.id = id_
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    # id 
    @property
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("El ID debe ser un entero.")
        if value < 0:
            raise ValueError("El ID no puede ser negativo.")
        self._id = value

    # nombre
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: Any) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("El nombre debe ser una cadena no vacía.")
        self._nombre = value.strip()

    # cantidad 
    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("La cantidad debe ser un entero.")
        if value < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        self._cantidad = value

    # precio 
    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, value: Any) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise TypeError("El precio debe ser numérico (float).")
        if value < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = value

    def __repr__(self) -> str:
        return f"Producto(id={self.id}, nombre='{self.nombre}', cantidad={self.cantidad}, precio={self.precio:.2f})"


class Inventario:
    def __init__(self) -> None:
        self._productos: List[Producto] = []  # Colección principal (lista)

    @property
    def productos(self) -> List[Producto]:
        # devolvemos copia para evitar modificaciones externas directas
        return list(self._productos)

    def anadir_producto(self, producto: Producto) -> bool:
        """Añade si el ID es único. Devuelve True si se añadió."""
        if any(p.id == producto.id for p in self._productos):
            return False
        self._productos.append(producto)
        return True

    def eliminar_por_id(self, id_: int) -> bool:
        """Elimina por ID. Devuelve True si se eliminó."""
        for i, p in enumerate(self._productos):
            if p.id == id_:
                del self._productos[i]
                return True
        return False

    def actualizar_por_id(self, id_: int, *, cantidad: Optional[int] = None, precio: Optional[float] = None) -> bool:
        """Actualiza cantidad y/o precio por ID. Devuelve True si se actualizó."""
        for p in self._productos:
            if p.id == id_:
                if cantidad is not None:
                    p.cantidad = cantidad
                if precio is not None:
                    p.precio = precio
                return True
        return False

    def buscar_por_nombre(self, termino: str) -> List[Producto]:
        """Búsqueda parcial (case-insensitive)."""
        termino = termino.strip().lower()
        return [p for p in self._productos if termino in p.nombre.lower()]

    def mostrar_todos(self) -> List[Producto]:
        return list(self._productos)

# Interfaz de usuario por consola (CLI)

def leer_entero(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Entrada inválida: introduce un número entero.")


def leer_flotante(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Entrada inválida: introduce un número (puede tener decimales).")


def imprimir_tabla(productos: List[Producto]) -> None:
    if not productos:
        print("(No hay productos)")
        return
    headers = ["ID", "Nombre", "Cantidad", "Precio"]
    filas = [[str(p.id), p.nombre, str(p.cantidad), f"{p.precio:.2f}"] for p in productos]
    anchos = [max(len(h), *(len(f[i]) for f in filas)) for i, h in enumerate(headers)]

    def fmt_row(vals):
        return " | ".join(val.ljust(anchos[i]) for i, val in enumerate(vals))

    sep = "-+-".join("-" * w for w in anchos)
    print(fmt_row(headers))
    print(sep)
    for fila in filas:
        print(fmt_row(fila))


def menu():
    inventario = Inventario()
    opciones = {
        "1": "Añadir producto",
        "2": "Eliminar producto por ID",
        "3": "Actualizar cantidad/precio por ID",
        "4": "Buscar producto(s) por nombre",
        "5": "Mostrar todos los productos",
        "0": "Salir",
    }

    while True:
        print("\n=== Sistema de Gestión de Inventarios ===")
        for k in sorted(opciones.keys()):
            print(f"{k}. {opciones[k]}")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            try:
                id_ = leer_entero("ID (entero y único): ")
                nombre = input("Nombre: ").strip()
                cantidad = leer_entero("Cantidad: ")
                precio = leer_flotante("Precio: ")
                producto = Producto(id_, nombre, cantidad, precio)
                if inventario.anadir_producto(producto):
                    print("Producto añadido correctamente.")
                else:
                    print("No se pudo añadir: ya existe un producto con ese ID.")
            except Exception as e:
                print(f"Error al crear el producto: {e}")

        elif opcion == "2":
            id_ = leer_entero("ID del producto a eliminar: ")
            if inventario.eliminar_por_id(id_):
                print("Producto eliminado.")
            else:
                print("No existe un producto con ese ID.")

        elif opcion == "3":
            id_ = leer_entero("ID del producto a actualizar: ")
            actualizar_cantidad = input("¿Actualizar cantidad? (s/n): ").strip().lower() == "s"
            cantidad: Optional[int] = None
            precio: Optional[float] = None
            if actualizar_cantidad:
                cantidad = leer_entero("Nueva cantidad: ")
            actualizar_precio = input("¿Actualizar precio? (s/n): ").strip().lower() == "s"
            if actualizar_precio:
                precio = leer_flotante("Nuevo precio: ")
            ok = inventario.actualizar_por_id(id_, cantidad=cantidad, precio=precio)
            print("✔ Producto actualizado." if ok else " No existe un producto con ese ID.")

        elif opcion == "4":
            termino = input("Nombre o parte del nombre a buscar: ").strip()
            resultados = inventario.buscar_por_nombre(termino)
            print(f"Resultados para '{termino}':")
            imprimir_tabla(resultados)

        elif opcion == "5":
            imprimir_tabla(inventario.mostrar_todos())

        elif opcion == "0":
            print("Adiós.")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()
