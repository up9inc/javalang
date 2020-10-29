import unittest

from .. import parse, unparse


def setup_java_class(content_to_add):
    """ returns an example java class with the
        given content_to_add contained within a method.
    """
    template = """

public class Lambda
{
    public static void main(String args[])
    {
        %s
    }
}

"""
    return template % content_to_add


class UnparserTestCase(unittest.TestCase):
    def assertUnparse(self, out):
        # print(out)
        out = out[1:]
        tree = parse.parse(out)
        result = unparse.unparse(tree)
        self.assertEqual(out, result)


class LambdaSupportTest(UnparserTestCase):

    """ Contains tests for java 8 lambda syntax. """

    def test_lambda_support_no_parameters_no_body(self):
        """ tests support for lambda with no parameters and no body. """
        self.assertUnparse(setup_java_class("() -> {};"))

    def test_lambda_support_no_parameters_expression_body(self):
        """ tests support for lambda with no parameters and an
            expression body.
        """
        test_classes = [
            setup_java_class("() -> 3;"),
            setup_java_class("() -> null;"),
            setup_java_class("""() -> {
            return 21;
        };"""),
            setup_java_class("""() -> {
            System.exit(1);
        };"""),
        ]
        for test_class in test_classes:
            self.assertUnparse(test_class)

    def test_lambda_support_no_parameters_complex_expression(self):
        """ tests support for lambda with no parameters and a
            complex expression body.
        """
        code = """() -> {
            if (true)
            {
                return 21;
            }
            else
            {
                int result = 21;
                return result / 2;
            }
        };"""
        self.assertUnparse(setup_java_class(code))

    def test_parameter_no_type_expression_body(self):
        """ tests support for lambda with parameters with inferred types. """
        test_classes = [
            setup_java_class("(bar) -> bar + 1;"),
            setup_java_class("(x) -> x.length();"),
            setup_java_class("(y) -> y.boom();"),
        ]
        for test_class in test_classes:
            self.assertUnparse(test_class)

    def test_parameter_with_type_expression_body(self):
        """ tests support for lambda with parameters with formal types. """
        test_classes = [
            setup_java_class("""(int foo) -> {
            return foo + 2;
        };"""),
            setup_java_class("(String s) -> s.length();"),
            setup_java_class("(int foo) -> foo + 1;"),
            setup_java_class("""(Thread th) -> {
            th.start();
        };"""),
            setup_java_class("(String foo, String bar) -> "
                             "foo + bar;"),
        ]
        for test_class in test_classes:
            self.assertUnparse(test_class)

    def test_parameters_with_no_type_expression_body(self):
        """ tests support for multiple lambda parameters
            that are specified without their types.
        """
        self.assertUnparse(setup_java_class("(x, y) -> x + y;"))

    def test_cast_works(self):
        """ this tests that a cast expression works as expected. """
        self.assertUnparse(setup_java_class("String x = (String) A.x();"))


class MethodReferenceSyntaxTest(UnparserTestCase):

    """ Contains tests for java 8 method reference syntax. """

    def test_method_reference(self):
        """ tests that method references are supported. """
        self.assertUnparse(setup_java_class("String::length;"))

    def test_method_reference_to_the_new_method(self):
        """ test support for method references to 'new'. """
        self.assertUnparse(setup_java_class("String::new;"))

    def test_method_reference_to_the_new_method_with_explict_type(self):
        """ test support for method references to 'new' with an
            explicit type.
        """
        self.assertUnparse(setup_java_class("String::<String> new;"))

    def test_method_reference_from_super(self):
        """ test support for method references from 'super'. """
        self.assertUnparse(setup_java_class("super::toString;"))

    def test_method_reference_from_super_with_identifier(self):
        """ test support for method references from Identifier.super. """
        self.assertUnparse(setup_java_class("String.super::toString;"))

    @unittest.expectedFailure
    def test_method_reference_explicit_type_arguments_for_generic_type(self):
        """ currently there is no support for method references
            for an explicit type.
        """
        self.assertUnparse(setup_java_class("List<String>::size;"))

    def test_method_reference_explicit_type_arguments(self):
        """ test support for method references with an explicit type.
        """
        self.assertUnparse(setup_java_class("Arrays::<String> sort;"))

    @unittest.expectedFailure
    def test_method_reference_from_array_type(self):
        """ currently there is no support for method references
            from a primary type.
        """
        self.assertUnparse(setup_java_class("int[]::new;"))


class MethodInvocationSyntaxTest(UnparserTestCase):

    """ Contains tests for java 8 method reference syntax. """

    def test_method_invocation(self):
        """ tests that method invocations are supported. """
        self.assertUnparse(setup_java_class("System.out.println(\"Hello World\");"))


class InterfaceSupportTest(UnparserTestCase):

    """ Contains tests for java 8 interface extensions. """

    def test_interface_support_static_methods(self):
        out = """

interface Foo
{
    void foo();
    static Bar create()
    {
        return new Baz()
        {
            @Override
            void bar()
            {
                System.out.println("baz");
            }
        };
    }
}

"""
        self.assertUnparse(out)

    def test_interface_support_default_methods(self):
        out = """

interface Foo
{
    default void foo()
    {
        System.out.println("foo");
    }
}

"""
        self.assertUnparse(out)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
