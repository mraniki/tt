
import unittest
import ping3
from tt.utils import BasePlugin, send_notification, __version__
from tt.config import logger, settings

from helper_plugin import HelperPlugin  

class TestHelpCommand(unittest.TestCase):
    def setUp(self):
        self.instance = HelperPlugin()  

    def test_help_command_output(self):
        output = self.instance.help_command()
        expected_start = f"{self.instance.version}\n"
        self.assertTrue(output.startswith(expected_start), f"Output should start with '{expected_start}'")

        expected_contains = [f"🕸️ {self.instance.host_ip}\n",
                             f"🏓 {round(ping3.ping(settings.ping, unit='ms'), 3)}\n",
                             f"{self.instance.help_message}"]
        for expected in expected_contains:
            self.assertIn(expected, output, f"Output should contain '{expected}'")

if __name__ == '__main__':
    unittest.main()
