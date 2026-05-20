# Flujos del módulo Económico

Esta carpeta documenta los **flujos de información** del módulo económico siguiendo la estructura común que acordamos:

1. Propósito
2. Entidades implicadas
3. Estados y transiciones (máquinas de estado)
4. Acciones (quién las dispara y efecto)
5. Pantallas UI
6. Permisos / roles
7. Norma legal aplicable

Plus:
8. Estado de implementación
9. Plan de implementación
10. Decisiones tomadas
11. Pantallas adicionales / casos especiales
12. Implicaciones para otros módulos

---

## Índice de flujos

| # | Flujo | Doc | Estado backend | Estado UI |
|---|---|---|---|---|
| 1 | Establecimiento de cuotas del ejercicio (ordinaria + reducidas) | [01_establecimiento_cuotas.md](./01_establecimiento_cuotas.md) | parcial | ✗ |
| 2 | Emisión de recibos (ordinaria / extraordinaria / reenvío) | [02_emision_recibos.md](./02_emision_recibos.md) | ✓ | ✗ |
| 3 | Generación y envío de remesa SEPA | [03_generacion_remesa.md](./03_generacion_remesa.md) | ✓ parcial | parcial |
| 4 | **Liquidación de remesa** (pain.002 / camt.054) | [04_liquidacion_remesa.md](./04_liquidacion_remesa.md) | parcial | ✗ |
| 5 | Cobro manual (transferencia / efectivo / tarjeta) | [05_cobro_manual.md](./05_cobro_manual.md) | ✓ | parcial |
| 6 | Donaciones (registro + certificado fiscal Modelo 182) | [06_donaciones.md](./06_donaciones.md) | ✓ | ✓ |
| 7 | Justificantes de gasto (presentado → aceptado → aprobado → pagado) | [07_justificantes_gasto.md](./07_justificantes_gasto.md) | parcial | ✗ |
| 8 | Conciliación bancaria (importar extracto, casar movimientos) | ⏳ | ✓ | ✗ |
| 9 | Cierre de ejercicio (regularización → cierre → apertura) | [09_cierre_ejercicio.md](./09_cierre_ejercicio.md) | ✓ | ✗ |
| 10 | Cuentas Anuales (Balance PCESFL + Cuenta Resultados + Memoria) | [10_cuentas_anuales.md](./10_cuentas_anuales.md) | ✗ | ✗ |
| 11 | Modelo 182 (declaración fiscal donaciones a AEAT) | [11_modelo_182.md](./11_modelo_182.md) | ✗ | ✗ |

⏳ = documento pendiente de redactar.

---

## Convenciones

- Cada flujo lleva un número de 2 dígitos (`04_*`).
- Las decisiones se identifican por flujo (`D4.1`, `D4.2`...) y se consolidan también en [decisiones.md](./decisiones.md).
- Las preguntas pendientes para el usuario quedan en la sección 10 del flujo como "Decisiones pendientes" hasta que se respondan; entonces pasan a "Decisiones tomadas".
- Las máquinas de estado se dibujan en ASCII art para que sean legibles en cualquier editor / preview.

### Ciclo de trabajo por funcionalidad

1. **Discutir** — pregunta y respuesta hasta entender qué hace falta.
2. **Diseñar** — decidir entidades, estados, transiciones, pantallas, permisos, norma.
3. **Documentar** — un md con las 7 secciones; las decisiones tomadas se reflejan en [decisiones.md](./decisiones.md).
4. **Visto bueno** del usuario antes de tocar código.
5. **Codear** — backend → frontend → seed/test → permisos.

### Comentarios extemporáneos (= "backlog")

Cuando el usuario observa fallos de UI, disconformidades, bugs o ideas durante un ciclo distinto al que estoy ejecutando, **no se atienden al vuelo**: se anotan en [pendientes_extemporaneos.md](./pendientes_extemporaneos.md) y se repasan al cerrar el ciclo en marcha.

**Importante**: existe **un único archivo** para todas las cuestiones aplazadas: `pendientes_extemporaneos.md`. Aunque en conversación me refiera a él como "backlog", "lista de pendientes" o "extemporáneos", siempre es el mismo archivo. No hay un segundo sitio donde apilar cosas. Cualquier idea, bug o mejora aplazada va aquí.

---

## Manuales de usuario por rol (pendiente — fase final)

Una vez completos todos los flujos, se redactará un **manual por rol** consolidando todas las pantallas y acciones que ese rol puede ejecutar:

| Rol | Manual previsto | Flujos que toca |
|---|---|---|
| `TESORERO_CENTRAL` | manual_tesorero_central.md | 1, 2, 3, 4, 5, 6, 8, 9, 10 (todas) |
| `TESORERO_AGRUPACION` | manual_tesorero_agrupacion.md | 2, 3, 4, 5 (solo de su agrupación) |
| `JUNTA_DIRECTIVA` | manual_junta.md | 9, 10 (aprobación de cierre y CCAA); 7 (autorización justificantes) |
| `SOCIO` | manual_socio.md | recibos propios, donaciones, certificados fiscales |
| `AUDITOR` | manual_auditor.md | lectura sobre 1–10 + Libro Diario + Balance al vuelo |

Cada manual reutilizará las secciones de pantallas (`5.*`) de los flujos correspondientes, filtradas por las transacciones asignadas a ese rol.

> **Nota**: las decisiones tomadas en cada flujo (`Dx.y`) deben quedar reflejadas en el manual del rol que las ejecuta, en lenguaje no técnico.
