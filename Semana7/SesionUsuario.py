import time

class Impresora:
    def __init__(self, marca):
        """
        Constructor que se ejecuta al crear el objeto Impresora.
        Inicializa la impresora y la enciende.
        """
        self.marca = marca
        self.encendida = True
        print(f"[ENCENDIDA] Impresora {self.marca} está ahora encendida.")

    def imprimir(self, documento):
        """
        Método que simula la impresión de un documento.
        """
        if self.encendida:
            print(f"Imprimiendo documento: '{documento}'...")
            time.sleep(2)  # Simula tiempo de impresión
            print("Documento impreso correctamente.\n")
        else:
            print("Error: La impresora está apagada.")

    def __del__(self):
        """
        Destructor que se ejecuta cuando el objeto se destruye.
        Apaga la impresora automáticamente.
        """
        self.encendida = False
        print(f"[APAGADA] Impresora {self.marca} ha sido apagada correctamente.")

# -------------------------------
# Simulación del uso del programa
# -------------------------------

# Crear un objeto de la clase Impresora
mi_impresora = Impresora("Epson L1250")

# Simular impresión de documentos
mi_impresora.imprimir("Doc1.docx")
mi_impresora.imprimir("Doc2.docx")

# Eliminar el objeto (opcional, también se destruye al final del programa)
del mi_impresora
