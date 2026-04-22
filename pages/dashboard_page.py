import flet as ft
import asyncio
from datetime import datetime
from database import obtener_estadisticas, obtener_membresias_por_vencer, obtener_cliente
#import config


def dashboard_page(page: ft.Page):
    alerts_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

    stats = obtener_estadisticas()
    por_vencer = obtener_membresias_por_vencer()

    card_total_clientes = ft.Container(
        content=ft.Column([
            ft.Text("Total Clientes", size=12, color=ft.Colors.GREY_600),
            ft.Text(str(stats["total_clientes"]), size=28, weight=ft.FontWeight.BOLD),
        ]),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    card_activos = ft.Container(
        content=ft.Column([
            ft.Text("Clientes Activos", size=12, color=ft.Colors.GREY_600),
            ft.Text(str(stats["clientes_activos"]), size=28, weight=ft.FontWeight.BOLD),
        ]),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    card_membresias_activas = ft.Container(
        content=ft.Column([
            ft.Text("Membresias Activas", size=12, color=ft.Colors.GREY_600),
            ft.Text(str(stats["membresias_activas"]), size=28, weight=ft.FontWeight.BOLD),
        ]),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    card_vencidas = ft.Container(
        content=ft.Column([
            ft.Text("Membresias Vencidas", size=12, color=ft.Colors.GREY_600),
            ft.Text(str(stats["membresias_vencidas"]), size=28, weight=ft.FontWeight.BOLD),
        ]),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    card_por_vencer = ft.Container(
        content=ft.Column([
            ft.Text("Por Vencer", size=12, color=ft.Colors.GREY_600),
            ft.Text(str(stats["membresias_por_vencer"]), size=28, weight=ft.FontWeight.BOLD),
        ]),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    card_asistencias_hoy = ft.Container(
        content=ft.Column([
            ft.Text("Asistencias Hoy", size=12, color=ft.Colors.GREY_600),
            ft.Text(str(stats["asistencias_hoy"]), size=28, weight=ft.FontWeight.BOLD),
        ]),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    async def periodic_load():
        while True:
            await asyncio.sleep(30)
            _load_stats()

    def _load_stats():
        nonlocal por_vencer
        stats = obtener_estadisticas()
        por_vencer = obtener_membresias_por_vencer()

        card_total_clientes.content.controls[1].value = str(stats["total_clientes"])
        card_total_clientes.content.controls[1].update()

        card_activos.content.controls[1].value = str(stats["clientes_activos"])
        card_activos.content.controls[1].update()

        card_membresias_activas.content.controls[1].value = str(stats["membresias_activas"])
        card_membresias_activas.content.controls[1].update()

        card_vencidas.content.controls[1].value = str(stats["membresias_vencidas"])
        card_vencidas.content.controls[1].update()

        card_por_vencer.content.controls[1].value = str(stats["membresias_por_vencer"])
        card_por_vencer.content.controls[1].update()

        card_asistencias_hoy.content.controls[1].value = str(stats["asistencias_hoy"])
        card_asistencias_hoy.content.controls[1].update()

        alerts_list.controls.clear()
        if por_vencer:
            for memb in por_vencer:
                cliente = obtener_cliente(memb["cliente_id"])
                dias = (memb["fin"].date() - datetime.now().date()).days
                color = ft.Colors.RED if dias <= 0 else ft.Colors.ORANGE
                alerts_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WARNING, color=color),
                            ft.Text(f"{cliente['nombre']} - {memb['nombre']}", expand=True),
                            ft.Text(f"{dias} dias" if dias > 0 else "Vencida", color=color),
                        ]),
                        padding=5,
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        border_radius=8,
                    )
                )
        else:
            alerts_list.controls.append(
                ft.Text("No hay membresias por vencer", color=ft.Colors.GREY_500, italic=True)
            )
        alerts_list.update()

    return ft.Column([
        ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Resumen general del gimnasio", size=14, color=ft.Colors.GREY_600),
        ft.Container(height=20),
        ft.GridView(
            controls=[
                card_total_clientes,
                card_activos,
                card_membresias_activas,
                card_vencidas,
                card_por_vencer,
                card_asistencias_hoy,
            ],
            max_extent=250,
            spacing=15,
            run_spacing=15,
            expand=1,
        ),
        ft.Container(height=20),
        ft.Text("Alertas de Vencimiento", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),
        ft.Container(
            content=alerts_list,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            expand=True,
        ),
    ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)
