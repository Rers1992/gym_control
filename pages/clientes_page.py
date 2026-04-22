import flet as ft
from database import (
    obtener_clientes, crear_cliente, actualizar_cliente, eliminar_cliente,
    buscar_clientes, rut_existe
)
from models import Cliente, validar_rut, formatear_rut


def clientes_page(page: ft.Page):
    search_field = ft.TextField(
        label="Buscar cliente...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        on_submit=lambda e: load_clientes(),
    )

    clientes_list = ft.ListView(spacing=8, expand=True)

    def load_clientes(termino=""):
        clientes_list.controls.clear()
        if termino:
            clientes = buscar_clientes(termino)
        else:
            clientes = obtener_clientes()

        if not clientes:
            clientes_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_OFF, size=60, color=ft.Colors.GREY_400),
                        ft.Text("No hay clientes registrados", size=16, color=ft.Colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                )
            )
        else:
            for c in clientes:
                clientes_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE, size=30),
                            ft.Column([
                                ft.Text(f"{c.nombre} ({formatear_rut(c.rut)})", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Tel: {c.telefono} | Email: {c.email}", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"Registro: {c.fecha_registro.strftime('%d/%m/%Y')}", size=11, color=ft.Colors.GREY_500),
                            ], spacing=2, expand=True),
                            ft.Chip(
                                label=ft.Text("Activo" if c.activo else "Inactivo", size=12),
                                color=ft.Colors.GREEN if c.activo else ft.Colors.RED,
                            ),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, cliente=c: show_edit_dialog(cliente),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Eliminar",
                                    icon_color=ft.Colors.RED,
                                    on_click=lambda e, cliente=c: confirm_delete(cliente),
                                ),
                            ]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                    )
                )
        clientes_list.update()

    def show_add_dialog():
        rut_field = ft.TextField(label="RUT", hint_text="Ej: 12.345.678-5", expand=True)
        nombre_field = ft.TextField(label="Nombre", expand=True)
        telefono_field = ft.TextField(label="Telefono", expand=True, keyboard_type=ft.KeyboardType.PHONE, input_filter=ft.NumbersOnlyInputFilter())
        email_field = ft.TextField(label="Email", expand=True, keyboard_type=ft.KeyboardType.EMAIL)
        rut_error = ft.Text("", color=ft.Colors.RED, size=12, visible=False)

        def on_rut_change(e):
            raw = rut_field.value.replace(".", "").replace("-", "").replace(",", "").upper()
            formatted = formatear_rut(raw) if len(raw) >= 7 else raw
            rut_field.value = formatted
            rut_error.visible = False
            rut_field.error_text = ""
            rut_field.update()
            rut_error.update()

        def save(e):
            rut_raw = rut_field.value.replace(".", "").replace("-", "").upper()
            if not rut_raw or len(rut_raw) < 8:
                rut_error.value = "RUT inválido"
                rut_error.visible = True
                rut_error.update()
                return
            if not validar_rut(rut_field.value):
                rut_error.value = "RUT no es válido"
                rut_error.visible = True
                rut_error.update()
                return
            if rut_existe(rut_raw):
                rut_error.value = "Este RUT ya está registrado"
                rut_error.visible = True
                rut_error.update()
                return
            if not nombre_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("El nombre es obligatorio"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()
                return

            cliente = Cliente(
                rut=rut_raw,
                nombre=nombre_field.value,
                telefono=telefono_field.value,
                email=email_field.value,
            )
            crear_cliente(cliente)
            load_clientes()
            page.snack_bar = ft.SnackBar(ft.Text("Cliente creado exitosamente"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
            page.close(dialog)

        rut_field.on_change = on_rut_change

        dialog = ft.AlertDialog(
            title=ft.Text("Nuevo Cliente"),
            content=ft.Column([
                rut_field,
                rut_error,
                nombre_field,
                telefono_field,
                email_field,
            ], tight=True, spacing=8, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dialog)),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dialog)

    def show_edit_dialog(cliente):
        rut_display = ft.Text(f"RUT: {formatear_rut(cliente.rut)}", size=14, color=ft.Colors.GREY_600)
        nombre_field = ft.TextField(label="Nombre", value=cliente.nombre, expand=True)
        telefono_field = ft.TextField(label="Telefono", value=cliente.telefono, expand=True, keyboard_type=ft.KeyboardType.NUMBER)
        email_field = ft.TextField(label="Email", value=cliente.email, expand=True, keyboard_type=ft.KeyboardType.EMAIL)
        activo_switch = ft.Switch(label="Activo", value=cliente.activo)

        def save(e):
            if not nombre_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("El nombre es obligatorio"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()
                return

            actualizar_cliente(cliente.rut, {
                "nombre": nombre_field.value,
                "telefono": telefono_field.value,
                "email": email_field.value,
                "activo": activo_switch.value,
            })
            load_clientes()
            page.snack_bar = ft.SnackBar(ft.Text("Cliente actualizado"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
            page.close(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Cliente"),
            content=ft.Column([
                rut_display,
                nombre_field,
                telefono_field,
                email_field,
                activo_switch,
            ], tight=True, spacing=8, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dialog)),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dialog)

    def confirm_delete(cliente):
        def delete(e):
            eliminar_cliente(cliente.id)
            load_clientes()
            page.snack_bar = ft.SnackBar(ft.Text("Cliente eliminado"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
            page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminacion"),
            content=ft.Text(f"¿Estas seguro de eliminar a {cliente.nombre}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
                ft.FilledButton("Eliminar", on_click=delete, bgcolor=ft.Colors.RED),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(confirm_dialog)

    def on_search_change(e):
        load_clientes(e.control.value)

    search_field.on_change = on_search_change

    def init():
        load_clientes()
        page.update()

    return (ft.Column([
        ft.Row([
            ft.Text("Clientes", size=28, weight=ft.FontWeight.BOLD),
            ft.Container(width=20),
            ft.FilledButton(
                "Nuevo Cliente",
                icon=ft.Icons.ADD,
                on_click=lambda e: show_add_dialog(),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=10),
        search_field,
        ft.Container(height=10),
        clientes_list,
    ], expand=True, spacing=10), init)
