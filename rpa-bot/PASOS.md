# Bot `RegistrarSolicitudEnERP` (Automation Anywhere, Community Edition)

La edición Community no permite exportar el bot, así que se documenta cómo está construido
(ver capturas `docs/img/06a` a `06d`). Es un TaskBot de 21 pasos.

## Variables
| Variable | Tipo | Uso |
|---|---|---|
| `tabla` | Data Table | Filas leídas del Excel |
| `fila` | Record | Fila actual del bucle (`fila[0]` Id, `[1]` Asunto, `[2]` Categoría, `[3]` Monto, `[4]` Correo, `[5]` Descripción, `[6]` CodigoERP, `[7]` EstadoRPA) |
| `nFila` | Number | Contador de fila (empieza en 1; la fila 1 es el encabezado) |
| `sFila` | String | `nFila` convertido a texto, para armar la celda (`G$sFila$`, `H$sFila$`) |
| `codigoERP` | String | Código leído de la pantalla de confirmación |
| contraseña | Credential | Se lee del Credential Vault, no está escrita en el bot |

## Pasos
1. **Excel advanced: Open** `OneDrive\RPA\SolicitudesAprobadas.xlsx` (requiere Excel de escritorio).
2. **Excel advanced: Get worksheet as data table** de la hoja activa → `tabla`.
3. **Browser: Open** `http://127.0.0.1:5000/login`.
4. **Recorder: Capture** escribe `erp_user` en `username`.
5. **Recorder: Capture** escribe la contraseña desde el Credential Vault en `password`.
6. **Recorder: Capture** clic en `btn-login`.
7. **Loop: For each row in table** (`tabla` → `fila`).
8. **Number: Assign** `$nFila$ + 1` → `nFila`.
9. **Number: To string** `nFila` → `sFila`.
10. **If** `fila[7]` ≠ `Registrado` (omite lo ya procesado: idempotencia).
11. Escribe `fila[0]` en `id_solicitud`.
12. Escribe `fila[4]` en `solicitante_email`.
13. Selecciona en `categoria` el elemento que contiene `fila[2]`.
14. Escribe `fila[3]` en `monto`.
15. Escribe `fila[5]` en `descripcion`.
16. Clic en `btn-guardar`.
17. **Get property** `HTML InnerText` de `codigo-registro` → `codigoERP`.
18. Clic en el enlace "Registrar otro".
19. **Excel advanced: Set cell** `G$sFila$` = `codigoERP`.
20. **Excel advanced: Set cell** `H$sFila$` = `Registrado`.
21. **Excel advanced: Close** (guardando).

## Pendientes conocidos
- No maneja la respuesta de error del ERP (por ejemplo, un `id_solicitud` duplicado, 409): debería escribir `Error` en `EstadoRPA`.
- Se ejecuta bajo demanda desde el Control Room, no con un disparador.
