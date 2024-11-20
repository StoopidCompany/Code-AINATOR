import unittest
from unittest.mock import patch
import io
from codeainator.cli import main

class TestCLI(unittest.TestCase):

    @patch('sys.argv', ['codeainator', '-h'])
    def test_help_shows(self):
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            with self.assertRaises(SystemExit):
                main()
            output = mock_stdout.getvalue()
            self.assertIn("usage: codeainator [-h]", output)

if __name__ == '__main__':
    unittest.main()