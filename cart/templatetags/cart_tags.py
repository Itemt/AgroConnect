from django import template

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
