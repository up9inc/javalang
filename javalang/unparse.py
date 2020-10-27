import inflection

INDENT = '    '


class Generator():
    def __init__(self):
        self.indent = 0

    def compilation_unit(self, node):
        result = ''
        for _node in node.types:
            result += self.unparse(_node)
        return result

    def class_declaration(self, node):
        result = ''
        result += '%sclass %s\n{\n' % (self.indent * INDENT, node.name)
        self.indent += 1
        for _node in node.body:
            result += self.unparse(_node)
        self.indent -= 1
        result += '%s}\n\n' % (self.indent * INDENT)
        return result

    def method_declaration(self, node):
        result = '%s' % (self.indent * INDENT)
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        if node.return_type == None:
            result += ' void'
        result += ' %s(' % node.name
        for _node in node.parameters:
            result += self.unparse(_node)
        result += ')\n%s{\n' % (self.indent * INDENT)
        self.indent += 1
        for _node in node.body:
            result += self.unparse(_node)
        self.indent -= 1
        result += '%s}\n' % (self.indent * INDENT)
        return result

    def formal_parameter(self, node):
        result = ''
        result += self.unparse(node.type)
        result += ' %s[]' % node.name
        return result

    def reference_type(self, node):
        return node.name

    def statement_expression(self, node):
        result = ''
        result += self.unparse(node.expression)
        return result

    def method_invocation(self, node):
        result = ''
        result += '%s%s.%s' % (self.indent * INDENT, node.qualifier, node.member)
        result += '('
        for _node in node.arguments:
            result += self.unparse(_node)
        result += ');\n'
        return result

    def literal(self, node):
        return node.value

    def unparse(self, tree):
        node_type = tree.__class__.__name__
        node_type = inflection.underscore(node_type)
        # print(node_type)
        # print(tree.__dict__)
        result = getattr(self, node_type)(tree)
        return result

def unparse(tree):
    generator = Generator()
    return generator.unparse(tree)
