# Gym Control - Sistema de Gestión de Gimnasio

Aplicación de escritorio para llevar el control de mensualidades y clientes de tu gimnasio.

## Tecnologías

- **Python 3.10+**
- **Flet** - Framework de UI
- **Firebase Firestore** - Base de datos en la nube (gratuita)
- **PyInstaller** - Empaquetado como ejecutable

## Estructura de Base de Datos (Firestore)

```
gym_control/
  ├── clientes/{id}
  │   ├── nombre: string
  │   ├── telefono: string
  │   ├── email: string
  │   ├── fecha_registro: timestamp
  │   └── activo: boolean
  │
  ├── membresias/{id}
  │   ├── cliente_id: string (ref)
  │   ├── plan: string (mensual|anual|pago_por_clase|minero|completo)
  │   ├── fecha_inicio: timestamp
  │   ├── fecha_fin: timestamp
  │   ├── precio: number
  │   ├── asistencias_usadas: number
  │   ├── asistencias_restantes: number
  │   ├── activa: boolean
  │   └── notas: string
  │
  └── asistencias/{id}
      ├── cliente_id: string (ref)
      ├── membresia_id: string (ref)
      ├── fecha: timestamp
      └── nota: string
```

## Planes Disponibles

| Plan | Descripción |
|------|-------------|
| **Mensual** | Acceso por 30 días |
| **Anual** | Acceso por 365 días |
| **Pago por Clase** | $5,000 COP por cada clase asistida |
| **Minero** | 3 veces lunes a viernes + 2 sábados al mes |
| **Completo** | Acceso ilimitado todos los días |

## Configuración Inicial

### 1. Firebase (Base de datos gratuita)

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto
3. Ve a **Firestore Database** > **Crear base de datos**
4. Selecciona **modo de prueba** (luego puedes cambiar las reglas)
5. Ve a **Configuración del proyecto** > **Cuentas de servicio**
6. Haz clic en **Generar nueva clave privada**
7. Descarga el archivo JSON y renómbralo a `firebase_credentials.json`
8. Colócalo en la raíz del proyecto
9. Habilitar api: https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project={id-app}
10. Crear BD https://console.cloud.google.com/datastore/setup?project={id-app}

### 2. Configuración de Email (Gmail)

1. Ve a tu cuenta de Google > **Seguridad**
2. Activa la **verificación en 2 pasos** si no está activa
3. Genera una **contraseña de aplicación**:
   - Ve a [Contraseñas de aplicación](https://myaccount.google.com/apppasswords)
   - Selecciona "Otro" y ponle un nombre como "Gym Control"
   - Copia la contraseña de 16 caracteres

### 3. Variables de Entorno

1. Copia `.env.example` a `.env`:
   ```bash
   copy .env.example .env
   ```
2. Edita `.env` con tus credenciales:
   ```
   EMAIL_SENDER=tu_correo@gmail.com
   EMAIL_PASSWORD=tu_app_password_de_google
   EMAIL_RECEIVER=correo_para_notificaciones@gmail.com
   FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
   ```

## Instalación

### Opción 1: Ejecutar desde código fuente

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
python main.py
```

### Opción 2: Compilar como ejecutable (.exe)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Compilar con PyInstaller
pyinstaller build.spec

# El ejecutable estará en dist/GymControl.exe
```

## Uso

### Dashboard
- Vista general con estadísticas del gimnasio
- Alertas de membresías por vencer
- Resumen de asistencias del día

### Clientes (CRUD)
- **Crear**: Botón "Nuevo Cliente"
- **Leer**: Lista con búsqueda en tiempo real
- **Actualizar**: Botón de editar en cada cliente
- **Eliminar**: Botón de eliminar con confirmación

### Membresias
- Asignar planes a clientes
- Seguimiento de vencimientos
- Filtros: Todas, Activas, Vencidas, Por Vencer
- Control de asistencias para planes que lo requieren

### Asistencias
- Registrar entrada de clientes
- Historial completo
- Actualización automática de asistencias usadas

### Notificaciones por Email
- Alertas automáticas 3 días antes del vencimiento
- Botón para verificar y enviar alertas manualmente
- Email HTML con tabla de membresías por vencer

## Reglas de Firestore (Producción)

Cuando estés listo para producción, cambia las reglas de Firestore:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /clientes/{clienteId} {
      allow read, write: if request.auth != null;
    }
    match /membresias/{membresiaId} {
      allow read, write: if request.auth != null;
    }
    match /asistencias/{asistenciaId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Estructura del Proyecto

```
gym_control/
├── main.py                   # Punto de entrada de la app
├── config.py                 # Configuración global
├── models.py                 # Modelos de datos
├── database.py               # Operaciones de Firebase
├── email_service.py          # Servicio de notificaciones
├── requirements.txt          # Dependencias
├── build.spec                # Configuración de PyInstaller
├── .env.example              # Ejemplo de variables de entorno
├── firebase_credentials.json # Credenciales de Firebase (no commitear)
└── pages/
    ├── __init__.py
    ├── dashboard_page.py     # Página del dashboard
    ├── clientes_page.py      # CRUD de clientes
    ├── membresias_page.py    # Gestión de membresías
    └── asistencias_page.py   # Registro de asistencias
```

## Notas

- La app requiere conexión a internet para funcionar (Firebase)
- Tu socio puede ver los datos accediendo a Firebase Console o puedes crearle una cuenta
- Las notificaciones por email se envían solo cuando hay membresías por vencer
- El plan "Pago por Clase" no tiene fecha de fin, se cobra por asistencia
