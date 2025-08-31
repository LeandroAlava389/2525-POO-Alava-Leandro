from typing import Any, List, Optional
import os
import tempfile

# Formato
DELIM = "|"

#  Clases 
class Producto:
    def __init__(self, id_: int, nombre: str, cantidad: int, precio: float) -> None:
        self._id = None
        self._nombre = None
        self._cantidad = None
        self._precio = None
        self.id = id_
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

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

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: Any) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("El nombre debe ser una cadena no vacía.")
        self._nombre = value.strip()

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

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, value: Any) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise TypeError("El precio debe ser numérico.")
        if value < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = value

    def __repr__(self) -> str:
        return f"Producto(id={self.id}, nombre='{self.nombre}', cantidad={self.cantidad}, precio={self.precio:.2f})"

    def a_linea(self) -> str:
        return f"{self.id}{DELIM}{self.nombre}{DELIM}{self.cantidad}{DELIM}{self.precio}\n"

    @staticmethod
    def desde_linea(linea: str) -> "Producto":
        partes = [p.strip() for p in linea.rstrip("\n").split(DELIM)]
        if len(partes) != 4:
            raise ValueError("Número de columnas inválido.")
        id_str, nombre, cant_str, precio_str = partes
        id_ = int(id_str)
        cantidad = int(cant_str)
        precio = float(precio_str)
        return Producto(id_, nombre, cantidad, precio)


class Inventario:
    def __init__(self, ruta_archivo: str = "inventario.txt") -> None:
        self._productos: List[Producto] = []
        self.ruta_archivo = ruta_archivo
        self._asegurar_archivo()
        self._cargar_desde_archivo()

    @property
    def productos(self) -> List[Producto]:
        return list(self._productos)

    def _asegurar_archivo(self) -> None:
        if not os.path.exists(self.ruta_archivo):
            try:
                with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                    f.write("")
            except PermissionError:
                print(f"Sin permisos para crear '{self.ruta_archivo}'. "
                      "Se trabajará solo en memoria y no se guardará en disco.")
            except OSError as e:
                print(f"No se pudo crear '{self.ruta_archivo}': {e}. "
                      "Se trabajará solo en memoria.")

    def _cargar_desde_archivo(self) -> None:
        if not os.path.exists(self.ruta_archivo):
            return
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                for idx, linea in enumerate(f, start=1):
                    if not linea.strip():
                        continue
                    try:
                        p = Producto.desde_linea(linea)
                        self._reemplazar_o_agregar(p)
                    except Exception as e:
                        print(f"Línea {idx} corrupta en '{self.ruta_archivo}': {e}. Saltada.")
        except PermissionError:
            print(f"Sin permisos de lectura para '{self.ruta_archivo}'. "
                  "Se continuará con inventario en memoria.")
        except OSError as e:
            print(f"Error leyendo '{self.ruta_archivo}': {e}. "
                  "Se continuará con inventario en memoria.")

    def _guardar_atomico(self) -> None:
        directorio = os.path.dirname(self.ruta_archivo) or "."
        try:
            fd, ruta_tmp = tempfile.mkstemp(prefix=".inv_", dir=directorio, text=True)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                    for p in self._productos:
                        tmp.write(p.a_linea())
                os.replace(ruta_tmp, self.ruta_archivo)
            except Exception:
                try:
                    os.remove(ruta_tmp)
                except Exception:
                    pass
                raise
        except PermissionError:
            raise PermissionError("Sin permisos de escritura en la carpeta/archivo de inventario.")
        except OSError as e:
            raise OSError(f"Fallo de E/S al guardar el inventario: {e}")

    def _reemplazar_o_agregar(self, producto: Producto) -> None:
        for i, p in enumerate(self._productos):
            if p.id == producto.id:
                self._productos[i] = producto
                return
        self._productos.append(producto)

    def anadir_producto(self, producto: Producto) -> bool:
        if any(p.id == producto.id for p in self._productos):
            return False
        self._productos.append(producto)
        try:
            self._guardar_atomico()
            return True
        except Exception as e:
            self._productos.pop()
            raise e

    def eliminar_por_id(self, id_: int) -> bool:
        for i, p in enumerate(self._productos):
            if p.id == id_:
                backup = self._productos[i]
                del self._productos[i]
                try:
                    self._guardar_atomico()
                    return True
                except Exception as e:
                    self._productos.insert(i, backup)
                    raise e
        return False

    def actualizar_por_id(self, id_: int, *, cantidad: Optional[int] = None, precio: Optional[float] = None) -> bool:
        for i, p in enumerate(self._productos):
            if p.id == id_:
                prev = Producto(p.id, p.nombre, p.cantidad, p.precio)
                try:
                    if cantidad is not None:
                        p.cantidad = cantidad
                    if precio is not None:
                        p.precio = precio
                    self._guardar_atomico()
                    return True
                except Exception as e:
                    self._productos[i] = prev
                    raise e
        return False

    def buscar_por_nombre(self, termino: str) -> List[Producto]:
        termino = termino.strip().lower()
        return [p for p in self._productos if termino in p.nombre.lower()]

    def mostrar_todos(self) -> List[Producto]:
        return list(self._productos)


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
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta = "Semana9-10"

    target_dir = base_dir if os.path.basename(base_dir) == carpeta else os.path.join(base_dir, carpeta)

    # Asegura que la carpeta exista
    os.makedirs(target_dir, exist_ok=True)

    ruta = os.path.join(target_dir, "inventario.txt")
    inventario = Inventario(ruta)
   

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
                    print("Producto añadido y guardado en archivo.")
                else:
                    print("Ya existe un producto con ese ID. No se añadió.")
            except PermissionError as e:
                print(f"Error permisos al guardar: {e}")
            except OSError as e:
                print(f"Error E/S al guardar: {e}")
            except Exception as e:
                print(f"Error al crear/validar el producto: {e}")

        elif opcion == "2":
            try:
                id_ = leer_entero("ID del producto a eliminar: ")
                if inventario.eliminar_por_id(id_):
                    print("Producto eliminado y archivo actualizado.")
                else:
                    print("No existe un producto con ese ID.")
            except PermissionError as e:
                print(f"Error permisos al guardar: {e}")
            except OSError as e:
                print(f"Error E/S al guardar: {e}")

        elif opcion == "3":
            try:
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
                if ok:
                    print("Producto actualizado y guardado en archivo.")
                else:
                    print(" No existe un producto con ese ID.")
            except (TypeError, ValueError) as ve:
                print(f"Error datos inválidos: {ve}")
            except PermissionError as e:
                print(f"Error permisos al guardar: {e}")
            except OSError as e:
                print(f"Error E/S al guardar: {e}")

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
