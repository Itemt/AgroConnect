from django.shortcuts import render

def documentation_view(request):
    """Vista para mostrar la documentación y FAQ de la plataforma"""
    
    context = {
        'title': 'Documentación y Ayuda',
        'sections': [
            {
                'title': '👥 Para Compradores',
                'icon': 'fas fa-shopping-cart',
                'color': 'blue',
                'content': [
                    {
                        'question': '¿Cómo me registro como comprador?',
                        'answer': 'Ve a "Registrarse" y completa el formulario básico. No necesitas información de finca, solo tus datos personales y ubicación.'
                    },
                    {
                        'question': '¿Qué puedo hacer como comprador?',
                        'answer': 'Puedes: explorar el marketplace, buscar productos por ubicación, hacer pedidos, comunicarte con vendedores, seguir el estado de tus compras y calificar vendedores.'
                    },
                    {
                        'question': '¿Cómo encuentro productos?',
                        'answer': 'Usa el Marketplace para buscar productos por tipo, ubicación o precio. Puedes filtrar por departamento y ciudad para encontrar productos locales.'
                    },
                    {
                        'question': '¿Cómo hago un pedido?',
                        'answer': 'Selecciona el producto que deseas, especifica la cantidad y haz clic en "Agregar al Carrito". Luego procede al checkout y completa tu pedido.'
                    },
                    {
                        'question': '¿Cómo me comunico con vendedores?',
                        'answer': 'Puedes iniciar conversaciones desde las publicaciones o desde tus pedidos. Ve a "Mensajes" para ver todas tus conversaciones activas.'
                    },
                    {
                        'question': '¿Cómo funciona el sistema de conversión de unidades?',
                        'answer': 'Si un vendedor publica en arrobas y tú quieres comprar en kilogramos, el sistema convierte automáticamente el precio y la cantidad disponible. Solo funciona con medidas de peso (kg, libras, arrobas, toneladas).'
                    }
                ]
            },
            {
                'title': '🏪 Para Vendedores',
                'icon': 'fas fa-store',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Cómo me convierto en vendedor?',
                        'answer': 'Si eres comprador, ve al sidebar y haz clic en "¿Quieres ser vendedor?". Completa el formulario de tu primera finca y automáticamente te convertirás en vendedor.'
                    },
                    {
                        'question': '¿Por qué necesito fincas para vender?',
                        'answer': 'Las fincas son OBLIGATORIAS para vender. Garantizan trazabilidad, permiten a los compradores conocer el origen de los productos y generan confianza en la calidad.'
                    },
                    {
                        'question': '¿Cómo gestiono mis fincas?',
                        'answer': 'Ve a "Mis Fincas" en el sidebar (primera opción). Desde ahí puedes: agregar nuevas fincas, editar información, agregar cultivos y ver estadísticas por finca.'
                    },
                    {
                        'question': '¿Cómo publico mis productos?',
                        'answer': 'Ve a "Mis Publicaciones" y haz clic en "Nueva Publicación". Selecciona la finca, el cultivo de esa finca, cantidad disponible y precio. La ubicación se toma automáticamente de la finca.'
                    },
                    {
                        'question': '¿Cómo manejo mis ventas?',
                        'answer': 'Ve a "Ventas" para ver todas tus transacciones, confirmar pedidos, gestionar el estado de tus ventas y ver estadísticas por finca.'
                    },
                    {
                        'question': '¿Qué debo saber sobre las unidades de medida?',
                        'answer': 'Si publicas en medidas de peso (kg, libras, arrobas, etc.), los compradores podrán elegir su unidad preferida. Si publicas en Unidades, Cajas o Bultos, los compradores SOLO podrán comprar en esa unidad fija.'
                    }
                ]
            },
            {
                'title': '🏡 Las Fincas: El Centro de Todo',
                'icon': 'fas fa-home',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Por qué las fincas son el corazón de AgroConnect?',
                        'answer': 'Las fincas son OBLIGATORIAS para vender. Todo gira alrededor de ellas: cultivos, publicaciones, ubicación y trazabilidad. Sin finca, NO puedes vender productos.'
                    },
                    {
                        'question': '¿Cómo creo mi primera finca?',
                        'answer': 'Si eres comprador: ve a "¿Quieres ser vendedor?" en el sidebar. Si ya eres vendedor: ve a "Mis Fincas" y haz clic en "Agregar Finca".'
                    },
                    {
                        'question': '¿Qué información necesito para una finca?',
                        'answer': 'Necesitas: nombre de la finca, departamento, ciudad, dirección, área total, área cultivable, tipo de suelo y tipo de riego. Esta información es crucial para la trazabilidad.'
                    },
                    {
                        'question': '¿Qué puedo hacer desde mis fincas?',
                        'answer': 'Desde "Mis Fincas" puedes: agregar cultivos, crear publicaciones, ver la ubicación en el mapa, gestionar inventario, hacer seguimiento de ventas por finca y agregar más fincas.'
                    },
                    {
                        'question': '¿Puedo tener múltiples fincas?',
                        'answer': '¡Sí! Puedes registrar y gestionar múltiples fincas. Cada finca puede tener diferentes cultivos y ubicaciones. Esto es ideal si tienes terrenos en diferentes lugares.'
                    },
                    {
                        'question': '¿Cómo organizo mis productos por finca?',
                        'answer': 'Cada finca tiene sus propios cultivos. Al crear publicaciones, seleccionas la finca y luego el cultivo específico de esa finca. Así mantienes todo organizado.'
                    }
                ]
            },
            {
                'title': '🌾 Gestión de Cultivos',
                'icon': 'fas fa-seedling',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Cómo agrego cultivos a mi finca?',
                        'answer': 'Ve a "Mis Fincas", selecciona una finca y haz clic en "Agregar Cultivo". Los cultivos están directamente vinculados a la finca donde se producen.'
                    },
                    {
                        'question': '¿Por qué los cultivos están vinculados a fincas?',
                        'answer': 'Para garantizar trazabilidad y transparencia. Los compradores saben exactamente de qué finca viene cada producto, su ubicación y características del terreno.'
                    },
                    {
                        'question': '¿Cómo gestiono mis cultivos?',
                        'answer': 'Desde "Mis Fincas" puedes ver todos los cultivos de cada finca, editarlos, agregar nuevos y hacer seguimiento de su estado y producción.'
                    },
                    {
                        'question': '¿Puedo tener diferentes cultivos en cada finca?',
                        'answer': '¡Sí! Cada finca puede tener sus propios cultivos. Esto te permite organizar mejor tu producción y mostrar a los compradores la diversidad de tus productos.'
                    },
                    {
                        'question': '¿Qué estados pueden tener mis cultivos?',
                        'answer': 'Los cultivos pueden estar en: Sembrado, En Crecimiento, Listo para Cosecha, o Cosechado. Esto ayuda a planificar cuándo estarán disponibles para la venta.'
                    },
                    {
                        'question': '¿Cómo controlo el área ocupada?',
                        'answer': 'El sistema te permite especificar cuánta área de tu finca está ocupada por cada cultivo, ayudándote a gestionar mejor el espacio disponible.'
                    }
                ]
            },
            {
                'title': '⚖️ Sistema de Conversión de Unidades',
                'icon': 'fas fa-balance-scale',
                'color': 'indigo',
                'content': [
                    {
                        'question': '¿Qué es el sistema de conversión de unidades?',
                        'answer': 'Es un sistema que permite a los compradores elegir su unidad de compra preferida cuando el vendedor publica productos en medidas de peso. Si un vendedor publica en arrobas, puedes comprar en kilogramos, libras o cualquier otra medida de peso.'
                    },
                    {
                        'question': '¿Qué unidades son convertibles?',
                        'answer': 'Las medidas de PESO son convertibles: Kilogramos (kg), Gramos (g), Libras (lb), Arrobas (@) y Toneladas (t). Puedes comprar en cualquiera si el vendedor publicó en alguna de estas.'
                    },
                    {
                        'question': '¿Qué unidades NO son convertibles?',
                        'answer': 'Las unidades discretas NO son convertibles: Unidades, Cajas y Bultos. Si el vendedor publica en estas unidades, SOLO puedes comprar en esa unidad específica, sin opción de conversión.'
                    },
                    {
                        'question': '¿Cómo funciona la conversión de precios?',
                        'answer': 'El sistema convierte automáticamente el precio. Ejemplo: Si el vendedor publica 3 arrobas de tomate a $50,000/arroba, y quieres comprar 5 kg, el sistema calcula automáticamente que el precio es $4,346/kg (porque 1 arroba = 11.502 kg).'
                    },
                    {
                        'question': '¿Puedo exceder la cantidad disponible?',
                        'answer': 'No. El sistema valida automáticamente la cantidad disponible convirtiendo tu solicitud a la unidad del vendedor. Si pides más de lo disponible, el botón de compra se desactiva y recibes una advertencia.'
                    },
                    {
                        'question': 'Como vendedor, ¿qué debo saber sobre las unidades?',
                        'answer': 'Si publicas en medidas de peso (kg, libras, arrobas, etc.), los compradores podrán elegir su unidad preferida. Si publicas en Unidades, Cajas o Bultos, los compradores SOLO podrán comprar en esa unidad fija. El sistema te muestra un aviso naranja al seleccionar unidades no convertibles.'
                    }
                ]
            },
            {
                'title': '🔐 Autenticación y Seguridad',
                'icon': 'fas fa-shield-alt',
                'color': 'purple',
                'content': [
                    {
                        'question': '¿Qué métodos de autenticación están disponibles?',
                        'answer': 'Puedes registrarte con email y contraseña, usar Google Sign-In, o recuperar tu contraseña por SMS. Todos los métodos son seguros y están integrados.'
                    },
                    {
                        'question': '¿Cómo funciona el inicio de sesión con Google?',
                        'answer': 'Haz clic en "Iniciar sesión con Google" en la página de login. Si es tu primera vez, se creará automáticamente una cuenta como comprador. Luego puedes completar tu perfil.'
                    },
                    {
                        'question': '¿Cómo recupero mi contraseña por SMS?',
                        'answer': 'En la página de login, haz clic en "¿Olvidaste tu contraseña? Recuperar por SMS". Ingresa tu número de teléfono registrado y recibirás un código de 6 dígitos para restablecer tu contraseña.'
                    },
                    {
                        'question': '¿Es seguro usar Firebase Authentication?',
                        'answer': 'Sí, Firebase es una plataforma de Google con altos estándares de seguridad. Tus datos están protegidos y no se almacenan contraseñas en nuestros servidores cuando usas Google Sign-In.'
                    },
                    {
                        'question': '¿Qué pasa si no tengo acceso a mi teléfono?',
                        'answer': 'Si no puedes recibir SMS, puedes contactar al soporte técnico para recuperar tu cuenta. También puedes usar Google Sign-In si lo configuraste previamente.'
                    },
                    {
                        'question': '¿Puedo cambiar mi método de autenticación?',
                        'answer': 'Sí, puedes agregar una contraseña a tu cuenta de Google o viceversa. Ve a tu perfil para gestionar tus métodos de autenticación.'
                    }
                ]
            },
            {
                'title': '🤖 Asistente IA y Sugerencias',
                'icon': 'fas fa-robot',
                'color': 'purple',
                'content': [
                    {
                        'question': '¿Qué es el asistente IA?',
                        'answer': 'Es un asistente inteligente que puede responder preguntas sobre agricultura, precios de mercado, y darte consejos para mejorar tus publicaciones. Está alimentado por Google Gemini.'
                    },
                    {
                        'question': '¿Cómo uso el asistente IA?',
                        'answer': 'Haz clic en el ícono del chatbot en la esquina inferior derecha de la pantalla. Puedes hacer preguntas sobre agricultura, precios, o cualquier duda que tengas sobre la plataforma.'
                    },
                    {
                        'question': '¿Qué tipo de sugerencias puedo obtener?',
                        'answer': 'El asistente puede sugerir títulos atractivos para tus publicaciones, precios competitivos basados en el mercado local, descripciones optimizadas, y consejos agrícolas específicos para Colombia.'
                    },
                    {
                        'question': '¿El asistente IA es gratuito?',
                        'answer': 'Sí, el asistente IA es completamente gratuito para todos los usuarios. No hay límites en el número de consultas que puedes hacer.'
                    },
                    {
                        'question': '¿Qué pasa si el asistente IA no está disponible?',
                        'answer': 'Si hay problemas con el servicio de IA, el sistema automáticamente usa sugerencias predeterminadas basadas en mejores prácticas agrícolas y de marketing.'
                    },
                    {
                        'question': '¿El asistente conoce el contexto colombiano?',
                        'answer': 'Sí, el asistente está configurado para entender el contexto agrícola colombiano, incluyendo precios en COP, ubicaciones geográficas, y prácticas agrícolas locales.'
                    }
                ]
            },
            {
                'title': '💰 Pagos y Transacciones',
                'icon': 'fas fa-credit-card',
                'color': 'purple',
                'content': [
                    {
                        'question': '¿Qué métodos de pago aceptan?',
                        'answer': 'Aceptamos tarjetas de crédito y débito (Visa, MasterCard, AmEx, Diners), transferencias bancarias PSE, y pagos en efectivo a través de MercadoPago (Baloto, Efecty, Gana, etc.).'
                    },
                    {
                        'question': '¿Es seguro pagar en AgroConnect?',
                        'answer': 'Sí, usamos MercadoPago que es una plataforma de pagos certificada y segura. Tus datos financieros están protegidos y no se almacenan en nuestros servidores.'
                    },
                    {
                        'question': '¿Cuándo recibo mi dinero como vendedor?',
                        'answer': 'El dinero se libera automáticamente cuando el comprador confirma la recepción del producto. Esto garantiza que ambos estén satisfechos con la transacción.'
                    },
                    {
                        'question': '¿Qué pasa si el pago falla?',
                        'answer': 'Si hay problemas con el pago, el sistema automáticamente simula el pago para proyectos universitarios. En producción, MercadoPago maneja los reintentos y notificaciones.'
                    },
                    {
                        'question': '¿Puedo ver el historial de mis pagos?',
                        'answer': 'Sí, puedes ver el historial completo de tus pagos en la sección "Historial de Pagos" de tu perfil. Incluye todos los detalles de cada transacción.'
                    },
                    {
                        'question': '¿Hay comisiones por usar la plataforma?',
                        'answer': 'Para proyectos universitarios, no hay comisiones. En producción, las comisiones son manejadas por MercadoPago según sus tarifas estándar.'
                    }
                ]
            },
            {
                'title': '💬 Comunicación y Mensajería',
                'icon': 'fas fa-comments',
                'color': 'orange',
                'content': [
                    {
                        'question': '¿Cómo me comunico con otros usuarios?',
                        'answer': 'Usa el sistema de mensajes integrado. Puedes iniciar conversaciones desde las publicaciones o desde tus pedidos. Ve a "Mensajes" para ver todas tus conversaciones activas.'
                    },
                    {
                        'question': '¿Recibo notificaciones?',
                        'answer': 'Sí, recibirás notificaciones por nuevos pedidos, mensajes, cambios de estado y pagos procesados. Puedes gestionarlas desde la sección "Notificaciones".'
                    },
                    {
                        'question': '¿Cómo gestiono mis notificaciones?',
                        'answer': 'Ve a "Notificaciones" para ver todas tus alertas. Puedes marcarlas como leídas, eliminarlas, o filtrarlas por categoría (Pedido, Pago, Sistema).'
                    },
                    {
                        'question': '¿Las conversaciones se guardan?',
                        'answer': 'Sí, todas las conversaciones se guardan para que puedas revisar el historial completo. Esto es útil para resolver disputas o recordar acuerdos previos.'
                    },
                    {
                        'question': '¿Puedo enviar archivos en los mensajes?',
                        'answer': 'Actualmente el sistema de mensajes es de texto. Para compartir imágenes o documentos, puedes usar enlaces o contactar al soporte técnico.'
                    },
                    {
                        'question': '¿Cómo reporto problemas con otros usuarios?',
                        'answer': 'Si tienes problemas con otro usuario, puedes usar el sistema de calificaciones para dejar comentarios o contactar al soporte técnico para casos más serios.'
                    }
                ]
            },
            {
                'title': '⭐ Sistema de Calificaciones',
                'icon': 'fas fa-star',
                'color': 'yellow',
                'content': [
                    {
                        'question': '¿Cómo funciona el sistema de calificaciones?',
                        'answer': 'Es un sistema bidireccional donde tanto compradores como vendedores pueden calificarse mutuamente después de completar una transacción.'
                    },
                    {
                        'question': '¿Qué aspectos puedo calificar?',
                        'answer': 'Puedes calificar: comunicación, puntualidad, calidad del producto, y dar una calificación general. También puedes dejar comentarios y recomendar al usuario.'
                    },
                    {
                        'question': '¿Cuándo puedo calificar a alguien?',
                        'answer': 'Solo puedes calificar después de que el pedido esté marcado como "Completado". Esto asegura que ambos hayan tenido la experiencia completa.'
                    },
                    {
                        'question': '¿Puedo ver las calificaciones de otros usuarios?',
                        'answer': 'Sí, puedes ver las calificaciones públicas de otros usuarios en sus perfiles. Esto te ayuda a tomar decisiones informadas sobre con quién hacer negocios.'
                    },
                    {
                        'question': '¿Qué pasa si recibo una calificación injusta?',
                        'answer': 'Si crees que recibiste una calificación injusta, puedes contactar al soporte técnico. Revisamos casos especiales y podemos ayudar a resolver disputas.'
                    },
                    {
                        'question': '¿Las calificaciones afectan mi ranking?',
                        'answer': 'Sí, las calificaciones contribuyen a tu ranking público. Los usuarios con mejores calificaciones aparecen en los rankings de "Top Productores" y "Top Compradores".'
                    }
                ]
            },
            {
                'title': '🔄 Flujo de Trabajo Completo',
                'icon': 'fas fa-sync-alt',
                'color': 'purple',
                'content': [
                    {
                        'question': '¿Cuál es el flujo correcto para empezar a vender?',
                        'answer': '1) Registrarse como comprador → 2) "¿Quieres ser vendedor?" → 3) Crear primera finca → 4) Agregar cultivos → 5) Crear publicaciones → 6) Gestionar ventas'
                    },
                    {
                        'question': '¿Cuál es el flujo para comprar?',
                        'answer': '1) Registrarse como comprador → 2) Explorar marketplace → 3) Agregar al carrito → 4) Hacer pedido → 5) Comunicarse con vendedor → 6) Recibir producto'
                    },
                    {
                        'question': '¿Por qué no puedo publicar sin finca?',
                        'answer': 'Las fincas son OBLIGATORIAS porque garantizan trazabilidad. Los compradores necesitan saber de dónde viene el producto para confiar en la calidad y frescura.'
                    },
                    {
                        'question': '¿Cómo organizo mis productos por finca?',
                        'answer': 'Cada finca tiene sus propios cultivos. Al crear publicaciones, seleccionas la finca y luego el cultivo específico de esa finca. Así mantienes todo organizado.'
                    },
                    {
                        'question': '¿Qué estados puede tener un pedido?',
                        'answer': 'Los pedidos pasan por: Pendiente → Confirmado → En Preparación → Enviado → En Tránsito → Recibido → Completado. Cada estado tiene acciones específicas para compradores y vendedores.'
                    },
                    {
                        'question': '¿Cómo cancelo un pedido?',
                        'answer': 'Los pedidos se pueden cancelar en estados tempranos (Pendiente, Confirmado). Al cancelar, el stock se devuelve automáticamente a la publicación.'
                    }
                ]
            },
            {
                'title': '🛠️ Soporte y Ayuda Técnica',
                'icon': 'fas fa-question-circle',
                'color': 'gray',
                'content': [
                    {
                        'question': '¿Cómo contacto soporte técnico?',
                        'answer': 'Puedes contactarnos a través del sistema de mensajes integrado, enviando un email a soporte@agroconnect.com, o usando el asistente IA para consultas generales.'
                    },
                    {
                        'question': '¿Qué hago si tengo problemas técnicos?',
                        'answer': 'Primero intenta cerrar sesión y volver a entrar. Si el problema persiste, contacta al soporte técnico con detalles específicos del error.'
                    },
                    {
                        'question': '¿Hay tutoriales disponibles?',
                        'answer': 'Esta documentación incluye guías paso a paso. También puedes explorar la plataforma usando las funciones de ayuda integradas y el asistente IA.'
                    },
                    {
                        'question': '¿Cómo reporto un bug?',
                        'answer': 'Si encuentras un bug, puedes reportarlo a través de GitHub Issues o contactar al soporte técnico con detalles específicos sobre cómo reproducir el problema.'
                    },
                    {
                        'question': '¿Ofrecen capacitación para usuarios?',
                        'answer': 'Para proyectos universitarios, ofrecemos sesiones de capacitación. Contacta al soporte técnico para coordinar una sesión de entrenamiento.'
                    },
                    {
                        'question': '¿Qué información necesito para reportar un problema?',
                        'answer': 'Incluye: descripción del problema, pasos para reproducirlo, navegador usado, capturas de pantalla si aplica, y cualquier mensaje de error que hayas visto.'
                    }
                ]
            }
        ]
    }
    
    return render(request, 'core/documentation.html', context)
