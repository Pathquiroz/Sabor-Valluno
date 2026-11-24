from productos import Producto, Plato, Bebida, Combo
from pagos import Pago, Efectivo, Qr, Tarjeta
from clientes import Cliente
from pedidos import Pedido, Local, Llevar, Delivery
from restaurante import Restaurante


def ejecutar_pruebas():
    # 1. Abstracción: no se pueden instanciar clases abstractas
    cliente_test = Cliente("Juan Perez", "71234567")
    for clase_abs, args in [
        (Producto, ("X", 10.0)),
        (Pedido, (1, cliente_test, "lunes")),
        (Pago, (10.0, "Efectivo")),
    ]:
        try:
            clase_abs(*args)
            assert False, f"{clase_abs.__name__} no debería instanciarse"
        except TypeError:
            pass

    # 2. Encapsulación y validaciones de Cliente (Regla 8)
    try:
        Cliente("Ana", "51234567")  # No empieza con 6 o 7
        assert False
    except ValueError:
        pass

    try:
        Cliente("Ana", "71234")  # Menos de 8 dígitos
        assert False
    except ValueError:
        pass

    # 3. Caso de referencia Variante A: Silpancho (35) + Mocochinchi vaso (6) = 41 * 0.90 = 36.90
    silpancho = Plato("Silpancho", 35.0)
    mocochinchi = Bebida("Mocochinchi", 6.0, "vaso")
    combo_ref = Combo("Combo Referencia", [silpancho, mocochinchi])
    assert combo_ref.calcular_precio() == 36.90

    # 2 combos por delivery a Quillacollo: 73.80 + 15 = 88.80
    ped_deliv = Delivery(1, cliente_test, "quillacollo", "Av. Blanco Galindo km 12", "lunes")
    ped_deliv.agregar_producto(combo_ref, 2)
    assert ped_deliv.calcular_subtotal() == 73.80
    assert ped_deliv.calcular_cargo() == 15.0
    assert ped_deliv.calcular_total() == 88.80

    # 4. Combo que contiene otro combo (polimorfismo recursivo y conteo de platos)
    pique = Plato("Pique Macho", 60.0)
    jarra = Bebida("Chicha", 10.0, "jarra")  # 10 * 3 = 30.0
    assert jarra.calcular_precio() == 30.0
    combo_grande = Combo("Combo Familiar", [combo_ref, pique, jarra])
    # (36.90 + 60.0 + 30.0) = 126.90 -> -10% = 114.21
    assert combo_grande.calcular_precio() == 114.21
    assert combo_grande.contar_platos() == 2  # 1 silpancho dentro de combo_ref + 1 pique

    # 5. Protección contra autorreferencia en Combo
    try:
        combo_ref.agregar_producto(combo_ref)
        assert False
    except ValueError:
        pass

    # 6. Variante A: Chicharrón solo los domingos (también afecta a combos que lo contienen)
    chicharron = Plato("Chicharron", 55.0, ["domingo"])
    combo_dom = Combo("Combo Domingo", [chicharron, mocochinchi])
    assert combo_dom.esta_disponible("lunes") is False
    assert combo_dom.esta_disponible("domingo") is True

    # 7. Para llevar: Bs 2 por cada plato, incluidos platos dentro de combos
    ped_llevar = Llevar(2, cliente_test, "domingo")
    ped_llevar.agregar_producto(combo_grande, 1)  # tiene 2 platos
    ped_llevar.agregar_producto(chicharron, 1)    # tiene 1 plato
    assert ped_llevar.contar_platos() == 3
    assert ped_llevar.calcular_cargo() == 6.0

    # 8. Delivery Variante A: pedido mínimo Bs 40 y envío gratis en Cercado desde Bs 150
    ped_cercado = Delivery(3, cliente_test, "cercado", "Plaza Colon", "lunes")
    ped_cercado.agregar_producto(silpancho, 1)  # Bs 35 < 40
    try:
        ped_cercado.calcular_total()
        assert False
    except ValueError:
        pass

    ped_cercado.agregar_producto(pique, 2)  # 35 + 120 = 155 >= 150 -> envío gratis
    assert ped_cercado.calcular_cargo() == 0.0
    assert ped_cercado.calcular_total() == 155.0

    # 9. Estados del pedido y encapsulación de ítems
    ped_local = Local(4, cliente_test, 5, "lunes")
    ped_local.agregar_producto(silpancho, 1)
    ped_local.cambiar_estado("EN_PREPARACION")
    try:
        ped_local.agregar_producto(mocochinchi, 1)  # No se puede editar fuera de REGISTRADO
        assert False
    except ValueError:
        pass
    try:
        ped_local.cancelar_pedido()  # Solo se cancela desde REGISTRADO
        assert False
    except ValueError:
        pass

    # 10. Métodos de pago: Efectivo, QR (10 dígitos), Tarjeta (3% comisión, prohibido en Delivery)
    pago_ef = Efectivo(50.0)
    cobrado = ped_local.registrar_pago(pago_ef)
    assert cobrado == 35.0
    assert pago_ef.cambio == 15.0

    try:
        ped_deliv.registrar_pago(Tarjeta(100.0))  # Delivery no acepta tarjeta
        assert False
    except ValueError:
        pass

    pago_qr = Qr(88.80, "1234567890")
    assert ped_deliv.registrar_pago(pago_qr) == 88.80

    # 11. Gestor Restaurante: mesa ocupada no permite dos pedidos abiertos
    rest = Restaurante()
    rest.crear_pedido_local(cliente_test, 10, "lunes")
    try:
        rest.crear_pedido_local(cliente_test, 10, "lunes")
        assert False
    except ValueError:
        pass

    print("Todas las 11 pruebas de la Variante A pasaron exitosamente.")


if __name__ == "__main__":
    ejecutar_pruebas()