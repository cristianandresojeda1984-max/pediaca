# PediAcá — Tareas pendientes por revisar

Resultado del test real end-to-end hecho el 26/07/2026 (registro de usuarios, aprobación, carga de menú y pedido vía WhatsApp).

## 1. El checkout nunca pregunta retiro vs. envío

Ningún pedido de la plataforma —ni los 18 de demo ni los 2 generados en este test— quedó registrado como envío: todos figuran como "Retiro" en el panel de administración, aunque varios locales (Pizzeria La Esquina, Burger Rebels y el local de prueba) tienen el delivery activado y con costo configurado. El formulario de pedido del cliente nunca le muestra la opción de elegir entre retiro o envío, así que ese dato nunca se completa y siempre queda en "Retiro" por defecto.

**Impacto:** es el bug más importante — si un local vive del delivery, hoy no hay forma de que el pedido lo refleje.

## 2. No se puede asignar un pedido a un cadete

El panel de "Pedidos" es una tabla de solo lectura (columnas: #, local, cliente, total, entrega, estado, fecha) sin ninguna acción disponible. La sección "Cadetes" solo permite suspender cuentas, no asignarles repartos. Hoy la coordinación con el cadete tendría que hacerse manualmente por fuera del sistema (WhatsApp directo), no hay ningún flujo dentro de la web.

**Impacto:** falta construir esta funcionalidad si se quiere que los cadetes reciban pedidos desde la plataforma.

## 3. Emojis rotos en el mensaje de WhatsApp del pedido

El mensaje que se genera al pedir por WhatsApp trae varios emojis (📋, 👤, 📞, 🚚) que llegan como el símbolo "�" en vez del emoji real. Probablemente un problema de encoding UTF-8 al armar el texto del pedido en el servidor.

**Impacto:** estético pero visible en cada pedido — el mensaje que le llega al local queda con caracteres rotos.

## 4. Producto con "Gustos" (variantes) no aparece en el menú público

Le agregué la opción de "Gustos" (sabores) a un producto de prueba ("Docena de Empanadas de Carne") y quedó invisible para el cliente en la página pública del local, aunque sigue apareciendo correctamente en "Mis productos" dentro del panel del dueño del local.

**Impacto:** cualquier local que use variantes/gustos en un producto corre el riesgo de que ese producto no se vea nunca en el menú que ve el cliente.

## 5. Local de prueba duplicado

Se había creado un local de prueba antes de un corte de sesión y se perdió la contraseña de esa cuenta. Tuve que crear una cuenta nueva con el mismo nombre ("La Testeria QA") para poder seguir probando. Quedó un local duplicado y sin uso en el sistema (email `local.qa@pediaca.ar` es el que quedó activo con productos cargados).

**Impacto:** ninguno funcional, pero conviene suspender o borrar el duplicado desde el panel admin para no ensuciar las estadísticas de "Locales por categoría".

---

## Lo que sí funciona bien

Registro de cliente, local y cadete; aprobación de solicitudes desde el panel admin; carga de categorías y productos; y el flujo completo de pedido (cliente arma el carrito → botón "Pedir por WhatsApp" → mensaje prellenado → WhatsApp Web) funcionan de punta a punta sin problemas.
