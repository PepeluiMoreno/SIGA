# AIEL - Sistema de Gestión de Asociaciones

Sistema integral de gestión para organizaciones no gubernamentales, desarrollado con FastAPI, Strawberry GraphQL y SQLAlchemy.

## Tecnologías

- **Backend**: Python 3.11+, FastAPI, Strawberry GraphQL
- **Base de datos**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy 2.0 (async)
- **Autenticación**: JWT con RBAC (Role-Based Access Control)
- **Migraciones**: Alembic

## Módulos Implementados

### 1. Gestión de Usuarios y Autenticación
- Registro y login con JWT
- Sistema de roles y permisos (RBAC)
- Gestión de sesiones
- Control de acceso por transacciones

### 2. Gestión de Miembros/Socios
- Alta, baja y modificación de miembros
- Tipos de miembro: Socio, Simpatizante, etc.
- Datos personales y de contacto
- Documentación (DNI, NIE, Pasaporte)
- Datos bancarios (IBAN para domiciliación)
- Asignación a agrupaciones territoriales
- Soft delete para historial

### 3. Agrupaciones Territoriales
- Estructura organizativa por territorios
- Coordinadores, secretarios y tesoreros por agrupación
- Gestión de miembros por agrupación

### 4. Módulo Financiero
- **Cuotas anuales**: Gestión de cuotas de socios por año
- **Estados de cuota**: Pendiente, Cobrada, Cobrada Parcial, Exento, Devuelta
- **Donaciones**: Registro de donaciones con conceptos predefinidos
- **Remesas SEPA**: Generación de lotes de cobros bancarios
- **Órdenes de cobro**: Seguimiento individual de cada cobro
- **Modos de ingreso**: SEPA, Transferencia, PayPal, Efectivo

### 5. Módulo de Campañas
- **Tipos de campaña**: Recaudación, Sensibilización, Ayuda Directa, Voluntariado
- **Estados**: Planificada, Activa, Suspendida, Finalizada, Cancelada
- **Planificación**: Fechas planificadas vs reales
- **Objetivos y metas**: Meta de recaudación y participantes
- **Acciones**: Actividades dentro de cada campaña
  - Fecha, hora, lugar
  - Voluntarios necesarios/confirmados
  - Materiales necesarios
- **Participantes**: Inscripción de miembros con roles
  - Voluntario, Coordinador, Donante, Colaborador
  - Confirmación y registro de asistencia
  - Horas aportadas
- **Vinculación financiera**: Donaciones asociadas a campañas

### 6. Módulo de Grupos de Trabajo
- **Tipos de grupo**:
  - Permanentes: Técnico, Comunicación, Formación, Jurídico
  - Temporales: Campaña, Evento, Proyecto
- **Gestión de miembros**:
  - Roles: Coordinador, Secretario, Miembro, Colaborador
  - Permisos por rol (editar, aprobar gastos)
  - Fechas de incorporación y baja
- **Tareas**:
  - Asignación a miembros
  - Estados: Pendiente, En Progreso, En Revisión, Completada, Cancelada
  - Prioridades: Alta, Media, Baja
  - Horas estimadas vs reales
- **Reuniones**:
  - Programación con fecha, hora y lugar
  - Soporte para reuniones online (URL)
  - Orden del día y actas
  - Confirmación y registro de asistencia
- **Presupuesto**: Dotación económica por grupo

### 7. Módulo de Voluntariado y Competencias
- **Perfil de voluntario**:
  - Disponibilidad: Completa, Fines de semana, Tardes, Mañanas, Puntual
  - Horas disponibles por semana
  - Experiencia e intereses
  - Movilidad: Carnet de conducir, vehículo propio, disponibilidad para viajar
- **Competencias/Skills**:
  - Categorías: Técnica, Idiomas, Comunicación, Gestión, Jurídica, Educativa, Sanitaria
  - Niveles: Básico, Intermedio, Avanzado, Experto
  - Verificación de competencias
  - Búsqueda de voluntarios por competencias
- **Documentación**:
  - Tipos: CV, Certificados, DNI, Foto, Antecedentes, Autorizaciones, Seguros
  - Control de caducidad
  - Almacenamiento de archivos
- **Formación**:
  - Tipos: Curso, Taller, Seminario, Jornada, Certificación, Título
  - Historial de formación recibida
  - Horas de formación
  - Formación interna vs externa
