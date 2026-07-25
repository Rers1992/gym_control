import flet as ft
from settings_db import is_firebase_configured
from pages.settings_page import settings_page
from logger import log_error
from datetime import datetime
from ui import (
    APP_BG, DANGER, NAV_BG, NAV_MUTED, NAV_SURFACE, PRIMARY, PRIMARY_SOFT,
    SUCCESS, SURFACE, TEXT, TEXT_MUTED, WARNING, brand_image, configure_page,
    show_snack, surface,
)


def main(page: ft.Page):
    page.title = "Gym Control"
    page.window.width = 1280
    page.window.height = 820
    page.window.min_width = 1024
    page.window.min_height = 680
    configure_page(page)

    if not is_firebase_configured():
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        brand_image(64),
                        ft.Column([
                            ft.Text("Configura Gym Control", size=26, weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Text(
                                "Conecta Firebase para comenzar a administrar tu gimnasio.",
                                size=13,
                                color=TEXT_MUTED,
                            ),
                        ], spacing=2),
                    ], spacing=16),
                    surface(settings_page(page), padding=20, expand=True),
                ], spacing=20, expand=True),
                padding=32,
                bgcolor=APP_BG,
                expand=True,
            ),
        )
        page.update()
        return

    from pages.dashboard_page import dashboard_page
    from pages.clientes_page import clientes_page
    from pages.membresias_page import membresias_page
    from pages.asistencias_page import asignar_membresia

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
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=42, color=DANGER),
                ft.Text("Error al cargar la página", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                ft.Container(height=10),
                ft.Text(str(ex), size=12, color=TEXT_MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            content_area.update()

    storage_usage_text = ft.Text("Cargando...", size=10, color=NAV_MUTED)
    storage_indicator = ft.ProgressBar(
        width=118,
        height=6,
        bar_height=4,
        bgcolor=NAV_SURFACE,
        color=SUCCESS,
    )

    def update_storage_indicator():
        try:
            from database import calcular_uso_almacenamiento
            uso = calcular_uso_almacenamiento()
            storage_usage_text.value = f"{uso['mb']} MB / 1024 MB"
            storage_indicator.value = uso['porcentaje'] / 100
            if uso['porcentaje'] > 80:
                storage_indicator.color = DANGER
                storage_usage_text.color = DANGER
            elif uso['porcentaje'] > 50:
                storage_indicator.color = WARNING
                storage_usage_text.color = WARNING
            else:
                storage_indicator.color = SUCCESS
                storage_usage_text.color = NAV_MUTED
            storage_indicator.update()
            storage_usage_text.update()
        except Exception as ex:
            storage_usage_text.value = "Error"
            storage_usage_text.color = DANGER
            storage_usage_text.update()
            log_error(ex, "update_storage_indicator")

    storage_footer = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(width=7, height=7, bgcolor=SUCCESS, border_radius=4),
                ft.Text("FIREBASE ACTIVO", size=9, weight=ft.FontWeight.W_700, color=NAV_MUTED),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            storage_indicator,
            storage_usage_text,
            ft.Container(height=6),
            ft.Text("Gym Control · v2", size=10, color=NAV_MUTED),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        bgcolor=NAV_SURFACE,
        border_radius=14,
    )

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=178,
        min_extended_width=178,
        group_alignment=-0.72,
        bgcolor=NAV_BG,
        indicator_color=PRIMARY,
        use_indicator=True,
        selected_label_text_style=ft.TextStyle(
            color=ft.Colors.WHITE,
            size=11,
            weight=ft.FontWeight.W_600,
        ),
        unselected_label_text_style=ft.TextStyle(color=NAV_MUTED, size=11),
        pin_trailing_to_bottom=True,
        trailing=storage_footer,
        leading=ft.Column([
            brand_image(68),
            ft.Container(height=4),
            ft.Text("CHARLY BOXING", weight=ft.FontWeight.W_700, size=14, color=ft.Colors.WHITE),
            ft.Text("PERFORMANCE TEAM", weight=ft.FontWeight.W_600, size=8, color=PRIMARY),
            ft.Container(width=108, height=1, bgcolor=NAV_SURFACE, margin=ft.Padding.only(top=12)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, color=NAV_MUTED),
                selected_icon=ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.WHITE),
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=NAV_MUTED),
                selected_icon=ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.WHITE),
                label="Clientes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.CARD_MEMBERSHIP_OUTLINED, color=NAV_MUTED),
                selected_icon=ft.Icon(ft.Icons.CARD_MEMBERSHIP, color=ft.Colors.WHITE),
                label="Membresías",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.EVENT_AVAILABLE_OUTLINED, color=NAV_MUTED),
                selected_icon=ft.Icon(ft.Icons.EVENT_AVAILABLE, color=ft.Colors.WHITE),
                label="Asistencias",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=NAV_MUTED),
                selected_icon=ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.WHITE),
                label="Configuración",
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
        padding=ft.Padding.symmetric(horizontal=32, vertical=26),
        bgcolor=APP_BG,
        expand=True,
    )

    page.add(
        ft.Row([
            ft.Container(
                content=rail,
                width=178,
                bgcolor=NAV_BG,
            ),
            content_area,
        ], spacing=0, expand=True),
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
                    show_snack(page, result["mensaje"], SUCCESS)
                    page.update()
                elif not result["exitoso"]:
                    show_snack(page, f"Error email: {result['mensaje']}", DANGER)
                    page.update()
            except Exception as ex:
                log_error(ex, "alert_scheduler")
            await asyncio.sleep(3600)

    async def initial_alert_check():
        from email_service import verificar_y_enviar_alertas
        result = verificar_y_enviar_alertas()
        if result["exitoso"] and "ya enviada" not in result["mensaje"]:
            show_snack(page, result["mensaje"], SUCCESS)
            page.update()

    page.run_task(initial_alert_check)
    page.run_task(alert_scheduler)


if __name__ == "__main__":
    ft.run(main)
