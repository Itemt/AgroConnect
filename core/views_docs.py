from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def documentation_view(request):
    """Vista para mostrar la documentación y FAQ de la plataforma"""
    
    context = {
        'title': 'Documentación y Ayuda',
        'sections': [
            {
                'title': '¿Cómo Vender en AgroConnect?',
                'icon': 'fas fa-store',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Cómo me registro como vendedor?',
                        'answer': 'Al registrarte, marca la opción "Quiero vender productos" en el formulario de registro. Esto te dará acceso a las herramientas de venta.'
                    },
                    {
                        'question': '¿Cómo creo mi primera finca?',
                        'answer': 'Ve a "Mis Fincas" en el sidebar y haz clic en "Agregar Finca". Completa la información de ubicación, área y características de tu finca.'
                    },
                    {
                        'question': '¿Cómo publico mis productos?',
                        'answer': 'Ve a "Mis Publicaciones" y haz clic en "Nueva Publicación". Selecciona la finca, el cultivo, cantidad disponible y precio.'
                    },
                    {
                        'question': '¿Cómo manejo mis ventas?',
                        'answer': 'En "Ventas" puedes ver todas tus transacciones, confirmar pedidos y gestionar el estado de tus ventas.'
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
                'title': 'Gestión de Fincas',
                'icon': 'fas fa-tractor',
                'color': 'green',
                'content': [
                    {
                        'question': '¿Puedo tener múltiples fincas?',
                        'answer': 'Sí, puedes registrar y gestionar múltiples fincas desde "Mis Fincas". Cada finca puede tener diferentes cultivos.'
                    },
                    {
                        'question': '¿Cómo actualizo la información de mi finca?',
                        'answer': 'Ve a "Mis Fincas", selecciona la finca que quieres editar y haz clic en "Editar". Puedes actualizar ubicación, área y cultivos.'
                    },
                    {
                        'question': '¿Qué información necesito para registrar una finca?',
                        'answer': 'Necesitas: nombre de la finca, departamento, ciudad, dirección, área total, área cultivable, tipo de suelo y tipo de riego.'
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
