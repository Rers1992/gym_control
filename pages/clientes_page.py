import flet as ft
from database import (
    obtener_clientes, crear_cliente, actualizar_cliente, eliminar_cliente,
    buscar_clientes, rut_existe
)
from models import Cliente, validar_rut, formatear_rut
from ui import (
    BORDER, DANGER, INFO, INFO_SOFT, PRIMARY, SUCCESS, SUCCESS_SOFT, SURFACE,
    TEXT, TEXT_MUTED, CARD_SHADOW, empty_state, page_header, show_snack,
    status_badge,
)


def clientes_page(page: ft.Page):
    search_field = ft.TextField(
        hint_text="Buscar por nombre, RUT, teléfono o email...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        border_radius=12,
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
                empty_state(
                    ft.Icons.PERSON_SEARCH,
                    "No encontramos clientes",
                    "Registra un cliente nuevo o prueba con otra búsqueda.",
                )
            )
        else:
            for c in clientes:
                initials = "".join(part[0] for part in c.nombre.split()[:2]).upper() or "CL"
                clientes_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(initials, color=INFO, weight=ft.FontWeight.W_700, size=13),
                                width=44,
                                height=44,
                                bgcolor=INFO_SOFT,
                                border_radius=22,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column([
                                ft.Text(c.nombre, weight=ft.FontWeight.W_600, size=15, color=TEXT),
                                ft.Text(
                                    f"RUT {formatear_rut(c.rut)}  ·  {c.telefono or 'Sin teléfono'}  ·  {c.email or 'Sin email'}",
                                    size=11,
                                    color=TEXT_MUTED,
                                ),
                                ft.Text(f"Registro: {c.fecha_registro.strftime('%d/%m/%Y')}", size=10, color=TEXT_MUTED),
                            ], spacing=2, expand=True),
                            status_badge(
                                "Activo" if c.activo else "Inactivo",
                                SUCCESS if c.activo else DANGER,
                                SUCCESS_SOFT if c.activo else "#FEEDEC",
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
                                    icon_color=DANGER,
                                    on_click=lambda e, cliente=c: confirm_delete(cliente),
                                ),
                            ]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15,
                        bgcolor=SURFACE,
                        border=ft.Border.all(1, BORDER),
                        border_radius=12,
                        shadow=CARD_SHADOW,
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
                show_snack(page, "El nombre es obligatorio", DANGER)
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
            show_snack(page, "Cliente creado exitosamente", SUCCESS)
            page.update()
            page.pop_dialog()

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
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def show_edit_dialog(cliente):
        rut_display = ft.Text(f"RUT: {formatear_rut(cliente.rut)}", size=14, color=ft.Colors.GREY_600)
        nombre_field = ft.TextField(label="Nombre", value=cliente.nombre, expand=True)
        telefono_field = ft.TextField(label="Telefono", value=cliente.telefono, expand=True, keyboard_type=ft.KeyboardType.NUMBER)
        email_field = ft.TextField(label="Email", value=cliente.email, expand=True, keyboard_type=ft.KeyboardType.EMAIL)
        activo_switch = ft.Switch(label="Activo", value=cliente.activo)

        def save(e):
            if not nombre_field.value:
                show_snack(page, "El nombre es obligatorio", DANGER)
                page.update()
                return

            actualizar_cliente(cliente.rut, {
                "nombre": nombre_field.value,
                "telefono": telefono_field.value,
                "email": email_field.value,
                "activo": activo_switch.value,
            })
            load_clientes()
            show_snack(page, "Cliente actualizado", SUCCESS)
            page.update()
            page.pop_dialog()

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
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def confirm_delete(cliente):
        def delete(e):
            eliminar_cliente(cliente.id)
            load_clientes()
            show_snack(page, "Cliente eliminado", SUCCESS)
            page.update()
            page.pop_dialog()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminacion"),
            content=ft.Text(f"¿Estas seguro de eliminar a {cliente.nombre}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Eliminar", on_click=delete, bgcolor=ft.Colors.RED),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(confirm_dialog)

    def on_search_change(e):
        load_clientes(e.control.value)

    search_field.on_change = on_search_change

    def init():
        load_clientes()
        page.update()

    return (ft.Column([
        page_header(
            "Clientes",
            "Administra los datos y el estado de tus clientes.",
            ft.FilledButton(
                "Nuevo Cliente",
                icon=ft.Icons.ADD,
                on_click=lambda e: show_add_dialog(),
            ),
        ),
        search_field,
        clientes_list,
    ], expand=True, spacing=16), init)
