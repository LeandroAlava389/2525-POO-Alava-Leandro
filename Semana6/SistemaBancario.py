
# Clase base
class CuentaBancaria:
    def __init__(self, titular, numero_cuenta, saldo_inicial):
        self.titular = titular
        self.numero_cuenta = numero_cuenta
        self.__saldo = saldo_inicial  # Encapsulado
    
    def mostrar_info(self):
        print(f"Titular: {self.titular}")
        print(f"Número de Cuenta: {self.numero_cuenta}")
        print(f"Saldo: ${self.__saldo:.2f}")

    def obtener_saldo(self):
        return self.__saldo

    def depositar(self, monto):
        if monto > 0:
            self.__saldo += monto
            print(f"Depósito de ${monto:.2f} realizado.")
            print(f"Saldo actual: ${self.__saldo:.2f}")
        else:
            print("Monto inválido.")

    def retirar(self, monto):
        if monto <= self.__saldo:
            self.__saldo -= monto
            print(f"Retiro de ${monto:.2f} realizado.")
            print(f"Saldo actual: ${self.__saldo:.2f}")
        else:
            print("Fondos insuficientes.")
            print(f"Saldo disponible: ${self.__saldo:.2f}")


# Clase derivada: Cuenta de Ahorros
class CuentaAhorros(CuentaBancaria):
    def __init__(self, titular, numero_cuenta, saldo_inicial, tasa_interes):
        super().__init__(titular, numero_cuenta, saldo_inicial)
        self.tasa_interes = tasa_interes

    def retirar(self, monto):
        print("Cuenta Ahorros:")
        super().retirar(monto)


# Clase derivada: Cuenta Corriente
class CuentaCorriente(CuentaBancaria):
    def __init__(self, titular, numero_cuenta, saldo_inicial, limite_sobregiro):
        super().__init__(titular, numero_cuenta, saldo_inicial)
        self.limite_sobregiro = limite_sobregiro
    # Sobrescribe el método retirar para permitir sobregiro
    def retirar(self, monto):
        print("Cuenta Corriente:")
        saldo_disponible = self.obtener_saldo() + self.limite_sobregiro
        if monto <= saldo_disponible:
            # Acceso forzado al atributo privado (solo dentro de la clase)
            self._CuentaBancaria__saldo -= monto
            print(f"Retiro de ${monto:.2f} Realizado con sobregiro.")
            print(f"Saldo actual: ${self._CuentaBancaria__saldo:.2f}")
        else:
            print("Supera el límite de sobregiro permitido.")
            print(f"Saldo disponible con sobregiro: ${saldo_disponible:.2f}")


# Demostración
if __name__ == "__main__":
    cuenta1 = CuentaAhorros("Leandro Alava", "1864 7498 9669 3158", 685, 100)
    cuenta1.mostrar_info()
    cuenta1.depositar(350)
    cuenta1.retirar(325)
    print()

    cuenta2 = CuentaCorriente("Juan Alvarez", "1799 5487 8956 5666", 200, 360)
    cuenta2.mostrar_info()
    cuenta2.retirar(400)  # Usa parte del sobregiro
    print()

    cuenta2 = CuentaCorriente("Andrea Coronel", "7895 4795 5477 6214", 120, 20)
    cuenta2.mostrar_info()
    cuenta2.retirar(200)  # Usa parte del sobregiro
    print()

