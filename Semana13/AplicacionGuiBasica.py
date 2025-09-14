"""
Aplicación GUI básica con 

- El botón "Limpiar" es contextual: si hay filas seleccionadas en la tabla, las borra; si no, limpia el Entry. Esto interpreta el requisito "borre la información ingresada o seleccionada".
- Atajos de teclado para accesibilidad y pruebas rápidas.
- Separación ligera de responsabilidades: métodos por acción y utilitarios (update_status).
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional


class App(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Gestor Visual de Datos")
        self.minsize(680, 460)

        # Contador incremental simple para asignar IDs
        self._next_id: int = 1

        # Configurar rejilla principal para que la tabla expanda
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)  # La fila 2 (tabla) crece

        self._build_style()
        self._build_widgets()
        self._bind_events()
        self.update_status("Listo.")

    # Construcción de UI 
    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))
        style.configure("Danger.TButton", foreground="#391F75")

    def _build_widgets(self) -> None:
        # TopBar: título
        top = ttk.Frame(self, padding=(12, 10))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ttk.Label(
            top,
            text="Gestor de Datos",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        # InputBar: etiqueta + entry + botón Agregar
        input_bar = ttk.Frame(self, padding=(12, 0))
        input_bar.grid(row=1, column=0, sticky="ew")
        input_bar.columnconfigure(1, weight=1)

        ttk.Label(input_bar, text="Nuevo dato:").grid(row=0, column=0, padx=(0, 6), pady=10, sticky="w")

        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(input_bar, textvariable=self.entry_var)
        self.entry.grid(row=0, column=1, padx=(0, 6), pady=10, sticky="ew")
        self.entry.focus_set()

        self.btn_add = ttk.Button(input_bar, text="Agregar", command=self.add_item)
        self.btn_add.grid(row=0, column=2, pady=10)

        # DataTable: Treeview con scrollbar
        table_wrap = ttk.Frame(self, padding=(12, 0))
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("id", "texto")
        self.tree = ttk.Treeview(
            table_wrap,
            columns=columns,
            show="headings",
            selectmode="extended",  # permitir múltiples selecciones
            height=10,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configurar cabeceras y anchos
        self.tree.heading("id", text="ID")
        self.tree.heading("texto", text="Texto")
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("texto", width=480, anchor="w")

        # Scrollbar vertical
        vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        # ActionsBar: botones de acciones
        actions = ttk.Frame(self, padding=(12, 10))
        actions.grid(row=3, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)

        self.btn_clean = ttk.Button(actions, text="Limpiar", command=self.smart_clean)
        self.btn_clean.grid(row=0, column=0, sticky="w")

        self.btn_delete = ttk.Button(actions, text="Eliminar seleccionados", command=self.delete_selected)
        self.btn_delete.grid(row=0, column=1, padx=(8, 0), sticky="w")

        self.btn_clear_all = ttk.Button(actions, text="Limpiar todo", command=self.clear_all)
        self.btn_clear_all.grid(row=0, column=2, padx=(8, 0), sticky="w")

        self.btn_exit = ttk.Button(actions, text="Salir", command=self.on_quit)
        self.btn_exit.grid(row=0, column=3, padx=(8, 0), sticky="w")

        # StatusBar
        status = ttk.Frame(self, padding=(12, 0))
        status.grid(row=4, column=0, sticky="ew")
        status.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="0 elementos")
        ttk.Label(status, textvariable=self.status_var, style="Status.TLabel").grid(row=0, column=0, sticky="w")

    def _bind_events(self) -> None:
        # Enter para agregar
        self.bind("<Return>", self.add_item)
        # Supr/BackSpace para eliminar selección
        self.tree.bind("<Delete>", self.delete_selected)
        # Ctrl+L para acción Limpiar contextual
        self.bind("<Control-l>", self.smart_clean)

    # Lógica de acciones 
    def add_item(self, event: Optional[tk.Event] = None) -> None:
        """Agregar el texto del Entry a la tabla."""
        text = self.entry_var.get().strip()
        if not text:
            self._beep()
            self.update_status("Nada que agregar: el campo está vacío.")
            return
        # Insertar en Treeview
        iid = self._next_id
        self.tree.insert("", "end", values=(iid, text))
        self._next_id += 1
        # Limpiar Entry y actualizar estado
        self.entry_var.set("")
        self.update_status(f"Agregado ID {iid}.")

    def smart_clean(self, event: Optional[tk.Event] = None) -> None:
        """Acción para el botón "Limpiar":
        - Si hay selección en la tabla: elimina las filas seleccionadas.
        - Si no hay selección y el Entry tiene texto: limpia el Entry.
        - Si no hay nada que limpiar: informa en status.
        """
        selected = self.tree.selection()
        if selected:
            for item in selected:
                self.tree.delete(item)
            self.update_status(f"Eliminadas {len(selected)} fila(s) seleccionada(s).")
            return
        if self.entry_var.get():
            self.entry_var.set("")
            self.update_status("Campo de texto limpiado.")
            return
        self.update_status("No hay selección ni texto para limpiar.")
        self._beep()

    def delete_selected(self, event: Optional[tk.Event] = None) -> None:
        selected = self.tree.selection()
        if not selected:
            self.update_status("No hay selección para eliminar.")
            self._beep()
            return
        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar {len(selected)} fila(s) seleccionada(s)?"):
            for item in selected:
                self.tree.delete(item)
            self.update_status(f"Eliminadas {len(selected)} fila(s).")

    def clear_all(self) -> None:
        children = self.tree.get_children()
        if not children:
            self.update_status("La tabla ya está vacía.")
            self._beep()
            return
        if messagebox.askyesno("Confirmar limpieza total", "¿Eliminar todas las filas de la tabla?"):
            for item in children:
                self.tree.delete(item)
            self.update_status("Tabla vaciada.")

    # Utilitarios 
    def update_status(self, msg: str) -> None:
        count = len(self.tree.get_children())
        self.status_var.set(f"{count} elemento(s) · {msg}")

    def on_quit(self) -> None:
        self.destroy()

    def _beep(self) -> None:
        # Sonido visual: parpadeo del título para feedback sin audio
        original = self.cget("title")
        self.title("· · ·")
        self.after(120, lambda: self.title(original))


if __name__ == "__main__":
    app = App()
    app.mainloop()
