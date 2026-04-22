import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

PLAN_MENSUAL = "mensual"
PLAN_ANUAL = "anual"
PLAN_PAGO_CLASE = "pago_por_clase"
PLAN_MINERO = "minero"
PLAN_COMPLETO = "completo"

PLANES = {
    PLAN_MENSUAL: {"nombre": "Mensual", "duracion_dias": 30, "precio_base": 0},
    PLAN_ANUAL: {"nombre": "Anual", "duracion_dias": 365, "precio_base": 0},
    PLAN_PAGO_CLASE: {"nombre": "Pago por Clase ($5,000)", "duracion_dias": 0, "precio_base": 5000},
    PLAN_MINERO: {"nombre": "Minero (L-V + 2 Sáb)", "duracion_dias": 30, "precio_base": 0},
    PLAN_COMPLETO: {"nombre": "Completo (Todos los días)", "duracion_dias": 30, "precio_base": 0},
}

DIAS_AVISO_VENCIMIENTO = 3

APP_TITLE = "Gym Control"
APP_WIDTH = 1200
APP_HEIGHT = 800