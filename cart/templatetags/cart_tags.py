from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.tag
def capture_as_var(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("'capture_as_var' node requires one argument")
    
    var_name = bits[1]
    nodelist = parser.parse(('endcapture_as_var',))
    parser.delete_first_token()
    return CaptureAsVarNode(nodelist, var_name)

class CaptureAsVarNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.var_name] = output.strip()
        return ''


@register.filter
def decimal_input(value, decimals=1):
    """
    Formatea un número para inputs HTML type=number garantizando punto decimal.
    """
    try:
        decimals = int(decimals)
    except (TypeError, ValueError):
        decimals = 1

    try:
        number = Decimal(str(value))
        formatted = format(number, f'.{decimals}f')
    except (InvalidOperation, TypeError, ValueError):
        try:
            formatted = format(float(value), f'.{decimals}f')
        except (TypeError, ValueError):
            return ''
    return formatted
