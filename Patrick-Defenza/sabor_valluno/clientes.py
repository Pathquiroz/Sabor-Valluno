class Cliente:
    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre del cliente es obligatorio.")
        self._nombre = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El teléfono del cliente es obligatorio.")
        tel = valor.strip()
        if len(tel) != 8 or not tel.isdigit() or tel[0] not in ("6", "7"):
            raise ValueError("El teléfono debe tener 8 dígitos y empezar con 6 o 7.")
        self._telefono = tel

    def __str__(self):
        return f"{self._nombre} (Tel: {self._telefono})"