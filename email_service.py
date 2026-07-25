import smtplib
from collections import OrderedDict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from html import escape
from settings_db import get_setting
from database import get_alerta_enviada_hoy, registrar_alerta_enviada
from database import obtener_membresias_por_vencer, obtener_cliente, obtener_tipo_membresia


def _crear_mensaje(email_sender, destinatario, asunto, cuerpo):
    msg = MIMEMultipart()
    msg["From"] = email_sender
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "html", "utf-8"))
    return msg


def _fila_membresia(detalle, incluir_cliente=False):
    membresia = detalle["membresia"]
    cliente = detalle["cliente"]
    dias = membresia.dias_restantes()
    fecha_fin = membresia.fecha_fin.strftime("%d/%m/%Y") if membresia.fecha_fin else "N/A"

    celda_cliente = ""
    if incluir_cliente:
        nombre_cliente = cliente.nombre if cliente else "Desconocido"
        celda_cliente = f"<td>{escape(nombre_cliente)}</td>"

    return f"""
<tr>
{celda_cliente}
<td>{escape(detalle["plan_nombre"])}</td>
<td>{escape(fecha_fin)}</td>
<td>{dias if dias is not None else "N/A"}</td>
</tr>
"""


def _cuerpo_resumen(detalles, dias_aviso):
    filas = "".join(_fila_membresia(detalle, incluir_cliente=True) for detalle in detalles)
    return f"""
<html>
<body>
<h2>Alerta de Vencimiento de Membresías</h2>
<p>Las siguientes membresías vencen en los próximos {dias_aviso} días:</p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
<tr style="background-color: #f2f2f2;">
<th>Cliente</th>
<th>Plan</th>
<th>Fecha de Vencimiento</th>
<th>Días Restantes</th>
</tr>
{filas}
</table>
<br>
<p style="color: #888;">Este es un mensaje automático de Gym Control.</p>
</body>
</html>
"""


def _cuerpo_cliente(cliente, detalles):
    filas = "".join(_fila_membresia(detalle) for detalle in detalles)
    return f"""
<html>
<body>
<h2>Tu membresía está próxima a vencer</h2>
<p>Hola {escape(cliente.nombre or "cliente")},</p>
<p>Te informamos que tu membresía está próxima a vencer:</p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
<tr style="background-color: #f2f2f2;">
<th>Plan</th>
<th>Fecha de Vencimiento</th>
<th>Días Restantes</th>
</tr>
{filas}
</table>
<p>Contáctanos para renovar tu membresía y continuar disfrutando de nuestros servicios.</p>
<br>
<p style="color: #888;">Este es un mensaje automático de Gym Control.</p>
</body>
</html>
"""


def enviar_email_vencimiento(ignorar_limite=False):
    email_sender = get_setting("email_sender", "")
    email_password = get_setting("email_password", "")
    email_receiver = get_setting("email_receiver", "")
    dias_aviso = int(get_setting("dias_aviso_vencimiento", "3"))

    if not email_sender or not email_password or not email_receiver:
        return False, "Configuracion de email incompleta. Ve a Settings."

    if not ignorar_limite:
        alerta_hoy = get_alerta_enviada_hoy()
        if alerta_hoy:
            return True, f"Alerta ya enviada hoy ({alerta_hoy['cantidad']} membresias)"

    membresias_por_vencer = obtener_membresias_por_vencer(dias_aviso)

    if not membresias_por_vencer:
        if not ignorar_limite:
            registrar_alerta_enviada(0)
        return True, "No hay membresias por vencer"

    detalles = []
    membresias_por_cliente = OrderedDict()
    for m in membresias_por_vencer:
        cliente = obtener_cliente(m.cliente_rut)
        tipo = obtener_tipo_membresia(m.plan)
        detalle = {
            "membresia": m,
            "cliente": cliente,
            "plan_nombre": tipo.nombre if tipo else m.plan,
        }
        detalles.append(detalle)
        if cliente:
            membresias_por_cliente.setdefault(cliente.rut, {
                "cliente": cliente,
                "detalles": [],
            })["detalles"].append(detalle)

    mensaje_resumen = _crear_mensaje(
        email_sender,
        email_receiver,
        f"Gym Control - {len(membresias_por_vencer)} membresía(s) por vencer",
        _cuerpo_resumen(detalles, dias_aviso),
    )

    server = None
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(mensaje_resumen)

        clientes_notificados = 0
        clientes_sin_email = 0
        errores_clientes = 0
        for datos_cliente in membresias_por_cliente.values():
            cliente = datos_cliente["cliente"]
            email_cliente = (cliente.email or "").strip()
            if not email_cliente:
                clientes_sin_email += 1
                continue

            try:
                mensaje_cliente = _crear_mensaje(
                    email_sender,
                    email_cliente,
                    "Gym Control - Tu membresía está próxima a vencer",
                    _cuerpo_cliente(cliente, datos_cliente["detalles"]),
                )
                server.send_message(mensaje_cliente)
                clientes_notificados += 1
            except (smtplib.SMTPException, OSError, ValueError):
                errores_clientes += 1

        if not ignorar_limite:
            registrar_alerta_enviada(len(membresias_por_vencer))

        mensaje = (
            f"Resumen enviado con {len(membresias_por_vencer)} membresía(s); "
            f"{clientes_notificados} cliente(s) notificado(s)"
        )
        if clientes_sin_email:
            mensaje += f", {clientes_sin_email} sin email"
        if errores_clientes:
            mensaje += f", {errores_clientes} envío(s) a clientes con error"
        return True, mensaje
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"
    finally:
        if server is not None:
            try:
                server.quit()
            except smtplib.SMTPException:
                pass


def verificar_y_enviar_alertas(ignorar_limite=False):
    success, mensaje = enviar_email_vencimiento(ignorar_limite=ignorar_limite)
    return {
        "exitoso": success,
        "mensaje": mensaje,
        "timestamp": datetime.now().isoformat(),
    }
