import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from settings_db import get_setting
from database import get_alerta_enviada_hoy, registrar_alerta_enviada
from database import obtener_membresias_por_vencer, obtener_cliente


DIAS_AVISO = int(get_setting("dias_aviso_vencimiento", "3"))


def enviar_email_vencimiento(ignorar_limite=False):
    email_sender = get_setting("email_sender", "")
    email_password = get_setting("email_password", "")
    email_receiver = get_setting("email_receiver", "")

    if not email_sender or not email_password or not email_receiver:
        return False, "Configuracion de email incompleta. Ve a Settings."

    if not ignorar_limite:
        alerta_hoy = get_alerta_enviada_hoy()
        if alerta_hoy:
            return True, f"Alerta ya enviada hoy ({alerta_hoy['cantidad']} membresias)"

    membresias_por_vencer = obtener_membresias_por_vencer(DIAS_AVISO)

    if not membresias_por_vencer:
        if not ignorar_limite:
            registrar_alerta_enviada(0)
        return True, "No hay membresias por vencer"

    cuerpo = """
<html>
<body>
<h2>Alerta de Vencimiento de Membresias</h2>
<p>Las siguientes membresias vencen en los proximos {} dias:</p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
<tr style="background-color: #f2f2f2;">
<th>Cliente</th>
<th>Plan</th>
<th>Fecha de Vencimiento</th>
<th>Dias Restantes</th>
</tr>
""".format(DIAS_AVISO)

    from config import PLANES
    for m in membresias_por_vencer:
        cliente = obtener_cliente(m.cliente_rut)
        nombre_cliente = cliente.nombre if cliente else "Desconocido"
        dias = m.dias_restantes()
        fecha_fin = m.fecha_fin.strftime("%d/%m/%Y") if m.fecha_fin else "N/A"
        plan_nombre = PLANES.get(m.plan, {}).get("nombre", m.plan)

        cuerpo += f"""
<tr>
<td>{nombre_cliente}</td>
<td>{plan_nombre}</td>
<td>{fecha_fin}</td>
<td>{dias if dias is not None else 'N/A'}</td>
</tr>
"""

    cuerpo += """
</table>
<br>
<p style="color: #888;">Este es un mensaje automatico de Gym Control.</p>
</body>
</html>
"""

    msg = MIMEMultipart()
    msg["From"] = email_sender
    msg["To"] = email_receiver
    msg["Subject"] = f"Gym Control - {len(membresias_por_vencer)} membresia(s) por vencer"
    msg.attach(MIMEText(cuerpo, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(msg)
        server.quit()
        if not ignorar_limite:
            registrar_alerta_enviada(len(membresias_por_vencer))
        return True, f"Email enviado con {len(membresias_por_vencer)} membresia(s) por vencer"
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"


def verificar_y_enviar_alertas(ignorar_limite=False):
    success, mensaje = enviar_email_vencimiento(ignorar_limite=ignorar_limite)
    return {
        "exitoso": success,
        "mensaje": mensaje,
        "timestamp": datetime.now().isoformat(),
    }
