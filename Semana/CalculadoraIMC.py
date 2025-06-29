# Calculadora del Indice de masa Corporal (IMC)

# Función para calcular el IMC
def calcular_imc(peso, altura):
    return peso / (altura ** 2)

# Entrada de datos: input para obtener nombre, peso y altura
nombre = input("Ingrese su nombre: ")
peso = float(input("Ingrese peso en kilogramos: "))
altura = float(input("Ingrese altura en metros: "))

# Proceso: calcular el IMC y determinar si hay sobrepeso
imc = calcular_imc(peso, altura)
sobrepeso = imc > 25

# Salida: mostrar el IMC y si hay sobrepeso
print(f"{nombre}, tu IMC es: {imc:.2f}")
if sobrepeso:
    print("Tienes sobrepeso.")
else:
    print("Estás dentro del rango saludable.")

