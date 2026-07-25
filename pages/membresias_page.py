import flet as ft
from datetime import datetime, timedelta
from database import (
    obtener_clientes, obtener_membresias, crear_membresia, actualizar_membresia,
    eliminar_membresia, obtener_cliente,
    obtener_tipos_membresia, obtener_tipo_membresia, crear_tipo_membresia, actualizar_tipo_membresia,
    eliminar_tipo_membresia
)
from models import Membresia, TipoMembresia
from settings_db import get_setting
from ui import (
    BORDER, DANGER, DANGER_SOFT, PRIMARY, PRIMARY_SOFT, SUCCESS, SUCCESS_SOFT,
    SURFACE, TEXT, TEXT_MUTED, WARNING, WARNING_SOFT, CARD_SHADOW,
    empty_state, page_header, show_snack, status_badge,
)


def membresias_page(page: ft.Page):
    filter_dropdown = ft.Dropdown(
        label="Filtrar por estado",
        width=220,
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        border_radius=10,
        options=[
            ft.dropdown.Option("todas", "Todas"),
            ft.dropdown.Option("activas", "Activas"),
            ft.dropdown.Option("vencidas", "Vencidas"),
            ft.dropdown.Option("por_vencer", "Por Vencer"),
        ],
        value="todas",
    )

    membresias_list = ft.ListView(spacing=8, expand=True)
    tipos_list = ft.ListView(spacing=8, expand=True)

    btn_tipos = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CREDIT_CARD, size=18, color=PRIMARY),
            ft.Text("Tipos de membresía", size=13, weight=ft.FontWeight.W_600, color=TEXT),
        ], spacing=7),
        padding=ft.Padding.symmetric(horizontal=16, vertical=11),
        bgcolor=PRIMARY_SOFT,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        ink=True,
    )
    btn_asignaciones = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ASSIGNMENT_IND, size=18, color=PRIMARY),
            ft.Text("Asignaciones", size=13, weight=ft.FontWeight.W_600, color=TEXT),
        ], spacing=7),
        padding=ft.Padding.symmetric(horizontal=16, vertical=11),
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        ink=True,
    )

    tipos_content = ft.Column([
        page_header(
            "Tipos de membresía",
            "Define los planes, su duración y precio base.",
            ft.FilledButton(
                "Nuevo Tipo",
                icon=ft.Icons.ADD,
                on_click=lambda e: show_add_tipo_dialog(),
            ),
        ),
        tipos_list,
    ], expand=True, spacing=16)

    asignaciones_content = ft.Column([
        page_header(
            "Asignaciones",
            "Revisa y administra los planes asociados a clientes.",
            ft.FilledButton(
                "Asignar Membresía",
                icon=ft.Icons.ADD,
                on_click=lambda e: show_add_dialog(),
            ),
        ),
        ft.Row([filter_dropdown], alignment=ft.MainAxisAlignment.START),
        membresias_list,
    ], expand=True, spacing=16)

    content_container = ft.Container(expand=True)

    def show_tipos(e=None):
        btn_tipos.bgcolor = PRIMARY_SOFT
        btn_asignaciones.bgcolor = SURFACE
        content_container.content = tipos_content
        load_tipos()
        page.update()

    def show_asignaciones(e=None):
        btn_tipos.bgcolor = SURFACE
        btn_asignaciones.bgcolor = PRIMARY_SOFT
        content_container.content = asignaciones_content
        load_membresias()
        page.update()

    btn_tipos.on_click = show_tipos
    btn_asignaciones.on_click = show_asignaciones

    def get_tipo_color(nombre):
        colores = {
            "mensual": ft.Colors.BLUE,
            "anual": ft.Colors.PURPLE,
            "clase": ft.Colors.ORANGE,
            "minero": ft.Colors.GREEN,
            "completo": ft.Colors.TEAL,
        }
        for key, color in colores.items():
            if key in nombre.lower():
                return color
        return ft.Colors.GREY

    def load_tipos():
        tipos_list.controls.clear()
        tipos = obtener_tipos_membresia()

        for t in tipos:
            color = get_tipo_color(t.nombre)
            dias_text = f"{t.duracion_dias} días" if t.duracion_dias > 0 else "Ilimitado"

            tipos_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(t.nombre[:3].upper(), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=color,
                                padding=8,
                                border_radius=8,
                            ),
                            ft.Column([
                                ft.Text(t.nombre, weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Duración: {dias_text}", size=12, color=ft.Colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.Container(
                                content=ft.Text(f"${t.precio_base:,.0f}", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.GREEN),
                                padding=10,
                            ),
                        ]),
                        ft.Row([
                            ft.Text(t.descripcion if t.descripcion else "Sin descripción", size=12, color=ft.Colors.GREY_500, expand=True),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, tipo=t: show_edit_tipo_dialog(tipo),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Eliminar",
                                    icon_color=ft.Colors.RED,
                                    on_click=lambda e, tipo=t: confirm_delete_tipo(tipo),
                                ),
                            ]),
                        ]),
                    ], spacing=8),
                    padding=15,
                    bgcolor=SURFACE,
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    shadow=CARD_SHADOW,
                )
            )

        if not tipos_list.controls:
            tipos_list.controls.append(
                empty_state(
                    ft.Icons.CREDIT_CARD,
                    "No hay tipos de membresía",
                    "Crea tu primer plan para comenzar a asignarlo.",
                )
            )

        page.update()

    def show_add_tipo_dialog():
        nombre_field = ft.TextField(label="Nombre", expand=True)
        duracion_field = ft.TextField(label="Duración (días)", value="30", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        precio_field = ft.TextField(label="Precio ($)", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        descripcion_field = ft.TextField(label="Descripción", expand=True, multiline=True, min_lines=2)

        def save(e):
            if not nombre_field.value or not precio_field.value:
                show_snack(page, "Nombre y precio son obligatorios", DANGER)
                page.update()
                return

            try:
                duracion = int(duracion_field.value) if duracion_field.value else 30
            except ValueError:
                duracion = 30

            try:
                precio = float(precio_field.value.replace(",", ""))
            except ValueError:
                precio = 0

            tipo = TipoMembresia(
                nombre=nombre_field.value,
                duracion_dias=duracion,
                precio_base=precio,
                descripcion=descripcion_field.value,
            )
            crear_tipo_membresia(tipo)
            load_tipos()
            show_snack(page, "Tipo de membresía creado", SUCCESS)
            page.update()
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("Nuevo Tipo de Membresía"),
            content=ft.Column([
                nombre_field,
                ft.Row([duracion_field, precio_field]),
                descripcion_field,
            ], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def show_edit_tipo_dialog(tipo):
        nombre_field = ft.TextField(label="Nombre", value=tipo.nombre, expand=True)
        duracion_field = ft.TextField(label="Duración (días)", value=str(tipo.duracion_dias), keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        precio_field = ft.TextField(label="Precio ($)", value=str(tipo.precio_base), keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        descripcion_field = ft.TextField(label="Descripción", value=tipo.descripcion, expand=True, multiline=True, min_lines=2)

        def save(e):
            if not nombre_field.value or not precio_field.value:
                show_snack(page, "Nombre y precio son obligatorios", DANGER)
                page.update()
                return

            try:
                duracion = int(duracion_field.value) if duracion_field.value else 30
            except ValueError:
                duracion = 30

            try:
                precio = float(precio_field.value.replace(",", ""))
            except ValueError:
                precio = 0

            actualizar_tipo_membresia(tipo.id, {
                "nombre": nombre_field.value,
                "duracion_dias": duracion,
                "precio_base": precio,
                "descripcion": descripcion_field.value,
            })
            load_tipos()
            show_snack(page, "Tipo de membresía actualizado", SUCCESS)
            page.update()
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Tipo de Membresía"),
            content=ft.Column([
                nombre_field,
                ft.Row([duracion_field, precio_field]),
                descripcion_field,
            ], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def confirm_delete_tipo(tipo):
        def delete(e):
            eliminar_tipo_membresia(tipo.id)
            load_tipos()
            show_snack(page, "Tipo de membresía eliminado", SUCCESS)
            page.update()
            page.pop_dialog()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar el tipo '{tipo.nombre}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Eliminar", on_click=delete, bgcolor=ft.Colors.RED),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(confirm_dialog)

    def load_membresias():
        membresias_list.controls.clear()
        membresias = obtener_membresias()
        filtro = filter_dropdown.value

        for m in membresias:
            dias = m.dias_restantes()
            esta_vencida = dias is not None and dias < 0
            dias_aviso = int(get_setting("dias_aviso_vencimiento", "3"))
            esta_por_vencer = dias is not None and 0 <= dias <= dias_aviso

            if filtro == "activas" and (esta_vencida or not m.activa):
                continue
            if filtro == "vencidas" and not esta_vencida:
                continue
            if filtro == "por_vencer" and not esta_por_vencer:
                continue

            cliente = obtener_cliente(m.cliente_rut)
            nombre_cliente = cliente.nombre if cliente else "Desconocido"
            tipo = obtener_tipo_membresia(m.plan)
            if tipo:
                plan_nombre = tipo.nombre
                plan_color = get_tipo_color(tipo.nombre)
            else:
                plan_nombre = m.plan
                plan_color = ft.Colors.GREY

            status_text = ""
            status_color = SUCCESS
            status_background = SUCCESS_SOFT
            if esta_vencida:
                status_text = f"Vencida hace {abs(dias) if dias is not None else 0} días"
                status_color = DANGER
                status_background = DANGER_SOFT
            elif esta_por_vencer:
                status_text = f"Por vencer en {dias} días"
                status_color = WARNING
                status_background = WARNING_SOFT
            elif dias is not None:
                status_text = f"{dias} días restantes"
                status_color = SUCCESS
                status_background = SUCCESS_SOFT
            else:
                status_text = "Sin fecha límite"
                status_color = PRIMARY
                status_background = PRIMARY_SOFT

            membresias_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(plan_nombre[:3].upper(), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=plan_color,
                                padding=8,
                                border_radius=8,
                            ),
                            ft.Column([
                                ft.Text(nombre_cliente, weight=ft.FontWeight.W_600, size=16, color=TEXT),
                                ft.Text(
                                    f"Inicio: {m.fecha_inicio.strftime('%d/%m/%Y')}  ·  Fin: {m.fecha_fin.strftime('%d/%m/%Y') if m.fecha_fin else 'Sin límite'}",
                                    size=11, color=TEXT_MUTED,
                                ),
                            ], spacing=2, expand=True),
                            status_badge(status_text, status_color, status_background),
                        ]),
                        ft.Row([
                            ft.Text(f"${m.precio:,.0f}", weight=ft.FontWeight.BOLD, size=18, color=SUCCESS),
                            ft.Container(expand=True),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, memb=m: show_edit_dialog(memb),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Eliminar",
                                    icon_color=ft.Colors.RED,
                                    on_click=lambda e, memb=m: confirm_delete(memb),
                                ),
                            ]),
                        ]),
                    ], spacing=8),
                    padding=15,
                    bgcolor=SURFACE,
                    border=ft.Border.all(1, BORDER),
                    border_radius=12,
                    shadow=CARD_SHADOW,
                )
            )

        if not membresias_list.controls:
            membresias_list.controls.append(
                empty_state(
                    ft.Icons.FITNESS_CENTER,
                    "No hay membresías asignadas",
                    "Asigna un plan a un cliente para verlo aquí.",
                )
            )

        page.update()

    def show_add_dialog():
        clientes = obtener_clientes()
        if not clientes:
            show_snack(page, "Primero debes registrar un cliente", WARNING)
            page.update()
            return

        tipos = obtener_tipos_membresia()
        if not tipos:
            show_snack(page, "Primero crea un tipo de membresía", WARNING)
            page.update()
            return

        cliente_field = ft.TextField(
            label="Cliente",
            hint_text="Buscar por nombre o RUT...",
            autofocus=True,
            prefix_icon=ft.Icons.PERSON_SEARCH,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            border_radius=10,
        )

        sugerencias_list = ft.ListView(height=120, spacing=2, visible=False)

        sugerencias_container = ft.Container(
            content=sugerencias_list,
            border=ft.Border.all(1, BORDER),
            border_radius=ft.BorderRadius.all(10),
            bgcolor=SURFACE,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        def actualizar_sugerencias(e):
            texto = cliente_field.value or ""
            sugerencias_list.controls.clear()

            if texto:
                resultados = [
                    c for c in clientes
                    if texto.lower() in c.nombre.lower() or texto.lower() in c.id.lower()
                ]
                for c in resultados:
                    sugerencias_list.controls.append(
                        ft.Container(
                            content=ft.Text(f"{c.nombre} ({c.id})", size=14),
                            padding=10,
                            ink=True,
                            on_click=lambda ev, cliente=c: seleccionar_cliente(cliente),
                        )
                    )

            sugerencias_list.visible = bool(texto and sugerencias_list.controls)
            page.update()

        def seleccionar_cliente(cliente):
            cliente_field.value = f"{cliente.nombre} ({cliente.id})"
            sugerencias_list.visible = False
            page.update()

        cliente_field.on_change = actualizar_sugerencias

        tipo_dropdown = ft.Dropdown(
            label="Tipo de Membresía",
            options=[ft.dropdown.Option(t.id, f"{t.nombre} - ${t.precio_base:,.0f}") for t in tipos],
            expand=True,
        )

        fecha_inicio_field = ft.TextField(
            label="Fecha de inicio",
            value=datetime.now().strftime("%Y-%m-%d"),
            read_only=True,
            expand=True,
        )
        fecha_inicio_picker = ft.DatePicker(
            value=datetime.now(),
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        fecha_inicio_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.show_dialog(fecha_inicio_picker),
        )
        fecha_inicio_picker.on_change = lambda e: (
            setattr(fecha_inicio_field, 'value', e.control.value.strftime("%Y-%m-%d")),
            on_fecha_inicio_change(e),
            page.update()
        )

        notas_field = ft.TextField(label="Notas", expand=True, multiline=True, min_lines=2)

        def on_tipo_change(e):
            tipo_id = e.control.value
            if tipo_id:
                tipo = obtener_tipo_membresia(tipo_id)
                if tipo:
                    if tipo.duracion_dias > 0:
                        try:
                            inicio = datetime.strptime(fecha_inicio_field.value, "%Y-%m-%d")
                            fecha_fin = inicio + timedelta(days=tipo.duracion_dias)
                            fecha_fin_field.value = fecha_fin.strftime("%Y-%m-%d")
                        except Exception:
                            pass
            else:
                fecha_fin_field.value = ""
            page.update()

        tipo_dropdown.on_change = on_tipo_change

        fecha_fin_field = ft.TextField(label="Fecha de fin", read_only=True, expand=True)
        fecha_fin_picker = ft.DatePicker(
            value=None,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        fecha_fin_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.show_dialog(fecha_fin_picker),
        )
        fecha_fin_picker.on_change = lambda e: (
            setattr(fecha_fin_field, 'value', e.control.value.strftime("%Y-%m-%d") if e.control.value else ""),
            page.update()
        )

        def on_fecha_inicio_change(e):
            try:
                tipo_id = tipo_dropdown.value
                if tipo_id:
                    tipo = obtener_tipo_membresia(tipo_id)
                    if tipo and tipo.duracion_dias > 0:
                        inicio = datetime.strptime(fecha_inicio_field.value, "%Y-%m-%d")
                        fecha_fin = inicio + timedelta(days=tipo.duracion_dias)
                        fecha_fin_field.value = fecha_fin.strftime("%Y-%m-%d")
                        page.update()
            except ValueError:
                pass

        def save(e):
            texto = cliente_field.value or ""
            cliente_seleccionado = next((c for c in clientes if f"{c.nombre} ({c.id})" == texto), None)
            if not cliente_seleccionado or not tipo_dropdown.value:
                show_snack(page, "Selecciona un cliente válido y el tipo de membresía", DANGER)
                page.update()
                return

            cliente_rut = cliente_seleccionado.id
            tipo = obtener_tipo_membresia(tipo_dropdown.value)
            if not tipo:
                show_snack(page, "Tipo de membresía no válido", DANGER)
                page.update()
                return

            fecha_inicio = datetime.strptime(fecha_inicio_field.value, "%Y-%m-%d") if fecha_inicio_field.value else datetime.now()
            fecha_fin = datetime.strptime(fecha_fin_field.value, "%Y-%m-%d") if fecha_fin_field.value else None

            membresia = Membresia(
                cliente_rut=cliente_rut,
                plan=tipo.id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                precio=tipo.precio_base,
                notas=notas_field.value,
            )
            crear_membresia(membresia)
            load_membresias()
            show_snack(page, "Membresía asignada exitosamente", SUCCESS)
            page.update()
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("Asignar Membresía"),
            content=ft.Column([
                cliente_field,
                sugerencias_container,
                tipo_dropdown,
                ft.Row([
                    ft.Column([fecha_inicio_field, fecha_inicio_btn], spacing=0, width=150),
                    ft.Column([fecha_fin_field, fecha_fin_btn], spacing=0, width=150),
                ], spacing=10),
                notas_field,
            ], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def show_edit_dialog(membresia):
        clientes = obtener_clientes()
        tipos = obtener_tipos_membresia()

        cliente_dropdown = ft.Dropdown(
            label="Cliente",
            options=[ft.dropdown.Option(c.id, c.nombre) for c in clientes],
            value=membresia.cliente_rut,
            expand=True,
        )

        tipo_dropdown = ft.Dropdown(
            label="Tipo de Membresía",
            options=[ft.dropdown.Option(t.id, f"{t.nombre} - ${t.precio_base:,.0f}") for t in tipos],
            value=membresia.plan if membresia.plan in [t.id for t in tipos] else "",
            expand=True,
        )

        fecha_inicio_field = ft.TextField(
            label="Fecha de inicio",
            value=membresia.fecha_inicio.strftime("%Y-%m-%d") if membresia.fecha_inicio else "",
            read_only=True,
            expand=True,
        )
        fecha_inicio_picker = ft.DatePicker(
            value=membresia.fecha_inicio,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        fecha_inicio_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.show_dialog(fecha_inicio_picker),
        )
        fecha_inicio_picker.on_change = lambda e: (
            setattr(fecha_inicio_field, 'value', e.control.value.strftime("%Y-%m-%d")),
            page.update()
        )

        fecha_fin_field = ft.TextField(
            label="Fecha de fin",
            value=membresia.fecha_fin.strftime("%Y-%m-%d") if membresia.fecha_fin else "",
            read_only=True,
            expand=True,
        )
        fecha_fin_picker = ft.DatePicker(
            value=membresia.fecha_fin,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        fecha_fin_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.show_dialog(fecha_fin_picker),
        )
        fecha_fin_picker.on_change = lambda e: (
            setattr(fecha_fin_field, 'value', e.control.value.strftime("%Y-%m-%d") if e.control.value else ""),
            page.update()
        )

        activa_switch = ft.Switch(label="Activa", value=membresia.activa)
        notas_field = ft.TextField(label="Notas", value=membresia.notas, expand=True, multiline=True, min_lines=2)

        def save(e):
            if not cliente_dropdown.value or not tipo_dropdown.value:
                show_snack(page, "Cliente y tipo de membresía son obligatorios", DANGER)
                page.update()
                return

            fecha_inicio = datetime.strptime(fecha_inicio_field.value, "%Y-%m-%d") if fecha_inicio_field.value else datetime.now()
            fecha_fin = datetime.strptime(fecha_fin_field.value, "%Y-%m-%d") if fecha_fin_field.value else None

            tipo = obtener_tipo_membresia(tipo_dropdown.value)
            precio = tipo.precio_base if tipo else 0

            actualizar_membresia(membresia.id, {
                "cliente_rut": cliente_dropdown.value,
                "plan": tipo_dropdown.value,
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
                "precio": precio,
                "activa": activa_switch.value,
                "notas": notas_field.value,
            })
            load_membresias()
            show_snack(page, "Membresía actualizada", SUCCESS)
            page.update()
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Membresía"),
            content=ft.Column([
                cliente_dropdown,
                tipo_dropdown,
                ft.Row([
                    ft.Column([fecha_inicio_field, fecha_inicio_btn], spacing=0, width=150),
                    ft.Column([fecha_fin_field, fecha_fin_btn], spacing=0, width=150),
                ], spacing=10),
                activa_switch,
                notas_field,
            ], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Guardar", on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def confirm_delete(membresia):
        def delete(e):
            eliminar_membresia(membresia.id)
            load_membresias()
            show_snack(page, "Membresía eliminada", SUCCESS)
            page.update()
            page.pop_dialog()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Eliminar esta membresía?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Eliminar", on_click=delete, bgcolor=ft.Colors.RED),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(confirm_dialog)

    filter_dropdown.on_change = lambda e: load_membresias()

    def init():
        content_container.content = tipos_content
        btn_tipos.bgcolor = PRIMARY_SOFT
        btn_asignaciones.bgcolor = SURFACE
        load_tipos()
        page.update()

    return (ft.Column([
        page_header(
            "Membresías",
            "Crea planes y controla sus asignaciones.",
        ),
        ft.Row([btn_tipos, btn_asignaciones], spacing=10),
        content_container,
    ], expand=True, spacing=16), init)
