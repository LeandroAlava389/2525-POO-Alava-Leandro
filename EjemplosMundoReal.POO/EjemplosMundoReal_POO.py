# Clase para representar a un paciente
class Paciente:
    def __init__(self, nombre, edad, cedula):
        self.nombre = nombre
        self.edad = edad
        self.cedula = cedula
        self.historial = []  # Lista de citas

    def agregar_cita(self, cita):
        self.historial.append(cita)

    def mostrar_historial(self):
        print(f"\nHistorial de citas de {self.nombre}:")
        for cita in self.historial:
            print(f"- {cita}")

# Clase para representar a un médico
class Medico:
    def __init__(self, nombre, especialidad):
        self.nombre = nombre
        self.especialidad = especialidad
        self.citas = []  # Lista de citas del médico

    def asignar_cita(self, cita):
        self.citas.append(cita)

    def mostrar_citas(self):
        print(f"\nCitas del Dr. {self.nombre} ({self.especialidad}):")
        for cita in self.citas:
            print(f"- {cita}")

# Clase para representar una cita médica
class Cita:
    def __init__(self, fecha, motivo, paciente, medico):
        self.fecha = fecha
        self.motivo = motivo
        self.paciente = paciente
        self.medico = medico

    def __str__(self):
        return f"{self.fecha} | Motivo: {self.motivo} | Médico: {self.medico.nombre}"

# PRUEBA DEL SISTEMA 

# Crear pacientes
paciente1 = Paciente("Leandro Alava", 19, "0986532018")
paciente2 = Paciente("Juan Perez", 26, "0986325477")

# Crear médicos
medico1 = Medico("Pedro Lopez", "Alergologia")
medico2 = Medico("Juan Ramírez", "Medicina General")

# Crear citas
cita1 = Cita("2025-06-30", "Escalofrios", paciente1, medico2)
cita2 = Cita("2025-06-33", "Dolor de cadera", paciente2, medico2)
cita3 = Cita("2025-06-30", "Prueba de alergia", paciente1, medico1)

# Asignar citas a pacientes y médicos
paciente1.agregar_cita(cita1)
paciente1.agregar_cita(cita3)
paciente2.agregar_cita(cita2)

medico2.asignar_cita(cita1)
medico2.asignar_cita(cita2)
medico1.asignar_cita(cita3)

# Mostrar historiales y agendas
paciente1.mostrar_historial()
paciente2.mostrar_historial()
medico1.mostrar_citas()
medico2.mostrar_citas()
