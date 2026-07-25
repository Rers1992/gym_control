import flet as ft
from database import (
    obtener_clientes, obtener_membresias_por_cliente, obtener_tipo_membresia,
    registrar_asistencia, obtener_asistencias,
    eliminar_asistencia, actualizar_membresia, obtener_cliente
)
from models import Asistencia
from ui import (
    BORDER, DANGER, PRIMARY, SUCCESS, SUCCESS_SOFT, SURFACE,
    TEXT, TEXT_MUTED, CARD_SHADOW, empty_state, page_header, section_title,
    show_snack, surface,
)


def asignar_membresia(page: ft.Page):
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
            clientes = obtener_clientes()
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
        load_membresias_cliente(cliente.id)
        page.update()

    cliente_field.on_change = actualizar_sugerencias

    membresia_dropdown = ft.Dropdown(
        label="Membresia activa",
        expand=True,
    )

    nota_field = ft.TextField(label="Nota (opcional)", expand=True)

    def load_membresias_cliente(rut_cliente=None):
        membresia_dropdown.options = []
        clientes = obtener_clientes()
        rut = rut_cliente or (
            next((c.id for c in clientes if f"{c.nombre} ({c.id})" == cliente_field.value), None)
            if cliente_field.value else None
        )
        if rut:
            membresias = obtener_membresias_por_cliente(rut)
            for m in membresias:
                if m.activa:
                    tipo = obtener_tipo_membresia(m.plan)
                    plan_nombre = tipo.nombre if tipo else m.plan
                    membresia_dropdown.options.append(
                        ft.dropdown.Option(m.id, f"{plan_nombre} - {m.fecha_inicio.strftime('%d/%m/%Y')}")
                    )
        membresia_dropdown.update()

    def registrar(e):
        clientes = obtener_clientes()
        rut = next((c.id for c in clientes if f"{c.nombre} ({c.id})" == cliente_field.value), None)
        if not rut:
            show_snack(page, "Selecciona un cliente válido", DANGER)
            page.update()
            return

        membresia_id = membresia_dropdown.value if membresia_dropdown.value else None

        asistencia = Asistencia(
            cliente_rut=rut,
            membresia_id=membresia_id,
            nota=nota_field.value,
        )
        registrar_asistencia(asistencia)

        if membresia_id:
            membresia = None
            for m in obtener_membresias_por_cliente(rut):
                if m.id == membresia_id:
                    membresia = m
                    break

            if membresia:
                nuevas_usadas = membresia.asistencias_usadas + 1
                actualizar_membresia(membresia_id, {
                    "asistencias_usadas": nuevas_usadas,
                })

        show_snack(page, "Asistencia registrada", SUCCESS)
        nota_field.value = ""
        cliente_field.value = ""
        membresia_dropdown.options = []
        page.update()
        load_asistencias()

    def load_asistencias():
        atrasos_list.controls.clear()
        atrasos = obtener_asistencias()
        atrasos.sort(key=lambda a: a.fecha, reverse=True)

        if not atrasos:
            atrasos_list.controls.append(
                empty_state(
                    ft.Icons.EVENT_AVAILABLE,
                    "Aún no hay asistencias",
                    "Los ingresos registrados aparecerán en este historial.",
                )
            )
        else:
            for a in atrasos[:50]:
                cliente = obtener_cliente(a.cliente_id)
                nombre_cliente = cliente.nombre if cliente else "Desconocido"

                atrasos_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.CHECK, color=SUCCESS, size=20),
                                width=40,
                                height=40,
                                bgcolor=SUCCESS_SOFT,
                                border_radius=20,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column([
                                ft.Text(nombre_cliente, weight=ft.FontWeight.W_600, size=14, color=TEXT),
                                ft.Text(
                                    f"{a.fecha.strftime('%d/%m/%Y %H:%M')}" +
                                    (f"  ·  {a.nota}" if a.nota else ""),
                                    size=11, color=TEXT_MUTED,
                                ),
                            ], spacing=2, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=DANGER,
                                tooltip="Eliminar",
                                on_click=lambda e, asist=a: confirm_delete(asist),
                            ),
                        ]),
                        padding=12,
                        bgcolor=SURFACE,
                        border=ft.Border.all(1, BORDER),
                        border_radius=12,
                        shadow=CARD_SHADOW,
                    )
                )

        atrasos_list.update()

    def confirm_delete(asistencia):
        def delete(e):
            eliminar_asistencia(asistencia.id)
            load_asistencias()
            show_snack(page, "Asistencia eliminada", SUCCESS)
            page.update()
            page.pop_dialog()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminacion"),
            content=ft.Text("¿Eliminar esta asistencia?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Eliminar", on_click=delete, bgcolor=ft.Colors.RED),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(confirm_dialog)

    atrasos_list = ft.ListView(spacing=6, expand=True)

    def init():
        load_asistencias()
        page.update()

    return (ft.Column([
        page_header(
            "Asistencias",
            "Registra ingresos y revisa la actividad reciente.",
        ),
        surface(
            content=ft.Column([
                section_title("Registrar nueva asistencia", ft.Icons.ADD_TASK),
                cliente_field,
                sugerencias_container,
                ft.Row([membresia_dropdown, nota_field]),
                ft.Row([
                    ft.FilledButton("Registrar ingreso", icon=ft.Icons.CHECK, on_click=registrar),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=10),
            padding=20,
        ),
        section_title("Historial reciente", ft.Icons.HISTORY),
        atrasos_list,
    ], expand=True, spacing=16, scroll=ft.ScrollMode.AUTO), init)
