from unittest.mock import call, patch

import pytest

from django.core.management import call_command


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.distributed_migrate.advisory_lock')
def test_distributed_migration(mocked_advisory_lock, mocked_handle):
    call_command('distributed_migrate')
    assert mocked_handle.call_count == 1
    assert mocked_advisory_lock.call_args == call(
        lock_id='migrations', shared=False, wait=True
    )


@pytest.mark.django_db
@patch(
    'core.management.commands.distributed_elasticsearch_migrate.'
    'MigrateCommand.handle'
)
@patch(
    'core.management.commands.distributed_elasticsearch_migrate.advisory_lock'
)
def test_distributed_migration_elasticsearch(
    mocked_advisory_lock, mocked_handle
):
    call_command('distributed_elasticsearch_migrate')
    assert mocked_handle.call_count == 1
    assert mocked_advisory_lock.call_args == call(
        lock_id='es_migrations', shared=False, wait=True
    )
