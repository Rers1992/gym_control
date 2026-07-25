from datetime import datetime

import flet as ft

from database import obtener_estadisticas
from ui import (
    DANGER, DANGER_SOFT, INFO, INFO_SOFT, PRIMARY, PRIMARY_SOFT, SUCCESS,
    SUCCESS_SOFT, SURFACE, TEXT, TEXT_MUTED, WARNING, WARNING_SOFT,
    CARD_SHADOW, page_header, section_title,
)


def dashboard_page(page: ft.Page):
    stats = obtener_estadisticas()
    value_controls = {}

    def stat_card(key, label, icon, color, background):
        value = ft.Text(
            str(stats[key]),
            size=30,
            weight=ft.FontWeight.W_700,
            color=TEXT,
        )
        value_controls[key] = value
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=23, color=color),
                        width=46,
                        height=46,
                        bgcolor=background,
                        border_radius=13,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(expand=True),
                    ft.Container(width=34, height=4, bgcolor=color, border_radius=4),
                ]),
                ft.Text(label, size=11, color=TEXT_MUTED),
                ft.Row([
                    value,
                    ft.Container(
                        content=ft.Text("EN VIVO", size=8, weight=ft.FontWeight.W_700, color=color),
                        padding=ft.Padding.symmetric(horizontal=7, vertical=3),
                        bgcolor=background,
                        border_radius=12,
                    ),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=4),
            padding=16,
            bgcolor=SURFACE,
            border=ft.Border.all(1, "#ECEEF3"),
            border_radius=18,
            shadow=CARD_SHADOW,
        )

    cards = [
        stat_card("total_clientes", "Total de clientes", ft.Icons.GROUP, INFO, INFO_SOFT),
        stat_card("clientes_activos", "Clientes activos", ft.Icons.PERSON, SUCCESS, SUCCESS_SOFT),
        stat_card("membresias_activas", "Membresías activas", ft.Icons.CARD_MEMBERSHIP, PRIMARY, PRIMARY_SOFT),
        stat_card("membresias_vencidas", "Membresías vencidas", ft.Icons.ERROR_OUTLINE, DANGER, DANGER_SOFT),
        stat_card("membresias_por_vencer", "Próximas a vencer", ft.Icons.SCHEDULE, WARNING, WARNING_SOFT),
        stat_card("asistencias_hoy", "Asistencias de hoy", ft.Icons.EVENT_AVAILABLE, SUCCESS, SUCCESS_SOFT),
    ]

    def load_stats():
        latest_stats = obtener_estadisticas()
        for key, control in value_controls.items():
            control.value = str(latest_stats[key])
        page.update()

    months = (
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    )
    today = datetime.now()
    date_label = f"{today.day} de {months[today.month - 1]} de {today.year}"
    greeting = "Buenos días" if today.hour < 12 else "Buenas tardes" if today.hour < 20 else "Buenas noches"

    summary = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=7, height=7, bgcolor="#7CF7C4", border_radius=4),
                        ft.Text("SISTEMA EN LÍNEA", size=9, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                    ], spacing=6),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                    bgcolor=ft.Colors.with_opacity(0.14, ft.Colors.WHITE),
                    border_radius=20,
                    width=145,
                ),
                ft.Text(greeting, size=28, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ft.Text(date_label.capitalize(), size=13, color=ft.Colors.with_opacity(0.82, ft.Colors.WHITE)),
                ft.Text(
                    "Todo lo importante de Charly Boxing, claro y listo para actuar.",
                    size=12.5,
                    color=ft.Colors.with_opacity(0.82, ft.Colors.WHITE),
                ),
            ], spacing=5, expand=True),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.FITNESS_CENTER, size=38, color=ft.Colors.WHITE),
                    ft.Text("TEAM", size=9, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=82,
                height=82,
                bgcolor=ft.Colors.with_opacity(0.14, ft.Colors.WHITE),
                border_radius=22,
                alignment=ft.Alignment.CENTER,
            ),
        ]),
        padding=24,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[PRIMARY, "#A91536"],
        ),
        border_radius=20,
        shadow=ft.BoxShadow(
            blur_radius=28,
            offset=ft.Offset(0, 12),
            color=ft.Colors.with_opacity(0.20, PRIMARY),
        ),
    )

    return ft.Column([
        page_header(
            "Dashboard",
            "Una vista rápida del rendimiento de tu gimnasio.",
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Actualizar estadísticas",
                icon_color=PRIMARY,
                bgcolor=PRIMARY_SOFT,
                on_click=lambda e: load_stats(),
            ),
        ),
        summary,
        section_title("Indicadores principales", ft.Icons.INSIGHTS),
        ft.GridView(
            controls=cards,
            max_extent=360,
            child_aspect_ratio=2.15,
            spacing=14,
            run_spacing=14,
            expand=1,
        ),
    ], spacing=18, expand=True, scroll=ft.ScrollMode.AUTO)
