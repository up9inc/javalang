import inflection

from . import tree

INDENT = '    '


class Generator():
    def __init__(self):
        self.indent = 0

    def compilation_unit(self, node):
        result = ''
        if node.package:
            result += self.unparse(node.package)
        if node.imports:
            for _node in node.imports:
                result += self.unparse(_node)
        if node.types:
            for _node in node.types:
                result += self.unparse(_node)
        return result

    def class_declaration(self, node):
        result = '\n'
        if node.documentation:
            result += '%s\n' % node.documentation
        for _node in node.annotations:
            result += self.unparse(_node)
        result += '%s' % (self.indent * INDENT)
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        result += ' class %s' % node.name
        if node.implements:
            result += ' %s' % 'implements'
            for _node in node.implements:
                result += ' %s,' % self.unparse(_node)
            result = result[:-1]
        result += '\n{'
        self.indent += 1
        for _node in node.body:
            result += self.unparse(_node)
        self.indent -= 1
        result += '%s}\n\n' % (self.indent * INDENT)
        return result

    def method_declaration(self, node):
        result = '\n'
        if node.documentation:
            result += '%s%s\n' % (self.indent * INDENT, node.documentation)
        for _node in node.annotations:
            result += self.unparse(_node)
        result += '%s' % (self.indent * INDENT)
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        if modifiers:
            result += ' '
        if hasattr(node, 'return_type'):
            if node.return_type is None:
                result += 'void'
            else:
                result += self.unparse(node.return_type)
        else:
            result = result[:-1]
        result += ' %s(' % node.name
        for _node in node.parameters:
            result += '%s, ' % self.unparse(_node)
        if node.parameters:
            result = result[:-2]
        result += ')'
        if node.throws:
            result += ' throws'
            for el in node.throws:
                result += ' %s,' % el
            result = result[:-1]
        if node.body:
            result += '\n%s{\n' % (self.indent * INDENT)
            self.indent += 1
            for _node in node.body:
                result += self.unparse(_node)
            self.indent -= 1
            result += '%s}\n' % (self.indent * INDENT)
        else:
            result += ';\n'
        return result

    def formal_parameter(self, node):
        result = ''
        result += self.unparse(node.type)
        result += ' %s' % node.name
        return result

    def reference_type(self, node):
        result = node.name
        if node.sub_type:
            result += '.%s' % self.unparse(node.sub_type)
        if node.arguments:
            result += '<'
            for _node in node.arguments:
                result += '%s, ' % self.unparse(_node)[1:-1]
            result = result[:-2]
            result += '>'
        if node.dimensions:
            result += '[]' * len(node.dimensions)
        return result

    def statement_expression(self, node):
        result = '%s' % (self.indent * INDENT)
        result += self.unparse(node.expression)
        result += ';\n'
        return result

    def method_invocation(self, node):
        result = ''
        if node.qualifier:
            result += '%s.' % node.qualifier
        result += '%s' % node.member
        result += '('
        for _node in node.arguments:
            result += self.unparse(_node)
            result += ', '
        if node.arguments:
            result = result[:-2]
        result += ')'
        if node.selectors:
            for _node in node.selectors:
                result += '.%s' % self.unparse(_node)
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
        result = ''
        if node.qualifier:
            result += '%s.' % node.qualifier
        if node.selectors:
            selectors = ''
            for _node in node.selectors:
                if _node.__class__.__name__ == 'ArraySelector':
                    selectors += '%s' % self.unparse(_node)
                else:
                    selectors += '.%s' % self.unparse(_node)
            result += '%s%s' % (node.member, selectors)
        else:
            result += node.member
        return result

    def binary_operation(self, node):
        result = ''
        result += self.unparse(node.operandl)
        result += ' %s ' % node.operator
        result += self.unparse(node.operandr)
        return result

    def local_variable_declaration(self, node):
        result = '%s' % (self.indent * INDENT)
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        if modifiers:
            result += ' '
        result += '%s ' % self.unparse(node.type)
        for _node in node.declarators:
            result += self.unparse(_node)
        result += ';\n'
        return result

    def variable_declaration(self, node):
        result = ''
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        if modifiers:
            result += ' '
        result += '%s ' % self.unparse(node.type)
        for _node in node.declarators:
            result += self.unparse(_node)
        return result

    def variable_declarator(self, node):
        result = ''
        result += node.name
        if node.initializer:
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
            else_statement_result = self.unparse(node.else_statement)
            if isinstance(node.else_statement, tree.IfStatement):
                result = result[:-1]
                result += ' %s' % else_statement_result.lstrip()
            else:
                result += else_statement_result
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
        result = ''
        if not node.dimensions:
            result += '%s' % node.name
        else:
            result += '%s[]' % node.name
        return result

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
            return '%s::%s%s' % (
                self.unparse(node.expression),
                type_arguments,
                self.unparse(node.method)
            )

    def type_argument(self, node):
        return '<%s>' % self.unparse(node.type)

    def keyword(self, node):
        return node.value

    def interface_declaration(self, node):
        result = '\ninterface %s\n{\n' % node.name
        self.indent += 1
        for _node in node.body:
            result += self.unparse(_node)
        self.indent -= 1
        result += '%s}\n\n' % (self.indent * INDENT)
        return result

    def class_creator(self, node):
        result = 'new %s(' % self.unparse(node.type)
        for _node in node.arguments:
            result += self.unparse(_node)
        result += ')'
        if node.selectors:
            result += '\n'
            self.indent += 1
            for _node in node.selectors:
                result += '%s.%s\n' % (self.indent * INDENT, self.unparse(_node))
            result = result[:-1]
            self.indent -= 1
        if node.body:
            result += ' '
            node_body = None
            if isinstance(node.body[0], list):
                node_body = node.body[0]
                result += '{'
            else:
                node_body = node.body
            result += '{\n'
            self.indent += 1
            for _node in node_body:
                result += self.unparse(_node)
            self.indent -= 1
            result += '%s}' % (self.indent * INDENT)
            if isinstance(node.body[0], list):
                result += '}'

        return result

    def annotation(self, node):
        result = '%s@%s' % (self.indent * INDENT, node.name)
        if node.element is not None:
            result += '(%s)' % node.element
        result += '\n'
        return result

    def field_declaration(self, node):
        result = '%s' % (self.indent * INDENT)
        modifiers = sorted(list(node.modifiers))
        result += ' '.join(modifiers)
        if modifiers:
            result += ' '
        result += self.unparse(node.type)
        for _node in node.declarators:
            result += ' %s' % self.unparse(_node)
        result += ';\n'
        return result

    def package_declaration(self, node):
        return 'package %s;\n\n' % node.name

    def _import(self, node):
        result = 'import '
        if node.static:
            result += 'static '
        result += '%s;\n' % node.path
        return result

    def try_statement(self, node):
        result = '%stry' % (self.indent * INDENT)
        if node.resources:
            result += ' '
            for _node in node.resources:
                result += self.unparse(_node)
        if node.block:
            result += '\n%s{\n' % (self.indent * INDENT)
            self.indent += 1
            for _node in node.block:
                result += self.unparse(_node)
            self.indent -= 1
            result += '%s}' % (self.indent * INDENT)
        result += '\n'
        if node.catches:
            for _node in node.catches:
                result += self.unparse(_node)
        if node.finally_block:
            result += '%sfinally' % (self.indent * INDENT)
            result += '\n%s{\n' % (self.indent * INDENT)
            self.indent += 1
            for _node in node.finally_block:
                result += self.unparse(_node)
            self.indent -= 1
            result += '%s}\n' % (self.indent * INDENT)
        return result

    def try_resource(self, node):
        result = '('
        result += self.unparse(node.type)
        result += ' %s = ' % node.name
        result += self.unparse(node.value)
        result += ')'
        return result

    def array_initializer(self, node):
        result = '{'
        was_nested = False
        is_empty = True
        for _node in node.initializers:
            if _node.__class__.__name__ == 'ArrayInitializer':
                separator = ','
                if is_empty:
                    separator = ''
                    is_empty = False
                was_nested = True
                self.indent += 1
                result += '%s\n%s%s' % (separator, self.indent * INDENT, self.unparse(_node))
                self.indent -= 1
            else:
                separator = ', '
                if is_empty:
                    separator = ''
                    is_empty = False
                result += '%s%s' % (separator, self.unparse(_node))
        if was_nested:
            result += '\n%s' % (self.indent * INDENT)
        result += '}'
        return result

    def array_selector(self, node):
        return '[%s]' % self.unparse(node.index)

    def catch_clause(self, node):
        result = '%scatch (' % (self.indent * INDENT)
        result += self.unparse(node.parameter)
        result += ')'
        if node.block:
            result += '\n%s{\n' % (self.indent * INDENT)
            self.indent += 1
            for _node in node.block:
                result += self.unparse(_node)
            self.indent -= 1
            result += '%s}' % (self.indent * INDENT)
        result += '\n'
        return result

    def catch_clause_parameter(self, node):
        result = ' '.join(node.types)
        result += ' %s' % node.name
        return result

    def constructor_declaration(self, node):
        return self.method_declaration(node)

    def assignment(self, node):
        result = self.unparse(node.expressionl)
        result += ' %s ' % node.type
        result += self.unparse(node.value)
        return result

    def for_statement(self, node):
        result = '%sfor (' % (self.indent * INDENT)
        result += self.unparse(node.control)
        result += ')\n'
        result += self.unparse(node.body)
        return result

    def enhanced_for_control(self, node):
        return '%s : %s' % (self.unparse(node.var), self.unparse(node.iterable))

    def class_reference(self, node):
        return '%s.class' % self.unparse(node.type)

    def array_creator(self, node):
        result = 'new %s' % self.unparse(node.type)
        if node.dimensions:
            result += '[]' * len(node.dimensions)
        result += self.unparse(node.initializer)
        return result

    def unparse(self, tree):
        node_type = tree.__class__.__name__
        node_type = inflection.underscore(node_type)
        node_type = '_import' if node_type == 'import' else node_type
        # print(node_type)
        # print(tree.__dict__)
        result = getattr(self, node_type)(tree)
        return result


def unparse(tree):
    generator = Generator()
    return generator.unparse(tree)
