# Poblado de staging / demo (sin volcado MySQL)

Los seeds históricos (`seed_miembros`, `seed_cuotas`, `seed_importes_cuota`,
`seed_usuarios_volcado`, `seed_remesas`, `seed_campanias`, `seed_nombramientos`…)
leen del **volcado MySQL** de producción y solo sirven para reproducir los datos
reales en desarrollo. En **staging** no hay volcado, así que se usan los seeds
**demo autónomos**.

## Cómo poblar staging

1. Arrancar el backend al menos una vez (el bootstrap crea catálogos base, roles
   funcionales, SUPERADMIN + admin inicial y comunicación).
2. Ejecutar el orquestador demo:

   ```bash
   docker compose exec backend python -m app.scripts.seeding.seed_demo_staging
   ```

   Es **idempotente**: se puede re-ejecutar sin duplicar.

3. Aplicar el `chown` de uploads si el volumen es de root (subida de documentos):

   ```bash
   docker compose exec -u root backend chown -R siga:siga /app/uploads
   ```

## Qué deja poblado

- Catálogos: plan de cuentas, categorías, tipos de miembro/actividad/campaña, habilidades, eventos.
- Estructura territorial completa (nacional → autonómicas → provinciales), roles orgánicos,
  miembros ficticios, juntas y nombramientos (`seed_demo_europalaica`).
- **Cuentas de acceso por perfil** (`seed_demo_usuarios`) — contraseña `Demo2026!`:
  - `presidente.demo@siga.test` · `tesorero.demo@siga.test` · `secretario.demo@siga.test`
  - `interventor.demo@siga.test` · `planificador.demo@siga.test` (coordinador de campañas)
  - `coordinador.demo@siga.test` (COORDINADOR, ámbito territorial de una autonómica)
- **Plan de cuotas** y cuotas del ejercicio (`seed_demo_cuotas`): tarifas 2024–2026
  (BASE/General/Joven/Parado/Honorario) + cuotas anuales del ejercicio actual para los socios activos.
- **Campañas y actividades** demo (`seed_campanias_europalaica`, `seed_actividades_permanentes`).
- Permisos por rol (voluntariado, cuotas, tesorería, justificantes, recibos, donaciones, etc.).

> ⚠️ Cambiar `DEMO_PASSWORD` y/o desactivar las cuentas demo antes de cualquier uso real.

## Seeds demo nuevos (sin volcado)

- `seed_demo_usuarios.py` — cuentas de acceso por perfil + asignación de rol (ámbito global/territorial).
- `seed_demo_cuotas.py` — `importes_cuota_anio` + `cuotas_anuales` del ejercicio.
- `seed_demo_staging.py` — orquestador que encadena, en orden y de forma idempotente, todos los
  seeds demo autónomos (excluye los del volcado).
