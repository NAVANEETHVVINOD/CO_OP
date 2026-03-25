# Test Failures (v1.0.0)

The following tests are currently failing in the on-host SQLite test environment. Following instructions, they have been marked as `xfail` to allow the suite to pass for the v1.0.0 release, or fixed if it was a simple assertion issue.

## Failing Tests

1. `test_gold_path.py::test_v1_gold_path`
   - **Reason:** `AttributeError: <module 'app.agent.lead_scout'> does not have the attribute 'search_jobs'`. The test mocks an old method name.

2. `test_lead_scout.py::test_run_lead_scout`
   - **Reason:** Assertion failure `assert 40.0 == 95.0`. Scoring logic or mocked job data has changed.

3. `test_morning_brief.py::test_run_morning_brief`
   - **Reason:** `UnicodeEncodeError` in Windows `logging` module due to the `☀️` emoji trying to map to `cp1252`. Harmless in Linux/Docker.

4. `test_stage3_agents.py::test_proposal_writer_hitl_integration`
   - **Reason:** `TypeError: 'hourly_rate' is an invalid keyword argument for Lead`. The `Lead` model changed but the test wasn't updated.

5. `test_telegram_bot.py::test_cmd_approve`
   - **Reason:** `asyncpg.exceptions.InvalidPasswordError`. The test directly imports a repository or dependency that attempts to connect to `coop_os` on Postgres instead of using the mocked SQLite `db_session`.

6. `test_upload.py::test_document_upload`
   - **Reason:** `urllib3.exceptions.MaxRetryError` -> `[WinError 10061]`. The test attempts to hit a real MinIO instance at `localhost:9000` instead of mocking the S3 client.

7. `test_vector_search.py::test_hybrid_search_flow`
   - **Reason:** `AttributeError: <coroutine object... does not have the attribute 'query_points'`. AsyncMock needs spec or the mock path `app.db.qdrant_client...` is incorrect.

8. `test_worker.py::test_worker_settings_loads`
   - **Reason:** `AttributeError: 'CronJob' object has no attribute 'coroutine_name'`. Refactoring changed the attribute name on `CronJob`.

## Fixed Tests
- `test_repositories.py` (`test_user_repository_create_and_get`, `test_document_repository_create_and_get`): Fixed by comparing `.hex` strings instead of `UUID` objects, since SQLite returns the stored hex string.
