# 🚀 Integración de ePayco en AgroConnect

## ✅ ¿Qué se ha integrado?

Hemos integrado completamente la plataforma de pagos **ePayco** en AgroConnect para procesar pagos de manera segura.

### Componentes Creados:

1. **App de Payments** (`payments/`)
   - Modelos para gestionar pagos
   - Servicio de integración con ePayco
   - Vistas para checkout y confirmación
   - Templates para el flujo de pago

2. **Modelo Payment**
   - Almacena información de cada transacción
   - Estados: pendiente, aprobado, rechazado, fallido, cancelado
   - Referencia única de ePayco
   - Relación con pedidos (Order)

3. **Flujo de Pago Completo**
   - Botón "Pagar Ahora" en detalles del pedido
   - Página de checkout con integración de ePayco
   - Confirmación automática vía webhook
   - Página de éxito/error del pago
   - Historial de pagos

4. **Templates Creados**
   - `checkout.html`: Formulario de pago con ePayco
   - `payment_success.html`: Página de resultado
   - `payment_detail.html`: Detalles de un pago
   - `payment_history.html`: Historial de pagos del usuario

## 📋 Configuración Necesaria

### 1. Variables de Entorno

Agrega estas variables a tu archivo `.env` (o configuración de Coolify):

```env
# ePayco Configuration
EPAYCO_PUBLIC_KEY=tu_public_key_de_epayco
EPAYCO_PRIVATE_KEY=tu_private_key_de_epayco
EPAYCO_TEST_MODE=True  # Cambiar a False en producción
EPAYCO_RESPONSE_URL=https://agroconnect.itemt.tech/payments/success/
EPAYCO_CONFIRMATION_URL=https://agroconnect.itemt.tech/payments/confirmation/
```

### 2. Obtener Credenciales de ePayco

1. **Regístrate en ePayco**: https://www.epayco.co/
2. **Accede al Dashboard**: Inicia sesión en tu cuenta
3. **Ve a Integraciones**: Dashboard > Integraciones
4. **Copia tus credenciales**:
   - `PUBLIC_KEY`: Clave pública
   - `PRIVATE_KEY`: Clave privada
5. **Modo de Prueba**: Para desarrollo, activa el modo de prueba

### 3. Configurar Webhook en ePayco

Para que ePayco pueda confirmar los pagos automáticamente:

1. Ve a: Dashboard > Configuración > URLs de Confirmación
2. Agrega: `https://agroconnect.itemt.tech/payments/confirmation/`
3. **Importante**: Esta URL debe ser pública y accesible

## 🔧 Instalación y Despliegue

### Dependencias Agregadas

Ya están en `requirements.txt`:
```
epaycosdk==1.0.0
requests==2.32.3
```

### Pasos para Desplegar

1. **Commit y Push** (ya hicimos el fix del Dockerfile):
   ```bash
   git add .
   git commit -m "Integración de ePayco como plataforma de pagos"
   git push origin main
   ```

2. **Configurar Variables en Coolify**:
   - Ve a tu proyecto en Coolify
   - Agrega las variables de entorno de ePayco
   - Redespliega

3. **Aplicar Migraciones** (se hace automático en el despliegue):
   ```bash
   python manage.py migrate payments
   ```

## 💳 Métodos de Pago Soportados

- 💳 **Tarjetas de Crédito/Débito**: Visa, Mastercard, AmEx
- 🏦 **PSE**: Transferencia bancaria directa
- 💵 **Efectivo**: Baloto, Efecty, Gana, etc.
- 📱 **Otros**: Métodos locales de Colombia

## 🔐 Seguridad

- ✅ Los datos de tarjeta se procesan **directamente en ePayco**
- ✅ No almacenamos información sensible
- ✅ Todas las transacciones usan **HTTPS**
- ✅ Verificación de webhooks
- ✅ Referencias únicas por transacción

## 🧪 Testing en Desarrollo

### Tarjetas de Prueba de ePayco

Para probar pagos en modo de desarrollo:

**Tarjeta de Crédito de Prueba:**
- Número: `4575623182290326`
- CVV: `123`
- Fecha: Cualquier fecha futura
- Nombre: Tu nombre

**PSE de Prueba:**
- Banco: Banco de Bogotá
- Tipo: Persona Natural
- Persona: CC 123456789

## 📊 Flujo del Usuario

1. **Crear Pedido**: Usuario crea un pedido en el marketplace
2. **Ver Pedido**: En los detalles aparece el botón "Pagar Ahora"
3. **Checkout**: Se muestra el formulario de pago de ePayco
4. **Procesar**: Usuario completa el pago
5. **Confirmación**: ePayco envía confirmación automática
6. **Actualización**: El sistema actualiza el estado del pedido
7. **Notificación**: Usuario ve página de éxito y recibe confirmación

## 🛠️ URLs Agregadas

```python
/payments/checkout/<order_id>/          # Página de checkout
/payments/success/                      # Página de éxito
/payments/confirmation/                 # Webhook (ePayco)
/payments/history/                      # Historial de pagos
/payments/<payment_id>/                 # Detalle de un pago
/payments/<payment_id>/cancel/          # Cancelar pago pendiente
```

## 📝 Modelo de Datos

### Payment
```python
- order (ForeignKey): Pedido asociado
- user (ForeignKey): Usuario que paga
- epayco_ref (CharField): Referencia única
- epayco_transaction_id (CharField): ID de transacción
- amount (DecimalField): Monto
- currency (CharField): Moneda (COP)
- payment_method (CharField): Método de pago
- status (CharField): Estado del pago
- response_data (JSONField): Respuesta completa de ePayco
- paid_at (DateTimeField): Fecha de pago
```

## 🚨 Troubleshooting

### El pago no se confirma automáticamente
- ✅ Verifica que la URL de confirmación sea pública
- ✅ Revisa los logs en Coolify
- ✅ Verifica la configuración en el dashboard de ePayco

### Error al procesar pago
- ✅ Verifica las credenciales de ePayco
- ✅ Asegúrate de estar en modo de prueba
- ✅ Revisa que todas las variables de entorno estén configuradas

### No aparece el botón "Pagar Ahora"
- ✅ Verifica que el usuario sea comprador
- ✅ El pedido debe estar en estado "pendiente"
- ✅ No debe tener un pago aprobado previamente

## 📚 Documentación Adicional

- [Documentación de ePayco](https://docs.epayco.com/)
- [SDK Python de ePayco](https://github.com/epayco/epayco-python)
- [Dashboard de ePayco](https://dashboard.epayco.com/)

## 🎯 Próximos Pasos Recomendados

1. **Configurar credenciales de prueba** en Coolify
2. **Probar el flujo completo** en ambiente de staging
3. **Configurar credenciales de producción** cuando estés listo
4. **Implementar notificaciones por email** al confirmar pago
5. **Agregar reporte de transacciones** en el admin dashboard

## 💡 Notas Importantes

- En **modo de prueba**: Los pagos no son reales
- En **producción**: Cambiar `EPAYCO_TEST_MODE=False`
- El webhook debe ser **accesible públicamente**
- Las transacciones se registran en el dashboard de ePayco
- Puedes ver el historial completo en `/payments/history/`

---

**¿Necesitas ayuda?** Contacta al equipo de soporte de ePayco o revisa la documentación oficial.

