from abc import ABC, abstractmethod


class Producto(ABC):
    def __init__(self, nombre, precio, cantidad=1):
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if valor <= 0:
            raise ValueError("El precio del producto debe ser mayor que cero.")
        self._precio = round(float(valor), 2)

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if not isinstance(valor, int) or valor < 1:
            raise ValueError("La cantidad debe ser un entero positivo.")
        self._cantidad = valor

    @abstractmethod
    def calcular_precio(self):
        pass

    @abstractmethod
    def esta_disponible(self, dia):
        pass

    @abstractmethod
    def contar_platos(self):
        pass

    def __str__(self):
        return f"{self._nombre} - Bs {self.calcular_precio():.2f}"


class Plato(Producto):
    DIAS_VALIDOS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")

    def __init__(self, nombre, precio, dias_disponibles=None):
        super().__init__(nombre, precio)
        if dias_disponibles is None:
            self._dias_disponibles = list(self.DIAS_VALIDOS)
        else:
            self._dias_disponibles = [d.strip().lower() for d in dias_disponibles]

    @property
    def dias_disponibles(self):
        return list(self._dias_disponibles)

    def obtener_disponibilidad(self, dia):
        return dia.strip().lower() in self._dias_disponibles

    def calcular_precio(self):
        return self._precio

    def esta_disponible(self, dia):
        return self.obtener_disponibilidad(dia)

    def contar_platos(self):
        return 1


class Bebida(Producto):
    def __init__(self, nombre, precio_vaso, tipo="vaso"):
        super().__init__(nombre, precio_vaso)
        self.tipo = tipo

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        t = valor.strip().lower()
        if t not in ("vaso", "jarra"):
            raise ValueError("El tipo de bebida debe ser 'vaso' o 'jarra'.")
        self._tipo = t

    def calcular_precio(self):
        if self._tipo == "jarra":
            return round(self._precio * 3, 2)
        return self._precio

    def esta_disponible(self, dia):
        return True

    def contar_platos(self):
        return 0


class ComboProductos:
    def __init__(self, combo, producto):
        if combo is producto:
            raise ValueError("Un combo no puede contenerse a sí mismo.")
        self._combo = combo
        self._producto = producto

    @property
    def combo(self):
        return self._combo

    @property
    def producto(self):
        return self._producto


class Combo(Producto):
    DESCUENTO_VARIANTE_A = 0.10

    def __init__(self, nombre, productos):
        if len(productos) < 2:
            raise ValueError("Un combo debe contener al menos 2 productos.")
        self._items_combo = []
        super().__init__(nombre, 1.0)
        for prod in productos:
            self.agregar_producto(prod)
        self._precio = self.calcular_precio()

    def _contiene_combo(self, objetivo):
        for rel in self._items_combo:
            prod = rel.producto
            if prod is objetivo:
                return True
            if isinstance(prod, Combo) and prod._contiene_combo(objetivo):
                return True
        return False

    def agregar_producto(self, producto):
        if producto is self:
            raise ValueError("Un combo no puede contenerse a sí mismo.")
        if isinstance(producto, Combo) and producto._contiene_combo(self):
            raise ValueError("Referencia circular: el subcombo ya contiene a este combo.")
        self._items_combo.append(ComboProductos(self, producto))

    @property
    def productos(self):
        return [rel.producto for rel in self._items_combo]

    def calcular_descuento(self):
        suma = sum(rel.producto.calcular_precio() for rel in self._items_combo)
        return round(suma * self.DESCUENTO_VARIANTE_A, 2)

    def calcular_precio(self):
        suma = sum(rel.producto.calcular_precio() for rel in self._items_combo)
        return round(suma - self.calcular_descuento(), 2)

    def esta_disponible(self, dia):
        return all(rel.producto.esta_disponible(dia) for rel in self._items_combo)

    def contar_platos(self):
        return sum(rel.producto.contar_platos() for rel in self._items_combo)