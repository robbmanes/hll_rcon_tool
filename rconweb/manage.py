#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rconweb.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    # Make all the endpoints be exposed at startup to catch any crashing issues
    if not os.getenv("HLL_MAINTENANCE_CONTAINER") and not os.getenv(
        "HLL_WH_SERVICE_CONTAINER"
    ):
        import api.views


if __name__ == "__main__":
    main()
