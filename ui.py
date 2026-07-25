"""Shared visual language for Gym Control."""

import flet as ft

from resource_utils import image_as_base64


PRIMARY = "#F04455"
PRIMARY_DARK = "#B71835"
PRIMARY_SOFT = "#FFF0F2"
APP_BG = "#F6F7FB"
SURFACE = "#FFFFFF"
TEXT = "#101828"
TEXT_MUTED = "#667085"
BORDER = "#E7EAF0"
NAV_BG = "#111827"
NAV_SURFACE = "#1D2939"
NAV_MUTED = "#98A2B3"
SUCCESS = "#12A36D"
SUCCESS_SOFT = "#EAF8F2"
WARNING = "#E28A13"
WARNING_SOFT = "#FFF6E5"
DANGER = "#D92D20"
DANGER_SOFT = "#FEEDEC"
INFO = "#3578D4"
INFO_SOFT = "#EDF4FF"

CARD_SHADOW = ft.BoxShadow(
    blur_radius=24,
    spread_radius=0,
    offset=ft.Offset(0, 8),
    color=ft.Colors.with_opacity(0.07, "#101828"),
)


def configure_page(page: ft.Page) -> None:
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY,
        font_family="Segoe UI",
        use_material3=True,
    )
    page.bgcolor = APP_BG
    page.padding = 0


def brand_image(size: int = 76) -> ft.Control:
    encoded_image = image_as_base64("charly_photo.jpg")
    if encoded_image:
        return ft.Container(
            content=ft.Image(
                src=encoded_image,
                width=size,
                height=size,
                fit=ft.BoxFit.COVER,
            ),
            width=size,
            height=size,
            border_radius=size // 2,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border=ft.Border.all(3, SURFACE),
            shadow=ft.BoxShadow(
                blur_radius=18,
                offset=ft.Offset(0, 5),
                color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
            ),
        )
    return ft.Container(
        content=ft.Icon(ft.Icons.FITNESS_CENTER, size=size * 0.52, color=PRIMARY),
        width=size,
        height=size,
        border_radius=size // 2,
        bgcolor=PRIMARY_SOFT,
        alignment=ft.Alignment.CENTER,
    )


def page_header(title: str, subtitle: str, action: ft.Control = None) -> ft.Control:
    title_block = ft.Column(
        [
            ft.Row([
                ft.Container(width=26, height=4, bgcolor=PRIMARY, border_radius=4),
                ft.Text(
                    "GESTIÓN DEL GIMNASIO",
                    size=9,
                    weight=ft.FontWeight.W_700,
                    color=PRIMARY,
                ),
            ], spacing=8),
            ft.Text(title, size=30, weight=ft.FontWeight.W_700, color=TEXT),
            ft.Text(subtitle, size=13, color=TEXT_MUTED),
        ],
        spacing=3,
        expand=True,
    )
    controls = [title_block]
    if action is not None:
        controls.append(action)
    return ft.Row(
        controls,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def surface(content: ft.Control, padding: int = 18, expand: bool = False) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=18,
        shadow=CARD_SHADOW,
        expand=expand,
    )


def empty_state(icon, title: str, subtitle: str = "") -> ft.Container:
    controls = [
        ft.Container(
            content=ft.Icon(icon, size=34, color=TEXT_MUTED),
            width=64,
            height=64,
            bgcolor=APP_BG,
            border_radius=32,
            alignment=ft.Alignment.CENTER,
        ),
        ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=TEXT),
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=12, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER))
    return ft.Container(
        content=ft.Column(
            controls,
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        alignment=ft.Alignment.CENTER,
    )


def status_badge(label: str, color: str, background: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_600, color=color),
        padding=ft.Padding.symmetric(horizontal=10, vertical=5),
        bgcolor=background,
        border_radius=20,
    )


def section_title(title: str, icon=None) -> ft.Row:
    controls = []
    if icon is not None:
        controls.append(
            ft.Container(
                content=ft.Icon(icon, size=18, color=PRIMARY),
                width=34,
                height=34,
                bgcolor=PRIMARY_SOFT,
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            )
        )
    controls.append(ft.Text(title, size=17, weight=ft.FontWeight.W_700, color=TEXT))
    return ft.Row(controls, spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def show_snack(page: ft.Page, message: str, bgcolor: str) -> None:
    """Display a consistent floating notification using Flet's dialog stack."""
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=bgcolor,
            behavior=ft.SnackBarBehavior.FLOATING,
            show_close_icon=True,
            close_icon_color=ft.Colors.WHITE,
        )
    )
