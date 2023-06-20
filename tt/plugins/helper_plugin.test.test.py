import unittest
from your_module import YourClass  # Replace with the actual module and class names

class TestHelpCommand(unittest.TestCase):
    def setUp(self):
        self.your_class_instance = YourClass()  # Replace with the actual class instantiation

    def test_help_command_output(self):
        expected_output = (f"{self.your_class_instance.version}\n"
                           f"🕸️ {self.your_class_instance.host_ip}\n"
                           f"🏓 {round(ping3.ping(settings.ping, unit='ms'), 3)}\n"
                           f"{self.your_class_instance.help_message}")
        self.assertEqual(self.your_class_instance.help_command(), expected_output)

if __name__ == '__main__':
    unittest.main()