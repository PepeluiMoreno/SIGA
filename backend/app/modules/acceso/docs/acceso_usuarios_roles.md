# Control de usuarios, permisos y estructura organizativa

## 1. Principios de diseño

- Separar identidad, organización y autorización.
- Centralizar la seguridad en backend (nunca en frontend ni resolvers).
- Modelo híbrido RBAC + jerarquía organizativa.
- Toda decisión de acceso es determinista y trazable.
- El sistema debe funcionar en modo:
  - Monoterritorial
  - Multiterritorial (feature flag)


## 2. Feature flag de territorialidad

### Propósito
Controlar si el sistema opera con una única estructura o con múltiples agrupaciones territoriales.

### Flag
- `MULTITERRITORIAL_MODE: bool`

### Impacto del flag

#### Si FALSE (modo simple)
- Existe una única agrupación implícita
- No hay traslados entre agrupaciones
- Junta única global

#### Si TRUE (modo complejo)
- Existen múltiples agrupaciones territoriales
- Usuarios pueden cambiar de agrupación
- Existen juntas independientes por agrupación
- Se habilita histórico de pertenencias


## 3. Modelo de usuario

### Usuario (entidad base)
- Identidad única del sistema
- Puede actuar como:
  - Miembro
  - Voluntario
  - Ambos
  - Externo (solo acceso limitado)

### Estados posibles
- pendiente
- activo
- rechazado
- suspendido


## 4. Generación de juntas directivas

### Regla general
Cada agrupación territorial tiene una junta independiente.

### Composición fija
- Presidente
- Vicepresidente
- Secretario
- Tesorero


### Proceso de creación de junta

1. Crear agrupación territorial
2. Inicializar estructura de junta
3. Asignar cargos obligatorios
4. Validar unicidad de cargos por agrupación
5. Asociar cada cargo a usuarios miembros
6. Asociar cargos a roles del sistema


### Junta central

- Existe siempre independientemente del modo territorial
- Funciona como nivel de coordinación global
- Puede tener cargos equivalentes a los territoriales


## 5. Cargos y roles

### Separación clave

- Cargo → estructura organizativa
- Rol → capacidad funcional


### Relación

- Cargo puede tener múltiples roles asociados
- Un rol puede estar asociado a múltiples cargos
- Un usuario hereda roles a través de su cargo


### Ejemplo

Cargo: Presidente territorial  
→ Rol: diseño_campañas  
→ Rol: asignación_recursos  


## 6. Sistema de permisos

### Modelo
Usuario
↓ (por cargo o directo)
Rol
↓
Funcionalidad
↓
Transacción

# Resolución de permisos El sistema evalúa acceso combinando:

1. Roles del usuario
2. Roles derivados de cargos activos
3. Roles directos asignados4. Contexto territorial (si aplica)Resultado:- ALLOW / DENY

## 7. Funcionalidades y transacciones### Funcionalidad

Agrupación lógica de operaciones.

Ejemplo:- diseño_campaña- gestión_militancia- gestión_económica

### TransacciónUnidad mínima ejecutable.

Ejemplos:- crear_campaña- asignar_presupuesto- validar_miembro
Relación- Funcionalidad contiene transacciones- Rol habilita funcionalidades o transacciones- Transacción es el punto final de autorización


### 8. Servicios de aplicación

Responsabilidad Orquestar casos de uso completos.

Ejemplos:- creación de campañas- validación de miembros- gestión de cuotas- traslado de miembros

Regla importante- Nunca contienen lógica de permisos compleja- Solo invocan AuthorizationService


### 8. Servicios de aplicación

### 9. Authorization Service (núcleo del sistema)

ResponsabilidadResolver si un usuario puede ejecutar una transacción

Entrada- Usuario- Transacción- Contexto (agrupación, junta, etc.)
Salida- permitido / denegado- motivo

# Lógica interna1. Obtener roles del usuario2. Obtener roles por cargo activo3. Evaluar jerarquía organizativa4. Mapear roles → transacciones5. Validar contexto territorial (si aplica)


### 10. Frontend (GraphQL) 

Reglas estrictas- No evalúa permisos- No conoce roles internos de negocio- Solo consume capacidades expuestas
UX permitida- Mostrar/ocultar elementos según permisos recibidos- Consultar:  - me  - capabilities  - permisos derivados


### 11. Resolvers (Strawberry)

Responsabilidad- Adaptar GraphQL a servicios- Inyectar contexto de usuario- Delegar en Application Services

Prohibido- lógica de negocio- lógica de permisos- acceso directo a reglas RBAC


### 12. Casos de uso clave del sistema### Usuarios- registro- validación- activación- suspensión### Organización- creación de agrupaciones- generación de juntas- asignación de cargos- traslado de miembros### Permisos- asignación de roles- validación de transacciones- auditoría de accesos### Operación- campañas- tareas- voluntariado


### 13. AuditoríaTodo acceso a transacciones debe registrar:- usuario- rol efectivo- transacción- resultado- contexto (agrupación/junta)- timestamp


### 14. Modelo conceptual final
Usuario
├── Miembro
├── Voluntario
└── Credenciales
Usuario
↓
Cargo (Junta Central / Territorial)
↓
Rol
↓
Funcionalidad
↓
Transacción
Agrupación Territorial
└── Junta Directiva
└── Cargos


### 15. Recomendación de implementación-

 Dominio puro para reglas (sin ORM)- SQLAlchemy solo como persistencia- Application Services como orquestadores- AuthorizationService centralizado- GraphQL como capa fina de transporte- Feature flags para variabilidad estructural


### 16. Resultado esperado- 

Sistema escalable horizontalmente- Control de acceso consistente- Separación clara de responsabilidades- Fácil evolución a nuevos tipos de organización- Independencia del frontend respecto a seguridad