# Integración de ePayco en AgroConnect

Esta aplicación maneja los pagos con la plataforma ePayco para el marketplace de AgroConnect.

## Configuración

### 1. Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```env
# ePayco Configuration
EPAYCO_PUBLIC_KEY=tu_public_key_aqui
EPAYCO_PRIVATE_KEY=tu_private_key_aqui
EPAYCO_TEST_MODE=True  # False para producción
EPAYCO_RESPONSE_URL=https://tu-dominio.com/payments/success/
EPAYCO_CONFIRMATION_URL=https://tu-dominio.com/payments/confirmation/
```

### 2. Obtener Credenciales de ePayco

1. Regístrate en [ePayco](https://www.epayco.co/)
2. Ve a tu dashboard > Integraciones
3. Copia tu `PUBLIC_KEY` y `PRIVATE_KEY`
4. Para pruebas, activa el modo de prueba

### 3. Configurar Webhook de Confirmación

En el dashboard de ePayco:
1. Ve a Configuración > URLs de Confirmación
2. Agrega: `https://tu-dominio.com/payments/confirmation/`
3. Esta URL recibirá las confirmaciones de pago automáticamente

## Flujo de Pago

1. **Crear Orden**: El comprador crea un pedido desde el marketplace
2. **Iniciar Pago**: El comprador hace clic en "Pagar Ahora" en los detalles del pedido
3. **Checkout**: Se muestra la página de checkout con el formulario de ePayco
4. **Procesar Pago**: El usuario completa el pago en la plataforma de ePayco
5. **Confirmación**: ePayco envía una confirmación al webhook
6. **Actualizar Estado**: El sistema actualiza automáticamente el estado del pago y la orden

## Modelos

### Payment

Almacena información de cada pago:
- `order`: Relación con el pedido
- `user`: Usuario que realiza el pago
- `epayco_ref`: Referencia única del pago
- `amount`: Monto del pago
- `status`: Estado del pago (pending, approved, rejected, failed, cancelled)
- `payment_method`: Método de pago usado

## Vistas Principales

- `checkout_view`: Muestra el formulario de pago
- `payment_success_view`: Página de resultado después del pago
- `payment_confirmation_webhook`: Recibe confirmaciones de ePayco (webhook)
- `payment_history_view`: Historial de pagos del usuario

## Métodos de Pago Soportados

- 💳 Tarjetas de Crédito/Débito
- 🏦 PSE (Transferencia Bancaria)
- 💵 Efectivo (Baloto, Efecty, etc.)

## Seguridad

- Las transacciones se procesan directamente en ePayco
- No almacenamos información sensible de tarjetas
- Todas las comunicaciones usan HTTPS
- Verificación de firmas en confirmaciones

## Testing

Para probar en modo de desarrollo:

```bash
# Asegúrate de tener EPAYCO_TEST_MODE=True
python manage.py runserver
```

Usa las tarjetas de prueba proporcionadas por ePayco:
- **Número**: 4575623182290326
- **CVV**: 123
- **Fecha**: Cualquier fecha futura

## Producción

Antes de ir a producción:

1. Cambia `EPAYCO_TEST_MODE=False`
2. Usa tus credenciales de producción
3. Configura las URLs de confirmación correctas
4. Verifica que el webhook sea accesible públicamente

## Troubleshooting

### El pago no se confirma automáticamente

- Verifica que la URL de confirmación sea accesible
- Revisa los logs de Django para errores
- Verifica en el dashboard de ePayco si la URL está configurada

### Error "ModuleNotFoundError: No module named 'epayco'"

Instala el SDK:
```bash
pip install epaycosdk
```

### Pagos en modo prueba no aparecen

Asegúrate de tener `EPAYCO_TEST_MODE=True` en desarrollo

## Soporte

Para más información:
- [Documentación de ePayco](https://docs.epayco.com/)
- [SDK de Python](https://github.com/epayco/epayco-python)

