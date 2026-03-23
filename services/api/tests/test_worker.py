import pytest

def test_worker_settings_loads():
    from app.worker import WorkerSettings
    
    assert WorkerSettings.functions is not None
    assert WorkerSettings.cron_jobs is not None
    assert len(WorkerSettings.cron_jobs) == 3
    
    # Check that they match our intended cron
    job_names = [cj.coroutine_name for cj in WorkerSettings.cron_jobs]
    assert "cron_system_monitor" in job_names
    assert "cron_lead_scout" in job_names
    assert "cron_morning_brief" in job_names
