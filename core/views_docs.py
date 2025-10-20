from django.shortcuts import render

def documentation_view(request):
    """Vista para mostrar la documentación y FAQ de la plataforma"""
    
    context = {
        'title': 'Documentación y Ayuda',
        'sections': [
            {
                'title': 'Para Compradores',
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
                    }
                ]
            },
            {
                'title': 'Para Vendedores',
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
                    }
                ]
            },
            {
                'title': 'Las Fincas: El Centro de Todo para Vendedores',
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
                    }
                ]
            },
            {
                'title': 'Gestión de Cultivos desde Fincas',
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
                    }
                ]
            },
            {
                'title': '🛒 Publicaciones desde Fincas',
                'icon': 'fas fa-store',
                'color': 'blue',
                'content': [
                    {
                        'question': '¿Cómo publico productos desde mi finca?',
                        'answer': 'Ve a "Mis Publicaciones" y haz clic en "Nueva Publicación". Selecciona la finca, el cultivo de esa finca, cantidad disponible y precio. La ubicación se toma automáticamente de la finca.'
                    },
                    {
                        'question': '¿Por qué debo seleccionar una finca al publicar?',
                        'answer': 'Para mostrar a los compradores la ubicación exacta del producto. Esto genera confianza y permite que vean de dónde viene lo que compran.'
                    },
                    {
                        'question': '¿Cómo manejo mis ventas?',
                        'answer': 'En "Ventas" puedes ver todas tus transacciones, confirmar pedidos y gestionar el estado de tus ventas. Todo está organizado por finca para mejor control.'
                    },
                    {
                        'question': '¿Puedo publicar el mismo cultivo de diferentes fincas?',
                        'answer': '¡Sí! Puedes tener el mismo cultivo en diferentes fincas y crear publicaciones separadas para cada una. Esto te permite mostrar la diversidad de tus ubicaciones.'
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
                'title': '💰 Pagos y Transacciones',
                'icon': 'fas fa-credit-card',
                'color': 'purple',
                'content': [
                    {
                        'question': '¿Qué métodos de pago aceptan?',
                        'answer': 'Aceptamos tarjetas de crédito y débito, transferencias bancarias y pagos en efectivo a través de MercadoPago.'
                    },
                    {
                        'question': '¿Es seguro pagar en AgroConnect?',
                        'answer': 'Sí, usamos MercadoPago que es una plataforma de pagos certificada y segura. Tus datos financieros están protegidos.'
                    },
                    {
                        'question': '¿Cuándo recibo mi dinero como vendedor?',
                        'answer': 'El dinero se libera automáticamente cuando el comprador confirma la recepción del producto.'
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
                        'answer': 'Usa el sistema de mensajes integrado. Ve a "Mensajes" para ver tus conversaciones activas.'
                    },
                    {
                        'question': '¿Recibo notificaciones?',
                        'answer': 'Sí, recibirás notificaciones por nuevos pedidos, mensajes, cambios de estado y pagos procesados.'
                    },
                    {
                        'question': '¿Cómo gestiono mis notificaciones?',
                        'answer': 'Ve a "Notificaciones" para ver todas tus alertas. Puedes marcarlas como leídas o eliminarlas.'
                    }
                ]
            },
            {
                'title': 'Soporte y Ayuda',
                'icon': 'fas fa-question-circle',
                'color': 'gray',
                'content': [
                    {
                        'question': '¿Cómo contacto soporte técnico?',
                        'answer': 'Puedes contactarnos a través del sistema de mensajes o enviando un email a soporte@agroconnect.com'
                    },
                    {
                        'question': '¿Qué hago si tengo problemas técnicos?',
                        'answer': 'Primero intenta cerrar sesión y volver a entrar. Si el problema persiste, contacta al soporte técnico.'
                    },
                    {
                        'question': '¿Hay tutoriales disponibles?',
                        'answer': 'Esta documentación incluye guías paso a paso. También puedes explorar la plataforma usando las funciones de ayuda integradas.'
                    }
                ]
            }
        ]
    }
    
    return render(request, 'core/documentation.html', context)
