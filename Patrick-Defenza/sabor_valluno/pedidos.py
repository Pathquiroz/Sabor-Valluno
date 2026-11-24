from abc import ABC, abstractmethod
from modelo.clientes import Cliente
from modelo.productos import Producto
from modelo.pagos import Pago, Tarjeta


class PedidoProducto:
    def __init__(self, pedido, producto, cantidad):
        self._pedido = pedido
        self._producto = producto
        self.cantidad = cantidad

    @property
    def pedido(self):
        return self._pedido

    @property
    def producto(self):
        return self._producto

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if not isinstance(valor, int) or not (1 <= valor <= 20):
            raise ValueError("La cantidad de un producto en el pedido debe estar entre 1 y 20.")
        self._cantidad = valor

    def subtotal_item(self):
        return round(self._producto.calcular_precio() * self._cantidad, 2)


class Pedido(ABC):
    TRANSICIONES_VALIDAS = {
        "REGISTRADO": ("EN_PREPARACION", "CANCELADO"),
        "EN_PREPARACION": ("LISTO",),
        "LISTO": ("ENTREGADO",),
        "ENTREGADO": (),
        "CANCELADO": (),
    }

    def __init__(self, numero_pedido, cliente, dia="lunes"):
        self._numero_pedido = numero_pedido
        self._cliente = cliente
        self._dia = dia.strip().lower()
        self._estado = "REGISTRADO"
        self._pago = None
        self._items = []

    @property
    def numero_pedido(self):
        return self._numero_pedido

    @property
    def cliente(self):
        return self._cliente

    @property
    def dia(self):
        return self._dia

    @property
    def estado(self):
        return self._estado

    @property
    def pago(self):
        return self._pago

    @property
    def items(self):
        return list(self._items)

    def _verificar_editable(self):
        if self._estado != "REGISTRADO":
            raise ValueError(
                f"No se pueden modificar productos cuando el pedido está en estado '{self._estado}'."
            )

    def agregar_producto(self, producto, cantidad=1):
        self._verificar_editable()
        if not producto.esta_disponible(self._dia):
            raise ValueError(f"El producto '{producto.nombre}' no está disponible el día {self._dia}.")
        for item in self._items:
            if item.producto is producto:
                item.cantidad = item.cantidad + cantidad
                return
        self._items.append(PedidoProducto(self, producto, cantidad))

    def quitar_producto(self, nombre_producto):
        self._verificar_editable()
        for i, item in enumerate(self._items):
            if item.producto.nombre.lower() == nombre_producto.strip().lower():
                self._items.pop(i)
                return
        raise ValueError(f"El producto '{nombre_producto}' no está en el pedido.")

    def cambiar_estado(self, nuevo_estado):
        destino = nuevo_estado.strip().upper()
        permitidos = self.TRANSICIONES_VALIDAS.get(self._estado, ())
        if destino not in permitidos:
            raise ValueError(f"Transición de estado inválida: {self._estado} -> {destino}.")
        self._estado = destino

    def cancelar_pedido(self):
        self.cambiar_estado("CANCELADO")

    def calcular_subtotal(self):
        return round(sum(item.subtotal_item() for item in self._items), 2)

    def contar_platos(self):
        return sum(item.producto.contar_platos() * item.cantidad for item in self._items)

    @abstractmethod
    def calcular_cargo(self):
        pass

    def calcular_total(self):
        return round(self.calcular_subtotal() + self.calcular_cargo(), 2)

    def registrar_pago(self, pago):
        if not self._items:
            raise ValueError("No se puede cobrar un pedido sin productos.")
        if self._estado == "CANCELADO":
            raise ValueError("No se puede cobrar un pedido cancelado.")
        total_cobrado = pago.validar_pago(self.calcular_total())
        self._pago = pago
        return total_cobrado


class Local(Pedido):
    def __init__(self, numero_pedido, cliente, n_mesa, dia="lunes"):
        super().__init__(numero_pedido, cliente, dia)
        self.n_mesa = n_mesa

    @property
    def n_mesa(self):
        return self._n_mesa

    @n_mesa.setter
    def n_mesa(self, valor):
        if not isinstance(valor, int) or not (1 <= valor <= 15):
            raise ValueError("El número de mesa debe estar entre 1 y 15.")
        self._n_mesa = valor

    def calcular_cargo(self):
        return 0.0


class Llevar(Pedido):
    COSTO_ENVASE_PLATO = 2.0

    def __init__(self, numero_pedido, cliente, dia="lunes"):
        super().__init__(numero_pedido, cliente, dia)

    def calcular_cargo(self):
        return round(self.contar_platos() * self.COSTO_ENVASE_PLATO, 2)


class Delivery(Pedido):
    TARIFAS_ZONA = {
        "cercado": 8.0,
        "quillacollo": 15.0,
        "sacaba": 15.0,
        "vinto": 20.0,
    }
    PEDIDO_MINIMO = 40.0
    ENVIO_GRATIS_CERCADO_DESDE = 150.0

    def __init__(self, numero_pedido, cliente, zona, direccion, dia="lunes"):
        super().__init__(numero_pedido, cliente, dia)
        self.zona = zona
        self.direccion = direccion

    @property
    def zona(self):
        return self._zona

    @zona.setter
    def zona(self, valor):
        z = valor.strip().lower()
        if z not in self.TARIFAS_ZONA:
            raise ValueError(f"Zona no válida. Opciones: {', '.join(self.TARIFAS_ZONA.keys())}.")
        self._zona = z

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        if not valor or not valor.strip():
            raise ValueError("La dirección de entrega es obligatoria para delivery.")
        self._direccion = valor.strip()

    def calcular_cargo(self):
        subtotal = self.calcular_subtotal()
        if self._zona == "cercado" and subtotal >= self.ENVIO_GRATIS_CERCADO_DESDE:
            return 0.0
        return self.TARIFAS_ZONA[self._zona]

    def calcular_total(self):
        subtotal = self.calcular_subtotal()
        if subtotal < self.PEDIDO_MINIMO:
            raise ValueError(
                f"El pedido mínimo para delivery es Bs {self.PEDIDO_MINIMO:.2f} (subtotal actual: Bs {subtotal:.2f})."
            )
        return round(subtotal + self.calcular_cargo(), 2)

    def registrar_pago(self, pago):
        if isinstance(pago, Tarjeta):
            raise ValueError("Los pedidos por delivery solo aceptan pago en Efectivo o QR.")
        return super().registrar_pago(pago)