- **Estadísticas**:
  - Total horas de voluntariado
  - Campañas participadas
  - Historial de participación

## Estructura del Proyecto

```
backend/
├── app/
│   ├── core/
│   │   ├── auth.py          # Autenticación JWT
│   │   ├── config.py        # Configuración desde .env
│   │   ├── context.py       # Contexto GraphQL
│   │   ├── database.py      # Conexión async a BD
│   │   └── permissions.py   # Decoradores de permisos
│   ├── models/
│   │   ├── usuario.py       # Usuarios y roles
│   │   ├── miembro.py       # Miembros/socios
│   │   ├── agrupacion.py    # Agrupaciones territoriales
│   │   ├── financiero.py    # Cuotas, donaciones, remesas
│   │   ├── campania.py      # Campañas y acciones
│   │   ├── grupo_trabajo.py # Grupos, tareas, reuniones
│   │   ├── voluntariado.py  # Competencias, documentos, formación
│   │   ├── tipologias.py    # Tipos y roles del sistema
│   │   └── catalogos.py     # País, provincia
│   ├── schemas/
│   │   ├── usuario.py       # Types GraphQL de usuario
│   │   ├── miembro.py       # Types GraphQL de miembro
│   │   ├── financiero.py    # Types GraphQL financieros
│   │   ├── campania.py      # Types GraphQL de campañas
│   │   ├── grupo_trabajo.py # Types GraphQL de grupos
│   │   ├── voluntariado.py  # Types GraphQL de voluntariado
│   │   └── tipos_base.py    # Types comunes
│   └── resolvers/
│       ├── queries.py       # Query principal
│       ├── mutations.py     # Mutation principal
│       ├── financiero.py    # Resolvers financieros
│       ├── campania.py      # Resolvers de campañas
│       ├── grupo_trabajo.py # Resolvers de grupos
│       └── voluntariado.py  # Resolvers de voluntariado
├── alembic/
│   ├── versions/            # Migraciones
│   └── env.py               # Configuración Alembic
├── main.py                  # Punto de entrada
├── pyproject.toml           # Dependencias
└── .env                     # Variables de entorno
```

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/AIEL.git
cd AIEL/backend
```

2. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -e .
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con los datos de conexión a la base de datos
```

5. Ejecutar migraciones:
```bash
alembic upgrade head
```

6. Iniciar servidor:
```bash
uvicorn main:app --reload
```

## API GraphQL

El endpoint GraphQL está disponible en `http://localhost:8000/graphql`

### Ejemplos de Queries

```graphql
# Obtener campañas activas
query {
  campanias(estadoCodigo: "ACTIVA") {
    id
    codigo
    nombre
    tipoCampania { nombre }
    estadoCampania { nombre }
    metaRecaudacion
    participantes {
      miembro { nombre apellido1 }
      rolParticipante { nombre }
    }
  }
}

# Buscar voluntarios por competencias
query {
  voluntariosDisponibles(filtros: {
    competenciaIds: [1, 2]
    disponibilidad: "FINES_SEMANA"
    puedeConducir: true
  }) {
    miembroId
    nombreCompleto
    competencias { competencia { nombre } nivel { nombre } }
  }
}

# Grupos de trabajo con tareas pendientes
query {
  gruposTrabajo(soloPermanentes: true) {
    nombre
    tipoGrupo { nombre }
    tareasPendientes
    miembros { miembro { nombre } rolGrupo { nombre } }
  }
}
```

### Ejemplos de Mutations

```graphql
# Crear campaña
mutation {
  crearCampania(input: {
    codigo: "CAMP2024-001"
    nombre: "Campaña de Navidad 2024"
    tipoCampaniaId: 1
    metaRecaudacion: 5000.00
    fechaInicioPlan: "2024-12-01"
    fechaFinPlan: "2024-12-31"
  }) {
    id
    codigo
  }
}

# Inscribir participante en campaña
mutation {
  inscribirParticipante(input: {
    campaniaId: 1
    miembroId: 10
    rolParticipanteId: 1
  }) {
    miembro { nombre }
    rolParticipante { nombre }
    confirmado
  }
}

# Asignar competencia a miembro
mutation {
  asignarCompetenciaMiembro(input: {
    miembroId: 5
    competenciaId: 3
    nivelId: 2
  }) {
    competencia { nombre }
    nivel { nombre }
  }
}
```

## Licencia

MIT
