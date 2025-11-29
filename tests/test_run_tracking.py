"""Tests for RunTracker and RunStore implementations."""

import os
import tempfile

from akari.observability.run_tracking import (
    InMemoryRunStore,
    JsonRunStore,
    RunTracker,
)


def test_run_tracking_inmemory() -> None:
    store = InMemoryRunStore()
    tracker = RunTracker(store)

    run_id_1 = tracker.start_run(
        name='iris_rf',
        params={'n_estimators': 10},
        subject='user:alice',
    )
    tracker.log_metric(run_id_1, 'accuracy', 0.9, step=1)
    tracker.end_run(run_id_1, status='completed')

    run_id_2 = tracker.start_run(
        name='iris_rf',
        params={'n_estimators': 50},
        subject='user:alice',
    )
    tracker.log_metric(run_id_2, 'accuracy', 0.95, step=1)
    tracker.end_run(run_id_2, status='completed')

    runs = store.list_runs()
    assert len(runs) == 2

    # Collect the n_estimators values from all runs, order does not matter.
    values = {r.params['n_estimators'] for r in runs}
    assert values == {10, 50}


def test_run_tracking_json_store_persists_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        store = JsonRunStore(tmpdir)
        tracker = RunTracker(store)

        run_id = tracker.start_run(
            name='dummy_run',
            params={'x': 1},
            subject='user:test',
        )
        tracker.end_run(run_id, status='completed')

        path = os.path.join(tmpdir, f'{run_id}.json')
        assert os.path.exists(path)

        # Reload via store.get
        loaded = store.get(run_id)
        assert loaded.id == run_id
        assert loaded.status == 'completed'
