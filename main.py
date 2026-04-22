import flet as ft
from settings_db import is_firebase_configured
from pages.settings_page import settings_page
from logger import logger, log_error
from datetime import datetime


def main(page: ft.Page):
    page.title = "Gym Control"
    page.window.width = 1200
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 20

    if not is_firebase_configured():
        page.add(
            ft.Column([
                ft.Container(height=20),
                ft.Row([
                    ft.Icon(ft.Icons.SETTINGS_SUGGEST, size=40, color=ft.Colors.BLUE),
                    ft.Text("Configura Gym Control", size=24, weight=ft.FontWeight.BOLD),
                ]),
                ft.Text("Primero necesitas configurar Firebase para conectar con la base de datos", size=14, color=ft.Colors.GREY_600),
                ft.Container(height=15),
                ft.Container(
                    content=settings_page(page),
                    expand=True,
                ),
            ], scroll=ft.ScrollMode.AUTO),
        )
        page.update()
        return

    from pages.dashboard_page import dashboard_page
    from pages.clientes_page import clientes_page
    from pages.membresias_page import membresias_page
    from pages.asistencias_page import asignar_membresia
    from email_service import verificar_y_enviar_alertas

    current_page_index = 0

    def navigate(e):
        nonlocal current_page_index
        current_page_index = e.control.selected_index
        update_content()

    def update_content():
        try:
            pages_map = {
                0: dashboard_page,
                1: clientes_page,
                2: membresias_page,
                3: asignar_membresia,
                4: settings_page,
            }
            result = pages_map.get(current_page_index, dashboard_page)(page)
            if isinstance(result, tuple):
                content_area.content = result[0]
                content_area.update()
                if len(result) > 1 and result[1]:
                    result[1]()
            else:
                content_area.content = result
                content_area.update()
        except Exception as ex:
            log_error(ex, f"update_content page_index={current_page_index}")
            content_area.content = ft.Column([
                ft.Text("Error al cargar la pagina", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                ft.Container(height=10),
                ft.Text(str(ex), size=12),
            ])
            content_area.update()

    storage_usage_text = ft.Text("Cargando...", size=10, color=ft.Colors.GREY_600)
    storage_indicator = ft.ProgressBar(width=80, height=6, bar_height=4)

    def update_storage_indicator():
        try:
            from database import calcular_uso_almacenamiento
            uso = calcular_uso_almacenamiento()
            storage_usage_text.value = f"{uso['mb']} MB / 1024 MB"
            storage_indicator.value = uso['porcentaje'] / 100
            if uso['porcentaje'] > 80:
                storage_indicator.color = ft.Colors.RED
                storage_usage_text.color = ft.Colors.RED
            elif uso['porcentaje'] > 50:
                storage_indicator.color = ft.Colors.ORANGE
                storage_usage_text.color = ft.Colors.ORANGE
            else:
                storage_indicator.color = ft.Colors.GREEN
                storage_usage_text.color = ft.Colors.GREY_700
            storage_indicator.update()
            storage_usage_text.update()
        except Exception as ex:
            storage_usage_text.value = "Error"
            storage_usage_text.color = ft.Colors.RED
            storage_usage_text.update()
            log_error(ex, "update_storage_indicator")

    storage_footer = ft.Container(
        content=ft.Column([
            ft.Text("Storage Firebase", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500),
            storage_indicator,
            storage_usage_text,
        ], spacing=2),
        padding=5,
    )

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=100,
        group_alignment=-0.9,
        trailing=storage_footer,
        leading=ft.Column([
            ft.Icon(ft.Icons.FITNESS_CENTER, size=40, color=ft.Colors.BLUE),
            ft.Text("Gym Control", weight=ft.FontWeight.BOLD, size=14),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE,
                selected_icon=ft.Icons.PEOPLE,
                label="Clientes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CARD_MEMBERSHIP,
                selected_icon=ft.Icons.CARD_MEMBERSHIP,
                label="Membresias",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EVENT_AVAILABLE,
                selected_icon=ft.Icons.EVENT_AVAILABLE,
                label="Asistencias",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=navigate,
    )

    def load_page(page_fn):
        result = page_fn(page)
        if isinstance(result, tuple):
            if len(result) > 1 and result[1]:
                result[1]()
            return result[0]
        return result

    content_area = ft.Container(
        content=load_page(dashboard_page),
        expand=True,
    )

    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            content_area,
        ], expand=True),
    )
    page.update()
    update_storage_indicator()

    async def alert_scheduler():
        import asyncio
        from datetime import time as dtime
        while True:
            ahora = datetime.now()
            siguiente = ahora.replace(minute=0, second=0, microsecond=0)
            if siguiente <= ahora:
                siguiente = siguiente.replace(hour=siguiente.hour + 1)
            segundos = (siguiente - ahora).total_seconds()
            if segundos > 0:
                await asyncio.sleep(segundos)
            try:
                from email_service import verificar_y_enviar_alertas
                result = verificar_y_enviar_alertas()
                if result["exitoso"] and "ya enviada" not in result["mensaje"]:
                    page.snack_bar = ft.SnackBar(ft.Text(result["mensaje"]), bgcolor=ft.Colors.GREEN)
                    page.snack_bar.open = True
                    page.update()
                elif not result["exitoso"]:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error email: {result['mensaje']}"), bgcolor=ft.Colors.RED)
                    page.snack_bar.open = True
                    page.update()
            except Exception as ex:
                log_error(ex, "alert_scheduler")
            await asyncio.sleep(3600)

    async def initial_alert_check():
        from email_service import verificar_y_enviar_alertas
        result = verificar_y_enviar_alertas()
        if result["exitoso"] and "ya enviada" not in result["mensaje"]:
            page.snack_bar = ft.SnackBar(ft.Text(result["mensaje"]), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()

    page.run_task(initial_alert_check)
    page.run_task(alert_scheduler)


if __name__ == "__main__":
    ft.app(target=main)