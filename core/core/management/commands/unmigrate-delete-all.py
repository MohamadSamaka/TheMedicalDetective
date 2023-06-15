import os
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Removes migration files and drops tables in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            help='Specify the table name to delete along with its migration files (optional)',
        )

    def handle(self, *args, **options):
        table_name = options.get('table')

        if table_name:
            # Delete migration files and drop a specific table
            self.stdout.write(f"Deleting migration files and dropping table: {table_name}...")
            self.delete_migration_files(table_name)
            self.drop_database_table(table_name)
        else:
            # Delete all migration files and drop all tables
            self.stdout.write("Deleting all migration files and dropping all tables...")
            self.delete_migration_files()
            self.drop_all_database_tables()

        self.stdout.write(self.style.SUCCESS("Successfully removed migration files and dropped tables"))

    def delete_migration_files(self, table_name=None):
        for app_config in apps.get_app_configs():
            migrations_dir = app_config.path + '/migrations'
            if os.path.exists(migrations_dir):
                for root, dirs, files in os.walk(migrations_dir):
                    if 'env' in dirs:
                        dirs.remove('env')

                    for file in files:
                        if file.endswith('.py') and file != '__init__.py':
                            file_path = os.path.join(root, file)
                            if table_name and table_name in file_path:
                                os.remove(file_path)
                                self.stdout.write(f"Deleted migration file: {file_path}")
                            elif not table_name:
                                os.remove(file_path)
                                self.stdout.write(f"Deleted migration file: {file_path}")

    def drop_database_table(self, table_name):
        with connection.cursor() as cursor:
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 1;")
            self.stdout.write(f"Dropped table: {table_name}")

    def drop_all_database_tables(self):
        with connection.cursor() as cursor:
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 0;")
            table_names = connection.introspection.table_names()
            for table_name in table_names:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                self.stdout.write(f"Dropped table: {table_name}")
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 1;")
