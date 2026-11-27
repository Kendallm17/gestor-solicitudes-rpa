# ERP legacy (simulado) + scripts SQL

Sistema contable de ejemplo **sin API a propósito**: solo tiene interfaz web. Es el destino al que el bot de
Automation Anywhere registra las solicitudes aprobadas en Power Platform. Incluye los scripts SQL del portafolio.

## Requisitos
- Python 3.10 o superior (en Windows, marca "Add python.exe to PATH" al instalar).

## Ejecutar el ERP (Windows, PowerShell)
```powershell
cd erp-legacy
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Abre http://127.0.0.1:5000 e ingresa con `erp_user` / `erp1234`. La base de datos (`erp.db`) se crea sola.
Las credenciales se pueden cambiar con las variables de entorno `ERP_USER` y `ERP_PASSWORD`.

## Pantallas y selectores estables (para el bot)
| Pantalla | URL | Elementos (atributo `id`) |
|---|---|---|
| Login | `/login` | `username`, `password`, `btn-login` |
| Nuevo registro | `/nuevo` | `id_solicitud`, `solicitante_email`, `categoria` (lista), `monto`, `descripcion`, `btn-guardar` |
| Confirmación | `/registro/<codigo>` | `codigo-registro` (texto `ERP-000123`), `mensaje-ok` |
| Errores de validación | `/nuevo` | `mensaje-error` (id duplicado, correo inválido, etc.) |
| Listado | `/registros` | `q`, `btn-buscar`, `tabla-registros` |

Reglas útiles para el manejo de excepciones del bot:
- El `id_solicitud` es el GUID de la fila en Dataverse y es **único**: registrar dos veces la misma solicitud devuelve un error (idempotencia).
- Monto mayor que cero. Se acepta coma o punto decimal.

## Scripts SQL
```powershell
python seed.py            # carga 5.000 registros de prueba (reproducibles)
python run_analysis.py    # ejecuta sql/03_analysis.sql y muestra los resultados
python explain_demo.py    # plan de ejecución y tiempo ANTES y DESPUÉS de crear un índice
```
| Archivo | Contenido |
|---|---|
| `sql/01_schema.sql` | Tabla `registros` con restricciones (`UNIQUE`, `CHECK`) |
| `sql/02_indexes.sql` | Índice compuesto `(categoria, fecha_registro)` e índice por solicitante |
| `sql/03_analysis.sql` | `GROUP BY`, CTE, `RANK() OVER`, `SUM() OVER` (acumulado), `LAG` (variación mensual), `JOIN` con CTE |

`explain_demo.py` imprime el plan antes (`SCAN registros`) y después (`SEARCH ... USING INDEX`) y el tiempo promedio.
Ojo: `seed.py` y `explain_demo.py` modifican `erp.db`; si ya registraste datos reales, usa otra ruta: `python seed.py demo.db`.

## Nota de diseño
La base es SQLite para que corra sin instalar nada. Las consultas usan SQL estándar y funciones de ventana, por lo que
se portan a PostgreSQL o MySQL 8 cambiando solo las funciones de fecha (`strftime` por `to_char` / `DATE_FORMAT`).
