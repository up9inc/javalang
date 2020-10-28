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
        result = '%s' % (self.indent * INDENT)
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        result += ' class %s\n{\n' % node.name
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
        if not node.type.dimensions:
            result += ' %s' % node.name
        else:
            result += ' %s[]' % node.name
        return result

    def reference_type(self, node):
        return node.name

    def statement_expression(self, node):
        result = '%s' % (self.indent * INDENT)
        result += self.unparse(node.expression)
        result += ';\n'
        return result

    def method_invocation(self, node):
        result = ''
        result += '%s.%s' % (node.qualifier, node.member)
        result += '('
        for _node in node.arguments:
            result += self.unparse(_node)
        result += ')'
        return result

    def literal(self, node):
        return node.value

    def lambda_expression(self, node):
        result = '('
        for _node in node.parameters:
            result += '%s, ' % self.unparse(_node)
        if node.parameters:
            result = result[:-2]
        result += ') -> '
        if isinstance(node.body, list):
            if not node.body:
                result += '{}'
            else:
                result += '{\n'
                self.indent += 1
                for _node in node.body:
                    result += '%s' % self.unparse(_node)
                self.indent -= 1
                result += '%s}' % (self.indent * INDENT)
        else:
            result += self.unparse(node.body)
        return result

    def member_reference(self, node):
        if node.selectors:
            selectors = ''
            for _node in node.selectors:
                print(node)
                selectors += '.%s' % self.unparse(_node)
            return '%s%s' % (node.member, selectors)
        else:
            return node.member

    def binary_operation(self, node):
        result = ''
        result += self.unparse(node.operandl)
        result += ' %s ' % node.operator
        result += self.unparse(node.operandr)
        return result

    def local_variable_declaration(self, node):
        result = '%s' % (self.indent * INDENT)
        result += '%s ' % self.unparse(node.type)
        for _node in node.declarators:
            result += self.unparse(_node)
        result += ';\n'
        return result

    def variable_declarator(self, node):
        result = ''
        result += node.name
        result += ' = '
        result += self.unparse(node.initializer)
        return result

    def cast(self, node):
        result = ''
        result += '(%s) ' % self.unparse(node.type)
        result += self.unparse(node.expression)
        return result

    def if_statement(self, node):
        result = '%sif (' % (self.indent * INDENT)
        result += self.unparse(node.condition)
        result += ')\n'
        result += self.unparse(node.then_statement)
        if node.else_statement:
            result += '%selse\n' % (self.indent * INDENT)
            result += self.unparse(node.else_statement)
        return result

    def return_statement(self, node):
        result = '%sreturn' % (self.indent * INDENT)
        result += ' %s;\n' % self.unparse(node.expression)
        return result

    def block_statement(self, node):
        result = '%s{\n' % (self.indent * INDENT)
        self.indent += 1
        for _node in node.statements:
            result += self.unparse(_node)
        self.indent -= 1
        result += '%s}\n' % (self.indent * INDENT)
        return result

    def basic_type(self, node):
        return node.name

    def inferred_formal_parameter(self, node):
        return node.name

    def method_reference(self, node):
        if hasattr(node, 'member'):
            return node.member
        else:
            type_arguments = ''
            for _node in node.type_arguments:
                type_arguments += self.unparse(_node)
            if node.type_arguments:
                type_arguments += ' '
            return '%s::%s%s' % (self.unparse(node.expression), type_arguments, self.unparse(node.method))

    def type_argument(self, node):
        return '<%s>' % self.unparse(node.type)

    def keyword(self, node):
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
