# Solución de Power Platform

`GestorDeSolicitudes_1_0_0_1.zip` es la solución **no administrada** "Gestor de solicitudes". Contiene:

- Tablas de Dataverse: `Solicitud` (`kc_solicitud`) y `Categoria` (`kc_categoria1`).
- Canvas App "Gestor de Solicitudes".
- Flujos: `Solicitudes - Aprobacion`, `Solicitudes - Sincronizar codigo ERP` (manual) y `Solicitudes - Sincronizar codigo ERP (Programado)` (cada 15 min, desactivado).

## Importar
1. make.powerapps.com → Soluciones → Importar solución → elige el `.zip`.
2. Crea las conexiones que pida (Dataverse, Aprobaciones, Excel Online y OneDrive para la Empresa).
3. Crea en tu OneDrive `RPA/SolicitudesAprobadas.xlsx` con una tabla `tblSolicitudes` y las columnas:
   `IdSolicitud, Asunto, Categoria, Monto, CorreoSolicitante, Descripcion, CodigoERP, EstadoRPA`.
4. En el flujo de aprobación, cambia el correo del aprobador (está fijo en la acción "Iniciar y esperar una aprobación").
