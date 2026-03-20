#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
<<<<<<< HEAD
=======
import pymysql

pymysql.install_as_MySQLdb()
>>>>>>> 5e49df95f5e11975190813d018b8317677b9918a


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'creart1.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
