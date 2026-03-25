
def test_worker_settings_loads():
    from app.worker import WorkerSettings
    
    assert WorkerSettings.functions is not None
    assert WorkerSettings.cron_jobs is not None
    assert len(WorkerSettings.cron_jobs) == 5
    
    # Check that they match our intended cron
    job_names = [cj.coroutine.__name__ if hasattr(cj, "coroutine") else cj.func.__name__ for cj in WorkerSettings.cron_jobs]
    assert "system_monitor_task" in job_names
    assert "lead_scout_task" in job_names
    assert "morning_brief_task" in job_names
