import flet as ft
import os
import json
from settings_db import get_setting, set_setting, is_firebase_configured
from database import reset_db
from ui import (
    BORDER, PRIMARY, SUCCESS, SUCCESS_SOFT, SURFACE, TEXT, TEXT_MUTED, WARNING,
    WARNING_SOFT, page_header, section_title, surface,
)


def settings_page(page: ft.Page):
    firebase_cred_path = ft.TextField(
        label="Ruta del archivo JSON de Firebase",
        value=get_setting("firebase_credentials_path", ""),
        hint_text="C:\\ruta\\firebase_credentials.json",
        expand=True,
    )

    firebase_project_id = ft.TextField(
        label="Project ID de Firebase",
        value=get_setting("firebase_project_id", ""),
        hint_text="mi-proyecto-gym",
        expand=True,
    )

    email_sender = ft.TextField(
        label="Email remitente (Gmail)",
        value=get_setting("email_sender", ""),
        hint_text="tu_correo@gmail.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        expand=True,
    )

    email_password = ft.TextField(
        label="App Password de Google",
        value=get_setting("email_password", ""),
        hint_text="16 caracteres",
        password=True,
        can_reveal_password=True,
        expand=True,
    )

    email_receiver = ft.TextField(
        label="Email para recibir alertas",
        value=get_setting("email_receiver", ""),
        hint_text="correo@gmail.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        expand=True,
    )

    dias_aviso = ft.TextField(
        label="Dias de aviso",
        value=get_setting("dias_aviso_vencimiento", "3"),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=100,
    )

    status_text = ft.Text("", size=14)

    async def browse_credentials(e):
        files = await ft.FilePicker().pick_files(
            dialog_title="Seleccionar credenciales de Firebase",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
            allow_multiple=False,
        )
        if files:
            firebase_cred_path.value = files[0].path
            page.update()

    def save_settings(e):
        errors = []

        if not firebase_cred_path.value:
            errors.append("La ruta de credenciales de Firebase es obligatoria")
        elif not os.path.exists(firebase_cred_path.value):
            errors.append("El archivo de credenciales no existe")

        if not firebase_project_id.value:
            errors.append("El Project ID es obligatorio")

        if email_sender.value and not email_password.value:
            errors.append("Si configuras email, necesitas el App Password")

        if errors:
            status_text.value = "❌ " + "\n".join(errors)
            status_text.color = ft.Colors.RED
            page.update()
            return

        try:
            with open(firebase_cred_path.value, "r") as f:
                cred_data = json.load(f)
                if "project_id" not in cred_data:
                    errors.append("El archivo JSON no parece ser de Firebase")
                    status_text.value = "❌ " + "\n".join(errors)
                    status_text.color = ft.Colors.RED
                    page.update()
                    return
        except Exception as ex:
            errors.append(f"Error al leer el archivo: {str(ex)}")
            status_text.value = "❌ " + "\n".join(errors)
            status_text.color = ft.Colors.RED
            page.update()
            return

        set_setting("firebase_credentials_path", firebase_cred_path.value)
        set_setting("firebase_project_id", firebase_project_id.value)
        set_setting("email_sender", email_sender.value)
        set_setting("email_password", email_password.value)
        set_setting("email_receiver", email_receiver.value)
        set_setting("dias_aviso_vencimiento", dias_aviso.value)

        reset_db()

        status_text.value = "✅ Configuracion guardada exitosamente. Reinicia la app para aplicar cambios de Firebase."
        status_text.color = ft.Colors.GREEN
        page.update()

    def test_firebase(e):
        if not is_firebase_configured():
            status_text.value = "❌ Firebase no esta configurado"
            status_text.color = ft.Colors.RED
            page.update()
            return

        try:
            from database import get_db, obtener_clientes
            db = get_db()
            clientes = obtener_clientes()
            status_text.value = f"✅ Conexion exitosa! Project: {firebase_project_id.value} | Clientes: {len(clientes)}"
            status_text.color = ft.Colors.GREEN
        except Exception as ex:
            status_text.value = f"❌ Error de conexion: {str(ex)}"
            status_text.color = ft.Colors.RED
        page.update()

    def test_email(e):
        if not email_sender.value or not email_password.value or not email_receiver.value:
            status_text.value = "❌ Configura todos los campos de email primero"
            status_text.color = ft.Colors.RED
            page.update()
            return

        try:
            from email_service import enviar_email_vencimiento
            from settings_db import set_setting
            set_setting("email_sender", email_sender.value)
            set_setting("email_password", email_password.value)
            set_setting("email_receiver", email_receiver.value)

            success, msg = enviar_email_vencimiento(ignorar_limite=True)
            if success:
                status_text.value = f"✅ {msg}"
                status_text.color = ft.Colors.GREEN
            else:
                status_text.value = f"❌ {msg}"
                status_text.color = ft.Colors.RED
        except Exception as ex:
            status_text.value = f"❌ Error: {str(ex)}"
            status_text.color = ft.Colors.RED
        page.update()

    def load_settings(e):
        firebase_cred_path.value = get_setting("firebase_credentials_path", "")
        firebase_project_id.value = get_setting("firebase_project_id", "")
        email_sender.value = get_setting("email_sender", "")
        email_password.value = get_setting("email_password", "")
        email_receiver.value = get_setting("email_receiver", "")
        dias_aviso.value = get_setting("dias_aviso_vencimiento", "3")
        status_text.value = ""
        page.update()

    firebase_status = ft.Container(
        content=ft.Row([
            ft.Icon(
                ft.Icons.CHECK_CIRCLE if is_firebase_configured() else ft.Icons.WARNING,
                color=SUCCESS if is_firebase_configured() else WARNING,
                size=20,
            ),
            ft.Text(
                "Firebase configurado" if is_firebase_configured() else "Firebase NO configurado",
                size=14,
                weight=ft.FontWeight.W_600,
                color=TEXT,
            ),
        ]),
        padding=12,
        bgcolor=SUCCESS_SOFT if is_firebase_configured() else WARNING_SOFT,
        border=ft.Border.all(1, SUCCESS if is_firebase_configured() else WARNING),
        border_radius=10,
    )

    return ft.ListView(
        spacing=16,
        padding=0,
        controls=[
            page_header(
                "Configuración",
                "Conexiones, notificaciones y preferencias del sistema.",
            ),
            surface(ft.Column([
                section_title("Conexión con Firebase", ft.Icons.CLOUD_OUTLINED),
                firebase_status,
                ft.Row([
                    firebase_cred_path,
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Buscar archivo",
                        icon_color=PRIMARY,
                        on_click=browse_credentials,
                    ),
                ]),
                firebase_project_id,
                ft.Text(
                    "Obtén las credenciales en Firebase Console › Configuración del proyecto › "
                    "Cuentas de servicio › Generar clave privada.",
                    size=11,
                    color=TEXT_MUTED,
                    italic=True,
                ),
            ], spacing=12), padding=20),
            surface(ft.Column([
                section_title("Alertas por email", ft.Icons.MAIL_OUTLINE),
                ft.Text(
                    "Configura la cuenta desde la que se enviarán los avisos de vencimiento.",
                    size=12,
                    color=TEXT_MUTED,
                ),
                email_sender,
                email_password,
                email_receiver,
                ft.Row([
                    ft.Text("Avisar antes del vencimiento", size=13, color=TEXT),
                    dias_aviso,
                    ft.Text("días", size=13, color=TEXT_MUTED),
                ]),
                ft.Text(
                    "La cuenta de Google necesita una contraseña de aplicación.",
                    size=11,
                    color=TEXT_MUTED,
                    italic=True,
                ),
            ], spacing=12), padding=20),
            ft.Row([
                ft.FilledButton(
                    "Guardar configuración",
                    icon=ft.Icons.SAVE,
                    on_click=save_settings,
                ),
                ft.OutlinedButton(
                    "Probar Firebase",
                    icon=ft.Icons.CLOUD_DONE,
                    on_click=test_firebase,
                ),
                ft.OutlinedButton(
                    "Probar Email",
                    icon=ft.Icons.EMAIL,
                    on_click=test_email,
                ),
                ft.OutlinedButton(
                    "Recargar",
                    icon=ft.Icons.REFRESH,
                    on_click=load_settings,
                ),
            ], spacing=10, wrap=True),
            ft.Container(
                content=status_text,
                padding=15,
                bgcolor=SURFACE,
                border=ft.Border.all(1, BORDER),
                border_radius=10,
                visible=True,
            ),
        ],
        expand=1,
    )
