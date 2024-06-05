"""
Django command to wait for the database to be available
"""

import time
from mysql.connector import OperationalError as MySQLOperationalError
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for the database"""

    def handle(self, *args, **options):
        """Entrypoint for the command"""
        self.stdout.write('Waiting for database...')
        db_up = False
        while not db_up:
            try:
                result = self.check(databases=["default"])  # pylint: disable=assignment-from-no-return  # noqa
                self.stdout.write(f"Check result {result}")
                db_up = True
            except (MySQLOperationalError, OperationalError) as e:
                self.stdout.write(
                    f'Database unavailable, waiting 1 second...Error {e}'
                )
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS('Database available!')  # pylint: disable=no-member  # noqa
        )
