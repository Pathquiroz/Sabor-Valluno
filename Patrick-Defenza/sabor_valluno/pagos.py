from abc import ABC, abstractmethod


class Pago(ABC):
    def __init__(self, monto, tipo):
        if monto <= 0:
            raise ValueError("El monto del pago debe ser mayor que cero.")
        self._monto = round(float(monto), 2)
        self._tipo = tipo

    @property
    def monto(self):
        return self._monto

    @property
    def tipo(self):
        return self._tipo

    @abstractmethod
    def validar_pago(self, total_a_pagar):
        pass


class Efectivo(Pago):
    def __init__(self, monto_recibido):
        super().__init__(monto_recibido, "Efectivo")
        self._cambio = 0.0

    @property
    def cambio(self):
        return self._cambio

    def calcular_cambio(self, total_a_pagar):
        if self._monto < total_a_pagar:
            raise ValueError(
                f"Efectivo insuficiente: se recibió Bs {self._monto:.2f} y el total es Bs {total_a_pagar:.2f}."
            )
        self._cambio = round(self._monto - total_a_pagar, 2)
        return self._cambio

    def validar_pago(self, total_a_pagar):
        self.calcular_cambio(total_a_pagar)
        return round(total_a_pagar, 2)


class Qr(Pago):
    def __init__(self, monto, codigo_transferencia):
        super().__init__(monto, "QR")
        self.codigo_transferencia = codigo_transferencia

    @property
    def codigo_transferencia(self):
        return self._codigo_transferencia

    @codigo_transferencia.setter
    def codigo_transferencia(self, valor):
        cod = str(valor).strip()
        if len(cod) != 10 or not cod.isdigit():
            raise ValueError("El código de transferencia QR debe tener exactamente 10 dígitos.")
        self._codigo_transferencia = cod

    def validar_codigo(self):
        return len(self._codigo_transferencia) == 10 and self._codigo_transferencia.isdigit()

    def validar_pago(self, total_a_pagar):
        if not self.validar_codigo():
            raise ValueError("Código QR inválido.")
        if round(self._monto, 2) < round(total_a_pagar, 2):
            raise ValueError("El monto transferido por QR es menor al total del pedido.")
        return round(total_a_pagar, 2)


class Tarjeta(Pago):
    COMISION = 0.03

    def __init__(self, monto):
        super().__init__(monto, "Tarjeta")

    def calcular_comision(self, total_a_pagar):
        return round(total_a_pagar * self.COMISION, 2)

    def validar_pago(self, total_a_pagar):
        total_con_comision = round(total_a_pagar + self.calcular_comision(total_a_pagar), 2)
        if round(self._monto, 2) < total_con_comision:
            raise ValueError(
                f"Monto insuficiente en tarjeta (incluye 3% de comisión): Bs {total_con_comision:.2f}."
            )
        return total_con_comision