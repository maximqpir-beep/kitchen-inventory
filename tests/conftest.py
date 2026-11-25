from pathlib import Path

from django.core.management import call_command
import pytest


@pytest.fixture
def inventory_db(db, settings):
    settings.DEBUG = False
    source = Path(__file__).resolve().parents[1] / 'data/inventory.sqlite'
    call_command('import_legacy', source=source, verbosity=0)
