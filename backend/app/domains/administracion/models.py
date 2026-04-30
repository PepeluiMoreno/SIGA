from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Tabla asociativa Usuario-Rol (muchos a muchos)
usuarios_roles = Table(
    'usuarios_roles',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id'), nullable=False),
    Column('rol_id', Integer, ForeignKey('roles.id'), nullable=False),
    Column('agrupacion_territorial_id', Integer, ForeignKey('agrupaciones_territoriales.id')),  # Si el rol es territorial
    Column('fecha_asignacion', DateTime, default=datetime.utcnow),
    Column('fecha_revocacion', DateTime),
    Column('activo', Boolean, default=True),
    Column('asignado_por_id', Integer, ForeignKey('usuarios.id')),
    UniqueConstraint('usuario_id', 'rol_id', 'agrupacion_territorial_id', name='uq_usuario_rol_agrupacion')
)

# Tabla asociativa Rol-Transaccion (muchos a muchos)
roles_transacciones = Table(
    'roles_transacciones',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('rol_id', Integer, ForeignKey('roles.id'), nullable=False),
    Column('transaccion_id', Integer, ForeignKey('transacciones.id'), nullable=False),
    Column('fecha_asignacion', DateTime, default=datetime.utcnow),
    Column('asignado_por_id', Integer, ForeignKey('usuarios.id')),
    UniqueConstraint('rol_id', 'transaccion_id', name='uq_rol_transaccion')
)


class TipoRol(str, enum.Enum):
    SISTEMA = "SISTEMA"           # Roles del sistema (no modificables)
    ORGANIZACION = "ORGANIZACION"  # Roles organizativos (presidente, secretario, etc.)
    TERRITORIAL = "TERRITORIAL"    # Coordinadores territoriales
    FUNCIONAL = "FUNCIONAL"        # Roles funcionales (tesorero, etc.)
    PERSONALIZADO = "PERSONALIZADO" # Roles creados por administrador


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    
    # Vinculación con persona
    persona_id = Column(Integer, ForeignKey('personas.id'), unique=True)
    miembro_id = Column(Integer, ForeignKey('miembros.id'))  # Si es miembro
    
    # Credenciales
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Estado
    activo = Column(Boolean, default=True)
    bloqueado = Column(Boolean, default=False)
    fecha_bloqueo = Column(DateTime)
    motivo_bloqueo = Column(Text)
    
    # Sesiones
    ultimo_acceso = Column(DateTime)
    intentos_fallidos = Column(Integer, default=0)
    
    # Verificación
    email_verificado = Column(Boolean, default=False)
    token_verificacion = Column(String(255))
    
    # Recuperación contraseña
    token_reset_password = Column(String(255))
    fecha_token_reset = Column(DateTime)
    
    # Preferencias
    idioma = Column(String(5), default='es')
    timezone = Column(String(50), default='Europe/Madrid')
    
    # Control
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, onupdate=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    modificado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relaciones
    persona = relationship("Persona", back_populates="usuario")
    miembro = relationship("miembro")
    roles = relationship("Rol", secondary=usuarios_roles, back_populates="usuarios")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id], remote_side=[id])
    modificado_por = relationship("Usuario", foreign_keys=[modificado_por_id], remote_side=[id])


class Rol(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    
    # Identificación
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    
    # Tipo
    tipo = Column(Enum(TipoRol), default=TipoRol.PERSONALIZADO)
    
    # Jerarquía
    nivel = Column(Integer, default=0)  # 0=bajo, 100=alto
    
    # Ámbito territorial (si aplica)
    es_territorial = Column(Boolean, default=False)
    nivel_territorial = Column(String(50))  # NACIONAL, AUTONOMICO, PROVINCIAL, LOCAL
    
    # Control
    sistema = Column(Boolean, default=False)  # Si es True, no se puede eliminar
    activo = Column(Boolean, default=True)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, onupdate=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    modificado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relaciones
    usuarios = relationship("Usuario", secondary=usuarios_roles, back_populates="roles")
    transacciones = relationship("Transaccion", secondary=roles_transacciones, back_populates="roles")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id])
    modificado_por = relationship("Usuario", foreign_keys=[modificado_por_id])


class Transaccion(Base):
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True)
    
    # Identificación
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    
    # Clasificación
    modulo = Column(String(100), nullable=False)
    tipo = Column(String(50))  # consulta, escritura, aprobacion, critica, configuracion
    
    # Metadata
    activa = Column(Boolean, default=True)
    sistema = Column(Boolean, default=True)  # Transacciones del sistema
    
    # Relaciones
    roles = relationship("Rol", secondary=roles_transacciones, back_populates="transacciones")


# ==============================================================================
# MIXIN DE AUDITORÍA
# ==============================================================================

class AuditMixin:
    """Mixin para añadir campos de auditoría a cualquier modelo"""
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = Column(DateTime, onupdate=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    modificado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    
    @declared_attr
    def creado_por(cls):
        return relationship("Usuario", foreign_keys=[cls.creado_por_id], post_update=True)
    
    @declared_attr
    def modificado_por(cls):
        return relationship("Usuario", foreign_keys=[cls.modificado_por_id], post_update=True)


# ==============================================================================
# LOG DE AUDITORÍA
# ==============================================================================

class TipoAccion(str, enum.Enum):
    CREAR = "CREAR"
    EDITAR = "EDITAR"
    ELIMINAR = "ELIMINAR"
    VER = "VER"
    APROBAR = "APROBAR"
    RECHAZAR = "RECHAZAR"
    EXPORTAR = "EXPORTAR"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    OTRO = "OTRO"


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    
    id = Column(Integer, primary_key=True)
    
    # Usuario que realiza la acción
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    username = Column(String(100))  # Por si se elimina el usuario
    
    # Acción realizada
    transaccion_codigo = Column(String(50))
    accion = Column(Enum(TipoAccion), nullable=False)
    descripcion = Column(Text)
    
    # Entidad afectada
    entidad = Column(String(100))  # Nombre de la tabla
    entidad_id = Column(Integer)    # ID del registro
    
    # Datos
    datos_anteriores = Column(Text)  # JSON con estado anterior
    datos_nuevos = Column(Text)      # JSON con estado nuevo
    
    # Contexto
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Resultado
    exitoso = Column(Boolean, default=True)
    mensaje_error = Column(Text)
    
    # Timestamp
    fecha_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario")


# ==============================================================================
# EJEMPLO DE APLICACIÓN DEL MIXIN A OTROS MODELOS
# ==============================================================================

# Modificar modelo miembro para incluir auditoría
class miembro(Base, AuditMixin):  # Añadir AuditMixin
    __tablename__ = "miembros"
    
    # ... resto de campos ...


# Modificar modelo Cuota para incluir auditoría
class Cuota(Base, AuditMixin):  # Añadir AuditMixin
    __tablename__ = "cuotas"
    
    # ... resto de campos ...


# Y así con todos los modelos principales