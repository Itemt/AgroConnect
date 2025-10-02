# 🔧 Configurar ePayco en Coolify

## ❗ Problema Actual

El modal de ePayco se queda cargando porque **faltan las credenciales de ePayco** en el servidor.

---

## 📋 Pasos para Configurar ePayco en Coolify

### 1️⃣ Obtener Credenciales de ePayco

1. Ve a [dashboard.epayco.com](https://dashboard.epayco.com)
2. Inicia sesión con tu cuenta
3. Ve a **Configuración** → **Integración** → **Llaves API**
4. Copia tus credenciales:
   - **P_CUST_ID_CLIENTE** (Public Key)
   - **P_KEY** (Private Key)

**IMPORTANTE:** Para pruebas, usa las credenciales de **modo prueba/sandbox**.

### 2️⃣ Configurar Variables en Coolify

1. **Accede a tu proyecto en Coolify**
   - URL: Tu dashboard de Coolify
   - Proyecto: AgroConnect

2. **Ve a Environment Variables**
   - En el menú lateral: `Environment Variables` o `Variables de Entorno`

3. **Agrega las siguientes variables:**

```env
EPAYCO_PUBLIC_KEY=tu_public_key_de_epayco_aqui
EPAYCO_PRIVATE_KEY=tu_private_key_de_epayco_aqui
EPAYCO_TEST_MODE=True
EPAYCO_RESPONSE_URL=https://agroconnect.itemt.tech/payments/success/
EPAYCO_CONFIRMATION_URL=https://agroconnect.itemt.tech/payments/confirmation/
```

**Ejemplo con valores reales:**
```env
EPAYCO_PUBLIC_KEY=65e1cf4e3e1234567890abcdef
EPAYCO_PRIVATE_KEY=abc123def456ghi789jkl012mno
EPAYCO_TEST_MODE=True
EPAYCO_RESPONSE_URL=https://agroconnect.itemt.tech/payments/success/
EPAYCO_CONFIRMATION_URL=https://agroconnect.itemt.tech/payments/confirmation/
```

### 3️⃣ Reiniciar el Contenedor

Después de agregar las variables:

1. **Opción 1:** Coolify puede reiniciar automáticamente
2. **Opción 2:** Click en "Restart" o "Redeploy"
3. Espera 1-2 minutos a que el servicio esté disponible

### 4️⃣ Verificar la Configuración

Una vez reiniciado:

1. Ve a cualquier pedido
2. Haz clic en "Pagar Ahora"
3. El modal de ePayco debería cargar correctamente

---

## 🧪 Credenciales de Prueba de ePayco

Para probar sin hacer cargos reales, usa:

### Tarjeta de Crédito de Prueba:
- **Número:** 4575623182290326
- **CVV:** 123
- **Fecha:** Cualquier fecha futura (ej: 12/25)
- **Nombre:** Tu nombre

### PSE de Prueba:
- **Banco:** Banco de Bogotá
- **Tipo:** Persona Natural
- **Documento:** CC 123456789

---

## 🔍 Diagnóstico de Problemas

### Problema: Modal se queda cargando
**Causa:** Variables de entorno no configuradas o PUBLIC_KEY vacío

**Solución:**
1. Verifica que agregaste las variables en Coolify
2. Reinicia el contenedor
3. Verifica que no haya espacios extra en las claves

### Problema: Error de autenticación
**Causa:** Credenciales incorrectas

**Solución:**
1. Verifica que copiaste las claves completas
2. Asegúrate de usar las claves del modo correcto (prueba/producción)
3. Revisa que no haya caracteres extra

### Problema: Webhook no funciona
**Causa:** URL de confirmación no accesible

**Solución:**
1. Verifica que la URL sea pública: `https://agroconnect.itemt.tech/payments/confirmation/`
2. Configura esta URL en el dashboard de ePayco
3. Asegúrate de que no requiera autenticación

---

## 📞 Soporte

Si tienes problemas:

1. **Documentación de ePayco:** [docs.epayco.com](https://docs.epayco.com)
2. **Soporte ePayco:** soporte@epayco.co
3. **Revisar logs de Coolify:** En la sección de logs del contenedor

---

## ✅ Checklist de Configuración

- [ ] Cuenta de ePayco creada
- [ ] Credenciales obtenidas (Public y Private Key)
- [ ] Variables agregadas en Coolify
- [ ] Contenedor reiniciado
- [ ] Modal de ePayco carga correctamente
- [ ] Pago de prueba realizado exitosamente
- [ ] Webhook configurado en dashboard de ePayco

---

## 🚀 Próximos Pasos para Producción

Cuando estés listo para producción:

1. Obtén las credenciales de **producción** de ePayco
2. Cambia `EPAYCO_TEST_MODE=False`
3. Actualiza las claves a las de producción
4. Verifica con un pago real pequeño
5. Monitorea los primeros pagos

---

## 💡 Notas Importantes

- ⚠️ **NUNCA** subas las credenciales al código fuente
- ⚠️ Usa **variables de entorno** siempre
- ⚠️ En modo prueba, los pagos NO son reales
- ⚠️ Guarda las credenciales en un lugar seguro
- ⚠️ Rota las claves periódicamente por seguridad

