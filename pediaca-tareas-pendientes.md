# PediAcá — Estado y tareas pendientes

## Bugs del test end-to-end del 26/07/2026 — todos resueltos

Los 5 problemas detectados en el primer test real de punta a punta ya fueron corregidos y desplegados en sesiones posteriores:

1. **Checkout no preguntaba retiro vs. envío** — resuelto. El formulario de pedido ahora pide elegir entre retiro y delivery, y el costo de envío se calcula y se guarda en el pedido.
2. **No se podía asignar un pedido a un cadete** — resuelto. Los cadetes ven los pedidos disponibles de su ciudad en `/mi-panel-cadete`, los aceptan, y el pedido pasa a "en camino" automáticamente.
3. **Emojis rotos en el mensaje de WhatsApp** — resuelto (problema de encoding UTF-8 corregido).
4. **Producto con "Gustos" invisible en el menú público** — resuelto.
5. **Local de prueba duplicado** — el duplicado fue suspendido desde el panel admin. El local de prueba activo sigue siendo `local.qa@pediaca.ar` ("La Testeria QA").

## Sesión del 27–28/07/2026 — GPS en vivo, notificaciones y entrega con código

- **Bug de mapa GPS corregido:** el mapa de seguimiento del cliente (`/pedido/<id>`) nunca se mostraba por un conflicto CSS/JS (`display:none` de una regla de hoja de estilos que un `style=''` inline no lograba pisar). Ya está arreglado y confirmado en producción con marcadores 🏪/📍/🛵 en vivo.
- **Bug de inicio de GPS al aceptar pedido:** aceptar un pedido dejaba el pedido "en camino" al instante, pero como la aceptación es vía AJAX (sin recargar la página), el envío de ubicación del cadete nunca arrancaba hasta refrescar manualmente. Corregido: ahora la página se recarga sola apenas se acepta un pedido.
- **Direcciones claras para el cadete:** tanto en la lista de pedidos disponibles como en la tarjeta de "entrega en curso" ahora se muestran por separado la dirección de retiro (🏪 local) y la de entrega (🏠 cliente), cada una con un botón que abre Google Maps para navegar.
- **Código de entrega de 4 dígitos:** se genera automáticamente en cada pedido nuevo. El cliente lo ve en su pantalla de seguimiento y se lo tiene que dar al cadete al recibir el pedido. El cadete lo ingresa en su panel para poder marcar "Confirmar entrega" — si no coincide, no lo deja confirmar. Los pedidos viejos (sin código) siguen funcionando sin pedirlo, por compatibilidad.
- **Push al cadete si el local cancela:** si un cadete ya tenía un pedido asignado (yendo en camino) y el local lo cancela, ahora le llega una notificación push avisándole para que no siga viaje. Antes esto no pasaba.
- Todo probado de punta a punta en producción con un pedido de prueba real (aceptar → direcciones → código incorrecto rechazado → código correcto confirma la entrega → el cliente ve "¡Pedido entregado!").

## Cuentas de prueba activas

- **Local:** `local.qa@pediaca.ar` / `LocalQaTest2026!` ("La Testeria QA") — contraseña reseteada el 27/07 vía el flujo de recuperación, porque la original se había perdido.
- **Cadete:** `cadete.gpstest@pediaca.ar` / `GpsTest2026!` (Cristian, moto, Rosario) — pensada para probar el seguimiento GPS desde el celular.

## Pendientes (roadmap acordado con Cristian, sin apuro)

- QA a fondo del rol cadete, del panel admin, y de seguridad/permisos cruzados.
- Reseñas de cadetes (falta poder valorarlos, como ya se puede con los locales).
- Panel de estadísticas de ventas para locales.
- Gestión de horarios automática (más allá de pausar manualmente).
- Botón de reclamo/soporte dentro de la app.
- Programar pedido para más tarde (baja prioridad).
- Activar `admin@pediaca.ar` como casilla real (Cristian eligió Zoho Mail gratis — pasos ya conversados, falta que Cristian los ejecute: verificar dominio por TXT, agregar registros MX en Cloudflare, crear la casilla).
- Cuando el roadmap esté completo: revisión general honesta de la plataforma antes de presentarla en la cámara de comercio.

## Lo que funciona bien

Registro de cliente, local y cadete; aprobación de solicitudes desde el panel admin; carga de categorías, productos y promos; pedido completo por WhatsApp con retiro/envío; asignación de pedidos a cadetes con seguimiento GPS en vivo; carrusel de publicidad y banners laterales (desactivados por defecto, listos para demo).
