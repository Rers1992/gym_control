from datetime import datetime, date


def validar_rut(rut: str) -> bool:
    rut = rut.replace(".", "").replace("-", "").upper().strip()
    if len(rut) < 8:
        return False
    cuerpo = rut[:-1]
    dv = rut[-1]
    if not cuerpo.isdigit():
        return False
    try:
        suma = 0
        multiplicador = 2
        for i in range(len(cuerpo) - 1, -1, -1):
            suma += int(cuerpo[i]) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2
        resto = suma % 11
        esperado = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "K"}[11 - resto]
        return dv == esperado
    except (ValueError, KeyError):
        return False


def formatear_rut(rut: str) -> str:
    rut = rut.replace(".", "").replace("-", "").upper().strip()
    if len(rut) < 8:
        return rut
    cuerpo = rut[:-1]
    dv = rut[-1]
    n = len(cuerpo)
    if n <= 3:
        cuerpo_formato = cuerpo
    elif n <= 6:
        cuerpo_formato = f"{cuerpo[:-3]}.{cuerpo[-3:]}"
    else:
        cuerpo_formato = f"{cuerpo[:-6]}.{cuerpo[-6:-3]}.{cuerpo[-3:]}"
    return f"{cuerpo_formato}-{dv}"


class Cliente:
    def __init__(self, rut=None, nombre="", telefono="", email="", fecha_registro=None, activo=True):
        self.rut = rut
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.fecha_registro = fecha_registro or datetime.now()
        self.activo = activo

    @property
    def id(self):
        return self.rut

    @id.setter
    def id(self, value):
        self.rut = value

    def to_dict(self):
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "email": self.email,
            "fecha_registro": self.fecha_registro.isoformat() if isinstance(self.fecha_registro, (datetime, date)) else self.fecha_registro,
            "activo": self.activo,
        }

    @staticmethod
    def from_dict(doc_id, data):
        fecha_reg = data.get("fecha_registro")
        if isinstance(fecha_reg, str):
            fecha_reg = datetime.fromisoformat(fecha_reg)
        elif hasattr(fecha_reg, "isoformat"):
            fecha_reg = datetime.fromisoformat(fecha_reg.isoformat())
        else:
            fecha_reg = datetime.now()

        return Cliente(
            rut=data.get("rut") or doc_id,
            nombre=data.get("nombre", ""),
            telefono=data.get("telefono", ""),
            email=data.get("email", ""),
            fecha_registro=fecha_reg,
            activo=data.get("activo", True),
        )


class Membresia:
    def __init__(self, id=None, cliente_rut="", plan="", fecha_inicio=None,
                 fecha_fin=None, precio=0.0, asistencias_usadas=0, asistencias_restantes=0,
                 activa=True, notas=""):
        self.id = id
        self.cliente_rut = cliente_rut
        self.plan = plan
        self.fecha_inicio = fecha_inicio or datetime.now()
        self.fecha_fin = fecha_fin
        self.precio = precio
        self.asistencias_usadas = asistencias_usadas
        self.asistencias_restantes = asistencias_restantes
        self.activa = activa
        self.notas = notas

    @property
    def cliente_id(self):
        return self.cliente_rut

    @cliente_id.setter
    def cliente_id(self, value):
        self.cliente_rut = value

    def to_dict(self):
        return {
            "cliente_rut": self.cliente_rut,
            "plan": self.plan,
            "fecha_inicio": self.fecha_inicio.isoformat() if isinstance(self.fecha_inicio, (datetime, date)) else self.fecha_inicio,
            "fecha_fin": self.fecha_fin.isoformat() if isinstance(self.fecha_fin, (datetime, date)) else self.fecha_fin,
            "precio": self.precio,
            "asistencias_usadas": self.asistencias_usadas,
            "asistencias_restantes": self.asistencias_restantes,
            "activa": self.activa,
            "notas": self.notas,
        }

    @staticmethod
    def from_dict(doc_id, data):
        fecha_ini = data.get("fecha_inicio")
        if isinstance(fecha_ini, str):
            fecha_ini = datetime.fromisoformat(fecha_ini)
        elif hasattr(fecha_ini, "isoformat"):
            fecha_ini = datetime.fromisoformat(fecha_ini.isoformat())
        else:
            fecha_ini = datetime.now()

        fecha_fin = data.get("fecha_fin")
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.fromisoformat(fecha_fin)
        elif hasattr(fecha_fin, "isoformat"):
            fecha_fin = datetime.fromisoformat(fecha_fin.isoformat())

        return Membresia(
            id=doc_id,
            cliente_rut=data.get("cliente_rut") or data.get("cliente_id", ""),
            plan=data.get("plan", ""),
            fecha_inicio=fecha_ini,
            fecha_fin=fecha_fin,
            precio=data.get("precio", 0),
            asistencias_usadas=data.get("asistencias_usadas", 0),
            asistencias_restantes=data.get("asistencias_restantes", 0),
            activa=data.get("activa", True),
            notas=data.get("notas", ""),
        )

    def dias_restantes(self):
        if not self.fecha_fin:
            return None
        if isinstance(self.fecha_fin, str):
            fecha_fin = datetime.fromisoformat(self.fecha_fin).date()
        else:
            fecha_fin = self.fecha_fin.date() if hasattr(self.fecha_fin, "date") else self.fecha_fin
        hoy = date.today()
        return (fecha_fin - hoy).days


class TipoMembresia:
    def __init__(self, id=None, nombre="", duracion_dias=30, precio_base=0, descripcion="", activo=True):
        self.id = id
        self.nombre = nombre
        self.duracion_dias = duracion_dias
        self.precio_base = precio_base
        self.descripcion = descripcion
        self.activo = activo

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "duracion_dias": self.duracion_dias,
            "precio_base": self.precio_base,
            "descripcion": self.descripcion,
            "activo": self.activo,
        }

    @staticmethod
    def from_dict(doc_id, data):
        return TipoMembresia(
            id=doc_id,
            nombre=data.get("nombre", ""),
            duracion_dias=data.get("duracion_dias", 30),
            precio_base=data.get("precio_base", 0),
            descripcion=data.get("descripcion", ""),
            activo=data.get("activo", True),
        )


class Asistencia:
    def __init__(self, id=None, cliente_rut="", membresia_id="", fecha=None, nota=""):
        self.id = id
        self.cliente_rut = cliente_rut
        self.membresia_id = membresia_id
        self.fecha = fecha or datetime.now()
        self.nota = nota

    @property
    def cliente_id(self):
        return self.cliente_rut

    @cliente_id.setter
    def cliente_id(self, value):
        self.cliente_rut = value

    def to_dict(self):
        return {
            "cliente_rut": self.cliente_rut,
            "membresia_id": self.membresia_id,
            "fecha": self.fecha.isoformat() if isinstance(self.fecha, (datetime, date)) else self.fecha,
            "nota": self.nota,
        }

    @staticmethod
    def from_dict(doc_id, data):
        fecha = data.get("fecha")
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        elif hasattr(fecha, "isoformat"):
            fecha = datetime.fromisoformat(fecha.isoformat())
        else:
            fecha = datetime.now()

        return Asistencia(
            id=doc_id,
            cliente_rut=data.get("cliente_rut") or data.get("cliente_id", ""),
            membresia_id=data.get("membresia_id", ""),
            fecha=fecha,
            nota=data.get("nota", ""),
        )
