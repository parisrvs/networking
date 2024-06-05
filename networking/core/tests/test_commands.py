"""
Test custom Django management commands
"""

from unittest.mock import patch

from mysql.connector import OperationalError as MySQLOperationalError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """
    Test custom Django management commands
    """
    def test_wait_for_db_ready(self, patched_check):
        """
        Test waiting for db when db is available
        """
        patched_check.return_value = True
        call_command("wait_for_db")
        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for db when getting operational error
        """
        patched_check.side_effect = [MySQLOperationalError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
        self.assertEqual(patched_sleep.call_count, 5)
        patched_sleep.assert_called_with(1)
