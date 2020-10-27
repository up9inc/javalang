import unittest

import javalang


class TestUnparse(unittest.TestCase):
    def test_hello_world(self):
        out = """
class HelloWorld
{
    public static void main(String args[])
    {
        System.out.println("Hello, World");
    }
}

"""
        out = out[1:]
        tree = javalang.parse.parse(out)
        result = javalang.unparse.unparse(tree)
        self.assertEqual(out, result)


if __name__ == "__main__":
    unittest.main()
