from clientes import Cliente
from productos import Plato, Bebida, Combo
from pedidos import Local, Llevar, Delivery


class Restaurante:
    def __init__(self, nombre="Sabor Valluno"):
        self._nombre = nombre
        self._menu = []
        self._clientes = {}
        self._pedidos = {}
        self._contador_pedidos = 1
        self._cargar_menu_inicial()

    @property
    def nombre(self):
        return self._nombre

    @property
    def menu(self):
        return list(self._menu)

    @property
    def clientes(self):
        return list(self._clientes.values())

    @property
    def pedidos(self):
        return list(self._pedidos.values())

    def _cargar_menu_inicial(self):
        # Platos típicos de Cochabamba (Variante A: Chicharrón solo domingos)
        silpancho = Plato("Silpancho", 35.0)
        pique = Plato("Pique Macho", 60.0)
        chicharron = Plato("Chicharron", 55.0, ["domingo"])
        sopa_mani = Plato("Sopa de Mani", 20.0)

        # Bebidas (precio por vaso; jarra = 3x)
        mocochinchi_vaso = Bebida("Mocochinchi Vaso", 6.0, "vaso")
        mocochinchi_jarra = Bebida("Mocochinchi Jarra", 6.0, "jarra")
        gaseosa = Bebida("Gaseosa Personal", 7.0, "vaso")

        # Combo ejemplo (10% de descuento en Variante A)
        combo_valluno = Combo("Combo Valluno", [silpancho, mocochinchi_vaso])

        for prod in (
            silpancho,
            pique,
            chicharron,
            sopa_mani,
            mocochinchi_vaso,
            mocochinchi_jarra,
            gaseosa,
            combo_valluno,
        ):
            self._menu.append(prod)

    def registrar_producto(self, producto):
        for p in self._menu:
            if p.nombre.lower() == producto.nombre.lower():
                raise ValueError(f"Ya existe un producto con el nombre '{producto.nombre}'.")
        self._menu.append(producto)

    def buscar_producto(self, nombre):
        for prod in self._menu:
            if prod.nombre.lower() == nombre.strip().lower():
                return prod
        raise ValueError(f"No se encontró el producto '{nombre}'.")

    def listar_menu_disponible(self, dia):
        return [prod for prod in self._menu if prod.esta_disponible(dia)]

    def registrar_cliente(self, nombre, telefono):
        if telefono.strip() in self._clientes:
            return self._clientes[telefono.strip()]
        cliente = Cliente(nombre, telefono)
        self._clientes[cliente.telefono] = cliente
        return cliente

    def buscar_cliente(self, telefono):
        tel = telefono.strip()
        if tel not in self._clientes:
            raise ValueError(f"No existe un cliente registrado con el teléfono {tel}.")
        return self._clientes[tel]

    def _verificar_mesa_disponible(self, n_mesa):
        for pedido in self._pedidos.values():
            if isinstance(pedido, Local) and pedido.n_mesa == n_mesa:
                if pedido.estado not in ("ENTREGADO", "CANCELADO"):
                    raise ValueError(f"La mesa {n_mesa} ya tiene un pedido abierto (#{pedido.numero_pedido}).")

    def crear_pedido_local(self, cliente, n_mesa, dia="lunes"):
        self._verificar_mesa_disponible(n_mesa)
        pedido = Local(self._contador_pedidos, cliente, n_mesa, dia)
        self._pedidos[pedido.numero_pedido] = pedido
        self._contador_pedidos += 1
        return pedido

    def crear_pedido_llevar(self, cliente, dia="lunes"):
        pedido = Llevar(self._contador_pedidos, cliente, dia)
        self._pedidos[pedido.numero_pedido] = pedido
        self._contador_pedidos += 1
        return pedido

    def crear_pedido_delivery(self, cliente, zona, direccion, dia="lunes"):
        pedido = Delivery(self._contador_pedidos, cliente, zona, direccion, dia)
        self._pedidos[pedido.numero_pedido] = pedido
        self._contador_pedidos += 1
        return pedido

    def buscar_pedido(self, numero_pedido):
        if numero_pedido not in self._pedidos:
            raise ValueError(f"No existe el pedido #{numero_pedido}.")
        return self._pedidos[numero_pedido]

    def reporte_ventas_dia(self, dia):
        dia_norm = dia.strip().lower()
        totales_tipo = {"Local": 0.0, "Llevar": 0.0, "Delivery": 0.0}
        conteo_productos = {}

        for pedido in self._pedidos.values():
            if pedido.dia == dia_norm and pedido.pago is not None and pedido.estado != "CANCELADO":
                tipo_nombre = type(pedido).__name__
                totales_tipo[tipo_nombre] = round(
                    totales_tipo.get(tipo_nombre, 0.0) + pedido.calcular_total(), 2
                )
                for item in pedido.items:
                    nombre_p = item.producto.nombre
                    conteo_productos[nombre_p] = conteo_productos.get(nombre_p, 0) + item.cantidad

        top_3 = sorted(conteo_productos.items(), key=lambda x: x[1], reverse=True)[:3]
        return totales_tipo, top_3