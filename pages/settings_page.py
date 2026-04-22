import flet as ft
import os
import json
from settings_db import get_setting, set_setting, is_firebase_configured
from database import reset_db


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

    def browse_credentials(e):
        def on_result(result):
            if result.files:
                firebase_cred_path.value = result.files[0].path
                page.update()

        dialog = ft.FilePicker(on_result=on_result)
        page.overlay.append(dialog)
        page.update()
        dialog.pick_files(
            dialog_title="Seleccionar credenciales de Firebase",
            allowed_extensions=["json"],
            allow_multiple=False,
        )

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
                color=ft.Colors.GREEN if is_firebase_configured() else ft.Colors.ORANGE,
                size=20,
            ),
            ft.Text(
                "Firebase configurado" if is_firebase_configured() else "Firebase NO configurado",
                size=14,
                weight=ft.FontWeight.W_500,
            ),
        ]),
        padding=10,
        bgcolor=ft.Colors.GREEN_50 if is_firebase_configured() else ft.Colors.ORANGE_50,
        border_radius=8,
    )

    return ft.ListView(
        spacing=10,
        padding=10,
        controls=[
            ft.Text("Configuracion", size=22, weight=ft.FontWeight.BOLD),
            ft.Text("Firebase y notificaciones", size=12, color=ft.Colors.GREY_600),
            firebase_status,
            ft.Container(
                content=ft.Row([
                    firebase_cred_path,
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Buscar archivo",
                        on_click=browse_credentials,
                    ),
                ]),
            ),
            firebase_project_id,
            ft.Text(
                "Obten las credenciales en Firebase Console > Configuracion del proyecto > Cuentas de servicio > Generar clave privada",
                size=11, color=ft.Colors.GREY_500, italic=True,
            ),
            ft.Container(height=15),
            ft.Text("Email", weight=ft.FontWeight.BOLD, size=14),
            email_sender,
            email_password,
            email_receiver,
            ft.Row([
                ft.Text("Dias de aviso:", size=14),
                dias_aviso,
            ]),
            ft.Text(
                "Necesitas generar un App Password en tu cuenta de Google: https://myaccount.google.com/apppasswords",
                size=11, color=ft.Colors.GREY_500, italic=True,
            ),
            ft.Container(height=15),
            ft.Row([
                ft.FilledButton(
                    "Guardar Configuracion",
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
            ]),
            ft.Container(
                content=status_text,
                padding=15,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
            ),
        ],
        expand=1,
    )
