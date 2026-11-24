from restaurante import Restaurante
from productos import Plato, Bebida, Combo
from pagos import Efectivo, Qr, Tarjeta


def mostrar_detalle_pedido(pedido):
    print("\n" + "=" * 45)
    print(f"PEDIDO #{pedido.numero_pedido} | Tipo: {type(pedido).__name__} | Día: {pedido.dia.capitalize()}")
    print(f"Cliente: {pedido.cliente} | Estado: {pedido.estado}")
    print("-" * 45)
    if not pedido.items:
        print("  (Sin productos agregados)")
    else:
        for item in pedido.items:
            print(
                f"  - {item.producto.nombre} x{item.cantidad} "
                f"(Bs {item.producto.calcular_precio():.2f} c/u) = Bs {item.subtotal_item():.2f}"
            )
    print("-" * 45)
    subtotal = pedido.calcular_subtotal()
    cargo = pedido.calcular_cargo()
    print(f"Subtotal: Bs {subtotal:.2f}")
    print(f"Cargos (envases/envío): Bs {cargo:.2f}")
    try:
        total = pedido.calcular_total()
        print(f"TOTAL A PAGAR: Bs {total:.2f}")
    except ValueError as e:
        print(f"Aviso: {e}")
    print("=" * 45)


def menu_principal():
    sistema = Restaurante()
    dia_actual = "lunes"

    while True:
        print(f"\n=== SABOR VALLUNO (Día activo: {dia_actual.capitalize()}) ===")
        print("1. Cambiar día de atención")
        print("2. Ver menú disponible del día")
        print("3. Registrar nuevo producto o combo")
        print("4. Registrar cliente")
        print("5. Crear nuevo pedido (Local / Llevar / Delivery)")
        print("6. Agregar o quitar productos de un pedido")
        print("7. Ver detalle de un pedido")
        print("8. Cambiar estado de un pedido")
        print("9. Cobrar pedido")
        print("10. Ver reporte de ventas del día")
        print("0. Salir")

        opcion = input("Seleccione una opción: ").strip()

        try:
            if opcion == "1":
                nuevo_dia = input("Ingrese el día (lunes a domingo): ").strip().lower()
                if nuevo_dia not in ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"):
                    print("Día no válido.")
                else:
                    dia_actual = nuevo_dia
                    print(f"Día actualizado a {dia_actual.capitalize()}.")

            elif opcion == "2":
                disponibles = sistema.listar_menu_disponible(dia_actual)
                print(f"\n--- Menú disponible ({dia_actual.capitalize()}) ---")
                for prod in disponibles:
                    print(f"  * {prod}")

            elif opcion == "3":
                tipo = input("Tipo (1=Plato, 2=Bebida, 3=Combo): ").strip()
                nombre = input("Nombre: ").strip()
                if tipo == "1":
                    precio = float(input("Precio (Bs): "))
                    dias_txt = input("Días disponibles separados por coma (Enter = todos): ").strip()
                    dias = [d.strip() for d in dias_txt.split(",")] if dias_txt else None
                    sistema.registrar_producto(Plato(nombre, precio, dias))
                    print("Plato registrado.")
                elif tipo == "2":
                    precio_vaso = float(input("Precio por vaso (Bs): "))
                    presentacion = input("Presentación (vaso/jarra): ").strip().lower()
                    sistema.registrar_producto(Bebida(nombre, precio_vaso, presentacion))
                    print("Bebida registrada.")
                elif tipo == "3":
                    nombres_txt = input("Nombres de productos incluidos (separados por coma): ").strip()
                    lista_prods = [sistema.buscar_producto(n) for n in nombres_txt.split(",")]
                    sistema.registrar_producto(Combo(nombre, lista_prods))
                    print("Combo registrado con 10% de descuento.")

            elif opcion == "4":
                nombre = input("Nombre del cliente: ")
                telefono = input("Teléfono (8 dígitos, empieza con 6 o 7): ")
                cli = sistema.registrar_cliente(nombre, telefono)
                print(f"Cliente registrado: {cli}")

            elif opcion == "5":
                tel = input("Teléfono del cliente: ")
                cli = sistema.buscar_cliente(tel)
                tipo_ped = input("Tipo de pedido (1=Local, 2=Llevar, 3=Delivery): ").strip()
                if tipo_ped == "1":
                    mesa = int(input("Número de mesa (1-15): "))
                    ped = sistema.crear_pedido_local(cli, mesa, dia_actual)
                elif tipo_ped == "2":
                    ped = sistema.crear_pedido_llevar(cli, dia_actual)
                elif tipo_ped == "3":
                    zona = input("Zona (cercado, quillacollo, sacaba, vinto): ")
                    direccion = input("Dirección exacta: ")
                    ped = sistema.crear_pedido_delivery(cli, zona, direccion, dia_actual)
                else:
                    print("Tipo de pedido inválido.")
                    continue
                print(f"Pedido #{ped.numero_pedido} creado en estado {ped.estado}.")

            elif opcion == "6":
                num = int(input("Número de pedido: "))
                ped = sistema.buscar_pedido(num)
                accion = input("¿Desea (A)gregar o (Q)uitar producto?: ").strip().upper()
                if accion == "A":
                    nom_prod = input("Nombre del producto: ")
                    cant = int(input("Cantidad (1-20): "))
                    prod = sistema.buscar_producto(nom_prod)
                    ped.agregar_producto(prod, cant)
                    print("Producto agregado.")
                elif accion == "Q":
                    nom_prod = input("Nombre del producto a quitar: ")
                    ped.quitar_producto(nom_prod)
                    print("Producto quitado.")

            elif opcion == "7":
                num = int(input("Número de pedido: "))
                ped = sistema.buscar_pedido(num)
                mostrar_detalle_pedido(ped)

            elif opcion == "8":
                num = int(input("Número de pedido: "))
                ped = sistema.buscar_pedido(num)
                print(f"Estado actual: {ped.estado}")
                nuevo_est = input("Nuevo estado (EN_PREPARACION, LISTO, ENTREGADO, CANCELADO): ")
                ped.cambiar_estado(nuevo_est)
                print(f"Estado actualizado a {ped.estado}.")

            elif opcion == "9":
                num = int(input("Número de pedido: "))
                ped = sistema.buscar_pedido(num)
                mostrar_detalle_pedido(ped)
                total = ped.calcular_total()
                metodo = input("Método de pago (1=Efectivo, 2=QR, 3=Tarjeta): ").strip()
                if metodo == "1":
                    recibido = float(input("Monto recibido en efectivo (Bs): "))
                    pago = Efectivo(recibido)
                    cobrado = ped.registrar_pago(pago)
                    print(f"Pago exitoso: Bs {cobrado:.2f} | Cambio: Bs {pago.cambio:.2f}")
                elif metodo == "2":
                    codigo = input("Código de transferencia QR (10 dígitos): ")
                    pago = Qr(total, codigo)
                    cobrado = ped.registrar_pago(pago)
                    print(f"Pago QR exitoso por Bs {cobrado:.2f} (Cod: {pago.codigo_transferencia})")
                elif metodo == "3":
                    con_comision = round(total * 1.03, 2)
                    print(f"Total con 3% de comisión por tarjeta: Bs {con_comision:.2f}")
                    pago = Tarjeta(con_comision)
                    cobrado = ped.registrar_pago(pago)
                    print(f"Pago con tarjeta aprobado por Bs {cobrado:.2f}")

            elif opcion == "10":
                totales, top_3 = sistema.reporte_ventas_dia(dia_actual)
                print(f"\n--- Reporte de Ventas ({dia_actual.capitalize()}) ---")
                for tipo, monto in totales.items():
                    print(f"  {tipo}: Bs {monto:.2f}")
                print("Top 3 productos más vendidos:")
                for nom, cant in top_3:
                    print(f"  * {nom}: {cant} unidades")

            elif opcion == "0":
                print("Saliendo del sistema Sabor Valluno...")
                break

            else:
                print("Opción no válida.")

        except ValueError as err:
            print(f"[Error de validación]: {err}")
        except Exception as err:
            print(f"[Error]: {err}")


if __name__ == "__main__":
    menu_principal()