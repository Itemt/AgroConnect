from django.shortcuts import render

def documentation_view(request):
    """Vista para mostrar la documentación y FAQ de la plataforma"""
    
    context = {
        'title': 'Documentación y Ayuda',
        'sections': [
            {
                'title': '🏡 Las Fincas: El Centro de Todo',
                'icon': 'fas fa-home',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Por qué las fincas son tan importantes?',
                        'answer': 'Las fincas son el corazón de AgroConnect. Todo gira alrededor de ellas: cultivos, publicaciones, ubicación y trazabilidad. Sin finca, no puedes vender productos.'
                    },
                    {
                        'question': '¿Cómo creo mi primera finca?',
                        'answer': 'Ve a "Mis Fincas" en el sidebar (primera opción) y haz clic en "Agregar Finca". Completa la información de ubicación, área y características de tu finca.'
                    },
                    {
                        'question': '¿Qué puedo hacer desde mis fincas?',
                        'answer': 'Desde tus fincas puedes: agregar cultivos, crear publicaciones, ver la ubicación en el mapa, gestionar inventario y hacer seguimiento de ventas por finca.'
                    },
                    {
                        'question': '¿Puedo tener múltiples fincas?',
                        'answer': '¡Sí! Puedes registrar y gestionar múltiples fincas. Cada finca puede tener diferentes cultivos y ubicaciones. Esto es ideal si tienes terrenos en diferentes lugares.'
                    }
                ]
            },
            {
                'title': '🌱 Gestión de Cultivos desde Fincas',
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
                        'answer': 'Ve a "Mis Publicaciones" y haz clic en "Nueva Publicación". Selecciona la finca, el cultivo de esa finca, cantidad disponible y precio.'
                    },
                    {
                        'question': '¿Por qué debo seleccionar una finca al publicar?',
                        'answer': 'Para mostrar a los compradores la ubicación exacta del producto. Esto genera confianza y permite que vean de dónde viene lo que compran.'
                    },
                    {
                        'question': '¿Cómo manejo mis ventas?',
                        'answer': 'En "Ventas" puedes ver todas tus transacciones, confirmar pedidos y gestionar el estado de tus ventas. Todo está organizado por finca.'
                    }
                ]
            },
            {
                'title': '¿Cómo Comprar en AgroConnect?',
                'icon': 'fas fa-shopping-cart',
                'color': 'blue',
                'content': [
                    {
                        'question': '¿Cómo encuentro productos?',
                        'answer': 'Usa el Marketplace para buscar productos por tipo, ubicación o precio. Puedes filtrar por departamento y ciudad.'
                    },
                    {
                        'question': '¿Cómo hago un pedido?',
                        'answer': 'Selecciona el producto que deseas, especifica la cantidad y haz clic en "Agregar al Carrito". Luego procede al checkout.'
                    },
                    {
                        'question': '¿Cómo pago mis pedidos?',
                        'answer': 'AgroConnect usa MercadoPago para procesar pagos de forma segura. Puedes pagar con tarjeta, transferencia o efectivo.'
                    },
                    {
                        'question': '¿Cómo sigo mi pedido?',
                        'answer': 'Ve a "Mis Pedidos" para ver el estado de tus compras. Recibirás notificaciones cuando cambie el estado.'
                    }
                ]
            },
            {
                'title': 'Sistema de Pagos',
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
                    },
                    {
                        'question': '¿Qué pasa si hay problemas con el pago?',
                        'answer': 'Contacta al soporte técnico. MercadoPago tiene políticas de protección al comprador y vendedor.'
                    }
                ]
            },
            {
                'title': 'Comunicación y Mensajería',
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
                'title': '📍 Información Detallada de Fincas',
                'icon': 'fas fa-map-marker-alt',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Qué información necesito para registrar una finca?',
                        'answer': 'Necesitas: nombre de la finca, departamento, ciudad, dirección, área total, área cultivable, tipo de suelo y tipo de riego. Esta información es crucial para la trazabilidad.'
                    },
                    {
                        'question': '¿Cómo actualizo la información de mi finca?',
                        'answer': 'Ve a "Mis Fincas", selecciona la finca que quieres editar y haz clic en "Editar". Puedes actualizar ubicación, área y cultivos en cualquier momento.'
                    },
                    {
                        'question': '¿Por qué es importante la ubicación de la finca?',
                        'answer': 'La ubicación permite a los compradores saber exactamente de dónde viene el producto, genera confianza y permite calcular costos de transporte.'
                    },
                    {
                        'question': '¿Puedo tener múltiples fincas?',
                        'answer': '¡Sí! Puedes registrar y gestionar múltiples fincas. Cada finca puede tener diferentes cultivos y ubicaciones. Esto es ideal si tienes terrenos en diferentes lugares.'
                    }
                ]
            },
            {
                'title': '🔄 Flujo de Trabajo Centrado en Fincas',
                'icon': 'fas fa-sync-alt',
                'color': 'blue',
                'content': [
                    {
                        'question': '¿Cuál es el flujo correcto para empezar a vender?',
                        'answer': '1) Crear tu primera finca → 2) Agregar cultivos a la finca → 3) Crear publicaciones desde los cultivos → 4) Gestionar ventas. Todo comienza con la finca.'
                    },
                    {
                        'question': '¿Por qué no puedo publicar sin finca?',
                        'answer': 'Las fincas son obligatorias porque garantizan trazabilidad. Los compradores necesitan saber de dónde viene el producto para confiar en la calidad y frescura.'
                    },
                    {
                        'question': '¿Cómo organizo mis productos por finca?',
                        'answer': 'Cada finca tiene sus propios cultivos. Al crear publicaciones, seleccionas la finca y luego el cultivo específico de esa finca. Así mantienes todo organizado.'
                    },
                    {
                        'question': '¿Qué pasa si tengo productos de diferentes fincas?',
                        'answer': 'Perfecto. Puedes tener múltiples fincas y cada una puede tener diferentes cultivos. Al publicar, seleccionas de qué finca viene cada producto específico.'
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
