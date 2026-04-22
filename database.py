import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from settings_db import get_setting
import os
import json

_db = None
_initialized = False


def get_db():
    global _db, _initialized
    if not _initialized:
        cred_path = get_setting("firebase_credentials_path")
        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(
                "Firebase credentials no configurado. Ve a Settings para configurarlo."
            )
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        _initialized = True
    return _db


def reset_db():
    global _db, _initialized
    _db = None
    _initialized = False


def get_clientes_collection():
    return get_db().collection("clientes")


def get_membresias_collection():
    return get_db().collection("membresias")


def get_asistencias_collection():
    return get_db().collection("asistencias")


def get_alertas_collection():
    return get_db().collection("alertas")


def get_tipos_membresia_collection():
    return get_db().collection("tipos_membresia")


def crear_cliente(cliente):
    rut = cliente.rut.replace(".", "").replace("-", "").upper()
    doc_ref = get_clientes_collection().document(rut)
    doc_ref.set(cliente.to_dict())
    return cliente


def obtener_clientes():
    from models import Cliente
    docs = get_clientes_collection().stream()
    return [Cliente.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_cliente(rut):
    from models import Cliente
    rut = rut.replace(".", "").replace("-", "").upper() if rut else None
    doc = get_clientes_collection().document(rut).get()
    if doc.exists:
        return Cliente.from_dict(doc.id, doc.to_dict())
    return None


def rut_existe(rut):
    rut = rut.replace(".", "").replace("-", "").upper() if rut else None
    doc = get_clientes_collection().document(rut).get()
    return doc.exists


def actualizar_cliente(rut, datos: dict):
    rut = rut.replace(".", "").replace("-", "").upper()
    get_clientes_collection().document(rut).update(datos)


def eliminar_cliente(rut):
    rut = rut.replace(".", "").replace("-", "").upper()
    get_clientes_collection().document(rut).delete()


def buscar_clientes(termino):
    from models import Cliente
    docs = get_clientes_collection().stream()
    termino = termino.lower().replace(".", "").replace("-", "")
    return [
        Cliente.from_dict(doc.id, doc.to_dict())
        for doc in docs
        if termino in doc.to_dict().get("rut", "").lower().replace(".", "").replace("-", "")
        or termino in doc.to_dict().get("nombre", "").lower()
        or termino in doc.to_dict().get("telefono", "").lower()
        or termino in doc.to_dict().get("email", "").lower()
    ]


def crear_membresia(membresia):
    doc_ref = get_membresias_collection().add(membresia.to_dict())
    membresia.id = doc_ref[1].id
    return membresia


def obtener_membresias():
    from models import Membresia
    docs = get_membresias_collection().stream()
    return [Membresia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_membresias_por_cliente(cliente_rut):
    from models import Membresia
    cliente_rut = cliente_rut.replace(".", "").replace("-", "").upper() if cliente_rut else None
    docs = get_membresias_collection().where("cliente_rut", "==", cliente_rut).stream()
    return [Membresia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_membresia(membresia_id):
    from models import Membresia
    doc = get_membresias_collection().document(membresia_id).get()
    if doc.exists:
        return Membresia.from_dict(doc.id, doc.to_dict())
    return None


def actualizar_membresia(membresia_id, datos: dict):
    get_membresias_collection().document(membresia_id).update(datos)


def eliminar_membresia(membresia_id):
    get_membresias_collection().document(membresia_id).delete()


def obtener_membresias_activas():
    from models import Membresia
    docs = get_membresias_collection().where("activa", "==", True).stream()
    return [Membresia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_membresias_por_vencer(dias=3):
    hoy = datetime.now()
    fecha_limite = hoy + timedelta(days=dias)
    membresias_activas = obtener_membresias_activas()
    por_vencer = []
    for m in membresias_activas:
        if m.fecha_fin and m.fecha_fin <= fecha_limite:
            por_vencer.append(m)
    return por_vencer


def obtener_membresias_vencidas():
    hoy = datetime.now()
    membresias_activas = obtener_membresias_activas()
    vencidas = []
    for m in membresias_activas:
        if m.fecha_fin and m.fecha_fin < hoy:
            vencidas.append(m)
    return vencidas


def registrar_asistencia(asistencia):
    doc_ref = get_asistencias_collection().add(asistencia.to_dict())
    asistencia.id = doc_ref[1].id
    return asistencia


def obtener_asistencias():
    from models import Asistencia
    docs = get_asistencias_collection().stream()
    return [Asistencia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_asistencias_por_cliente(cliente_rut):
    from models import Asistencia
    cliente_rut = cliente_rut.replace(".", "").replace("-", "").upper() if cliente_rut else None
    docs = get_asistencias_collection().where("cliente_rut", "==", cliente_rut).stream()
    return [Asistencia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_asistencias_por_membresia(membresia_id):
    from models import Asistencia
    docs = get_asistencias_collection().where("membresia_id", "==", membresia_id).stream()
    return [Asistencia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_asistencias_hoy():
    from models import Asistencia
    hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = hoy_inicio + timedelta(days=1)
    docs = get_asistencias_collection().where("fecha", ">=", hoy_inicio).where("fecha", "<", hoy_fin).stream()
    return [Asistencia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def eliminar_asistencia(asistencia_id):
    get_asistencias_collection().document(asistencia_id).delete()


def obtener_estadisticas():
    clientes = obtener_clientes()
    membresias = obtener_membresias()
    asistenciaes = obtener_asistencias()

    hoy = datetime.now()
    membresias_activas = [m for m in membresias if m.activa]
    membresias_vencidas = [m for m in membresias_activas if m.fecha_fin and m.fecha_fin < hoy]
    membresias_por_vencer = [m for m in membresias_activas if m.fecha_fin and hoy <= m.fecha_fin <= hoy + timedelta(days=3)]
    asistenciaes_hoy = [a for a in asistenciaes if a.fecha.date() == hoy.date()]

    return {
        "total_clientes": len(clientes),
        "clientes_activos": len([c for c in clientes if c.activo]),
        "membresias_activas": len(membresias_activas),
        "membresias_vencidas": len(membresias_vencidas),
        "membresias_por_vencer": len(membresias_por_vencer),
        "asistencias_hoy": len(asistenciaes_hoy),
    }


def calcular_uso_almacenamiento():
    total_bytes = 0
    total_docs = 0
    collections = ["clientes", "membresias", "asistencias", "alertas"]
    
    for coll_name in collections:
        docs = get_db().collection(coll_name).stream()
        for doc in docs:
            doc_data = doc.to_dict()
            doc_size = len(json.dumps(doc_data).encode('utf-8'))
            doc_id_size = len(doc.id.encode('utf-8'))
            total_bytes += doc_size + doc_id_size + 32
            total_docs += 1
    
    mb = total_bytes / (1024 * 1024)
    gb = mb / 1024
    free_gb = 1.0
    
    return {
        "bytes": total_bytes,
        "mb": round(mb, 2),
        "gb": round(gb, 4),
        "docs": total_docs,
        "free_gb": free_gb,
        "porcentaje": round((gb / free_gb) * 100, 1),
        "disponible_mb": round((free_gb * 1024) - (mb), 1),
    }


def get_alerta_enviada_hoy():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    docs = get_alertas_collection().where("fecha", "==", fecha_hoy).stream()
    for doc in docs:
        return {"id": doc.id, "fecha": doc.get("fecha"), "cantidad": doc.get("cantidad")}
    return None


def registrar_alerta_enviada(cantidad):
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    docs = get_alertas_collection().where("fecha", "==", fecha_hoy).stream()
    for doc in docs:
        doc.reference.update({"cantidad": cantidad, "enviada_at": datetime.now().isoformat()})
        return
    get_alertas_collection().add({
        "fecha": fecha_hoy,
        "cantidad": cantidad,
        "enviada_at": datetime.now().isoformat(),
    })


def crear_tipo_membresia(tipo):
    doc_ref = get_tipos_membresia_collection().add(tipo.to_dict())
    tipo.id = doc_ref[1].id
    return tipo


def obtener_tipos_membresia():
    from models import TipoMembresia
    docs = get_tipos_membresia_collection().stream()
    return [TipoMembresia.from_dict(doc.id, doc.to_dict()) for doc in docs]


def obtener_tipo_membresia(tipo_id):
    from models import TipoMembresia
    doc = get_tipos_membresia_collection().document(tipo_id).get()
    if doc.exists:
        return TipoMembresia.from_dict(doc.id, doc.to_dict())
    return None


def actualizar_tipo_membresia(tipo_id, datos: dict):
    get_tipos_membresia_collection().document(tipo_id).update(datos)


def eliminar_tipo_membresia(tipo_id):
    get_tipos_membresia_collection().document(tipo_id).delete()
