============================= test session starts =============================
platform win32 -- Python 3.12.9, pytest-8.2.1, pluggy-1.5.0 -- C:\Users\PC\miniconda3\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: F:\kannan\projects\CO_OS\services\api
configfile: pyproject.toml
plugins: anyio-4.12.0, hypothesis-6.148.7, langsmith-0.7.22, asyncio-1.3.0, mock-3.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 45 items

tests/test_approvals.py::test_approvals_flow PASSED                      [  2%]
tests/test_auth.py::test_auth_login_success PASSED                       [  4%]
tests/test_auth.py::test_auth_full_flow PASSED                           [  6%]
tests/test_chat.py::test_chat_stream PASSED                              [  8%]
tests/test_credits.py::test_get_costs_with_data PASSED                   [ 11%]
tests/test_gold_path.py::test_v1_gold_path FAILED                        [ 13%]
tests/test_hardware_detector.py::test_detect_and_store_hardware PASSED   [ 15%]
tests/test_health.py::test_health_check PASSED                           [ 17%]
tests/test_invoices.py::test_list_invoices PASSED                        [ 20%]
tests/test_lead_scout.py::test_run_lead_scout FAILED                     [ 22%]
tests/test_morning_brief.py::test_run_morning_brief FAILED               [ 24%]
tests/test_parser.py::test_parse_text PASSED                             [ 26%]
tests/test_parser.py::test_parse_text_utf8 PASSED                        [ 28%]
tests/test_parser.py::test_parse_unsupported PASSED                      [ 31%]
tests/test_parser.py::test_parse_routing_txt PASSED                      [ 33%]
tests/test_parser.py::test_parse_routing_md PASSED                       [ 35%]
tests/test_parser.py::test_parse_pdf_mock PASSED                         [ 37%]
tests/test_parser.py::test_parse_docx_mock PASSED                        [ 40%]
tests/test_projects.py::test_list_projects PASSED                        [ 42%]
tests/test_projects.py::test_milestone_completion PASSED                 [ 44%]
tests/test_rag_pipeline.py::test_chunker_basic PASSED                    [ 46%]
tests/test_rag_pipeline.py::test_bm25_encoder PASSED                     [ 48%]
tests/test_repositories.py::test_user_repository_create_and_get FAILED   [ 51%]
tests/test_repositories.py::test_document_repository_create_and_get FAILED [ 53%]
tests/test_repositories.py::test_audit_repository_append_event PASSED    [ 55%]
tests/test_search.py::test_search_endpoint PASSED                        [ 57%]
tests/test_settings.py::test_get_settings_hardware PASSED                [ 60%]
tests/test_stage3_agents.py::test_proposal_writer_hitl_integration FAILED [ 62%]
tests/test_stage3_agents.py::test_finance_manager_billing_flow PASSED    [ 64%]
tests/test_stage3_agents.py::test_project_tracker_alerts PASSED          [ 66%]
tests/test_system_monitor.py::test_run_system_monitor_all_healthy PASSED [ 68%]
tests/test_system_monitor.py::test_run_system_monitor_failure PASSED     [ 71%]
tests/test_telegram_bot.py::test_cmd_start PASSED                        [ 73%]
tests/test_telegram_bot.py::test_cmd_help PASSED                         [ 75%]
tests/test_telegram_bot.py::test_cmd_status PASSED                       [ 77%]
tests/test_telegram_bot.py::test_cmd_budget PASSED                       [ 80%]
tests/test_telegram_bot.py::test_cmd_pause PASSED                        [ 82%]
tests/test_telegram_bot.py::test_cmd_resume PASSED                       [ 84%]
tests/test_telegram_bot.py::test_cmd_panic PASSED                        [ 86%]
tests/test_telegram_bot.py::test_cmd_approve FAILED                      [ 88%]
tests/test_upload.py::test_document_upload FAILED                        [ 91%]
tests/test_vector_search.py::test_compute_rrf_simple PASSED              [ 93%]
tests/test_vector_search.py::test_compute_rrf_weighted PASSED            [ 95%]
tests/test_vector_search.py::test_hybrid_search_flow FAILED              [ 97%]
tests/test_worker.py::test_worker_settings_loads FAILED                  [100%]

================================== FAILURES ===================================
______________________________ test_v1_gold_path ______________________________
tests\test_gold_path.py:23: in test_v1_gold_path
    mocker.patch("app.agent.lead_scout.search_jobs", return_value=[{
C:\Users\PC\miniconda3\Lib\site-packages\pytest_mock\plugin.py:448: in __call__
    return self._start_patch(
C:\Users\PC\miniconda3\Lib\site-packages\pytest_mock\plugin.py:266: in _start_patch
    mocked: MockType = p.start()
C:\Users\PC\miniconda3\Lib\unittest\mock.py:1624: in start
    result = self.__enter__()
C:\Users\PC\miniconda3\Lib\unittest\mock.py:1467: in __enter__
    original, local = self.get_original()
C:\Users\PC\miniconda3\Lib\unittest\mock.py:1437: in get_original
    raise AttributeError(
E   AttributeError: <module 'app.agent.lead_scout' from 'F:\\kannan\\projects\\CO_OS\\services\\api\\app\\agent\\lead_scout.py'> does not have the attribute 'search_jobs'
_____________________________ test_run_lead_scout _____________________________
tests\test_lead_scout.py:51: in test_run_lead_scout
    assert leads[0].score == 95.0
E   assert 40.0 == 95.0
E    +  where 40.0 = <app.db.models.Lead object at 0x000001A5C0DBCBF0>.score
---------------------------- Captured stdout call -----------------------------
Lead Scout starting...
Upwork RSS returned 404
Using simulated job data (Upwork RSS blocked)
Vector search failed: 'coroutine' object has no attribute 'search'
Vector search failed: 'coroutine' object has no attribute 'search'
Vector search failed: 'coroutine' object has no attribute 'search'
Vector search failed: 'coroutine' object has no attribute 'search'
Vector search failed: 'coroutine' object has no attribute 'search'
Lead Scout complete: 5 jobs scored, top score: 40
------------------------------ Captured log call ------------------------------
INFO     app.agent.lead_scout:lead_scout.py:172 Lead Scout starting...
WARNING  app.agent.lead_scout:lead_scout.py:59 Upwork RSS returned 404
INFO     app.agent.lead_scout:lead_scout.py:65 Using simulated job data (Upwork RSS blocked)
ERROR    app.services.vector_search:vector_search.py:48 Vector search failed: 'coroutine' object has no attribute 'search'
ERROR    app.services.vector_search:vector_search.py:48 Vector search failed: 'coroutine' object has no attribute 'search'
ERROR    app.services.vector_search:vector_search.py:48 Vector search failed: 'coroutine' object has no attribute 'search'
ERROR    app.services.vector_search:vector_search.py:48 Vector search failed: 'coroutine' object has no attribute 'search'
ERROR    app.services.vector_search:vector_search.py:48 Vector search failed: 'coroutine' object has no attribute 'search'
INFO     app.agent.lead_scout:lead_scout.py:258 Lead Scout complete: 5 jobs scored, top score: 40
___________________________ test_run_morning_brief ____________________________
tests\test_morning_brief.py:42: in test_run_morning_brief
    assert "1 found in last 24h" in message
E   AssertionError: assert '1 found in last 24h' in '\u2600\ufe0f *Co-Op Morning Brief*\\n\\n\U0001f3af *New Leads*: 6 found in last 24h\\n\U0001f3e5 *System Health*: 0/0 services OK\\n\U0001f4b0 *Token Usage*: 1,100 tokens ($4.0000)\\n\\n_Report generated at 04:57 UTC_'
---------------------------- Captured stdout call -----------------------------
Generating morning brief...\nMorning brief sent to Telegram.\nMorning brief:\n\u2600\ufe0f *Co-Op Morning Brief*\n\n\U0001f3af *New Leads*: 6 found in last 24h\n\U0001f3e5 *System Health*: 0/0 services OK\n\U0001f4b0 *Token Usage*: 1,100 tokens ($4.0000)\n\n_Report generated at 04:57 UTC_
---------------------------- Captured stderr call -----------------------------
--- Logging error ---\nTraceback (most recent call last):\n  File "C:\\Users\\PC\\miniconda3\\Lib\\logging\\__init__.py", line 1163, in emit\n    stream.write(msg + self.terminator)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\encodings\\cp1252.py", line 19, in encode\n    return codecs.charmap_encode(input,self.errors,encoding_table)[0]\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nUnicodeEncodeError: 'charmap' codec can't encode characters in position 16-17: character maps to <undefined>\nCall stack:\n  File "<frozen runpy>", line 198, in _run_module_as_main\n  File "<frozen runpy>", line 88, in _run_code\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pytest\\__main__.py", line 7, in <module>\n    raise SystemExit(pytest.console_main())\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\config\\__init__.py", line 206, in console_main\n    code = main()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\config\\__init__.py", line 178, in main\n    ret: Union[ExitCode, int] = config.hook.pytest_cmdline_main(\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_hooks.py", line 513, in __call__\n    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_manager.py", line 120, in _hookexec\n    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_callers.py", line 103, in _multicall\n    res = hook_impl.function(*args)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\main.py", line 332, in pytest_cmdline_main\n    return wrap_session(config, _main)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\main.py", line 285, in wrap_session\n    session.exitstatus = doit(config, session) or 0\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\main.py", line 339, in _main\n    config.hook.pytest_runtestloop(session=session)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_hooks.py", line 513, in __call__\n    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_manager.py", line 120, in _hookexec\n    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_callers.py", line 103, in _multicall\n    res = hook_impl.function(*args)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\main.py", line 364, in pytest_runtestloop\n    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_hooks.py", line 513, in __call__\n    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_manager.py", line 120, in _hookexec\n    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_callers.py", line 103, in _multicall\n    res = hook_impl.function(*args)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\runner.py", line 116, in pytest_runtest_protocol\n    runtestprotocol(item, nextitem=nextitem)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\runner.py", line 135, in runtestprotocol\n    reports.append(call_and_report(item, "call", log))\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\runner.py", line 240, in call_and_report\n    call = CallInfo.from_call(\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\runner.py", line 341, in from_call\n    result: Optional[TResult] = func()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\runner.py", line 241, in <lambda>\n    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_hooks.py", line 513, in __call__\n    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_manager.py", line 120, in _hookexec\n    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_callers.py", line 103, in _multicall\n    res = hook_impl.function(*args)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\runner.py", line 173, in pytest_runtest_call\n    item.runtest()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pytest_asyncio\\plugin.py", line 469, in runtest\n    super().runtest()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\python.py", line 1632, in runtest\n    self.ihook.pytest_pyfunc_call(pyfuncitem=self)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_hooks.py", line 513, in __call__\n    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_manager.py", line 120, in _hookexec\n    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pluggy\\_callers.py", line 103, in _multicall\n    res = hook_impl.function(*args)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\_pytest\\python.py", line 162, in pytest_pyfunc_call\n    result = testfunction(**testargs)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\site-packages\\pytest_asyncio\\plugin.py", line 716, in inner\n    runner.run(coro, context=context)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\asyncio\\runners.py", line 118, in run\n    return self._loop.run_until_complete(task)\n  File "C:\\Users\\PC\\miniconda3\\Lib\\asyncio\\base_events.py", line 678, in run_until_complete\n    self.run_forever()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\asyncio\\windows_events.py", line 322, in run_forever\n    super().run_forever()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\asyncio\\base_events.py", line 645, in run_forever\n    self._run_once()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\asyncio\\base_events.py", line 1999, in _run_once\n    handle._run()\n  File "C:\\Users\\PC\\miniconda3\\Lib\\asyncio\\events.py", line 88, in _run\n    self._context.run(self._callback, *self._args)\n  File "F:\\kannan\\projects\\CO_OS\\services\\api\\tests\\test_morning_brief.py", line 35, in test_run_morning_brief\n    await run_morning_brief()\n  File "F:\\kannan\\projects\\CO_OS\\services\\api\\app\\crons\\morning_brief.py", line 84, in run_morning_brief\n    logger.info(f"Morning brief:\\n{brief}")\nMessage: 'Morning brief:\\n\u2600\ufe0f *Co-Op Morning Brief*\\n\\n\U0001f3af *New Leads*: 6 found in last 24h\\n\U0001f3e5 *System Health*: 0/0 services OK\\n\U0001f4b0 *Token Usage*: 1,100 tokens ($4.0000)\\n\\n_Report generated at 04:57 UTC_'\nArguments: ()
------------------------------ Captured log call ------------------------------
INFO     app.crons.morning_brief:morning_brief.py:15 Generating morning brief...\nINFO     app.crons.morning_brief:morning_brief.py:79 Morning brief sent to Telegram.\nINFO     app.crons.morning_brief:morning_brief.py:84 Morning brief:\n\u2600\ufe0f *Co-Op Morning Brief*\n\n\U0001f3af *New Leads*: 6 found in last 24h\n\U0001f3e5 *System Health*: 0/0 services OK\n\U0001f4b0 *Token Usage*: 1,100 tokens ($4.0000)\n\n_Report generated at 04:57 UTC_
_____________________ test_user_repository_create_and_get _____________________
tests\test_repositories.py:34: in test_user_repository_create_and_get
    assert fetched_by_email.id == user.id
E   AssertionError: assert 'f0c4a8cc843e4fde972a0ab0dd4e103a' == UUID('f0c4a8cc-843e-4fde-972a-0ab0dd4e103a')
E    +  where 'f0c4a8cc843e4fde972a0ab0dd4e103a' = <app.db.models.User object at 0x000001A5C0AD4BC0>.id
E    +  and   UUID('f0c4a8cc-843e-4fde-972a-0ab0dd4e103a') = <app.db.models.User object at 0x000001A5C0E0EE40>.id
___________________ test_document_repository_create_and_get ___________________
tests\test_repositories.py:54: in test_document_repository_create_and_get
    assert fetched.id == doc.id
E   AssertionError: assert '6c25207f0ff64bd8a48f9b82f4d32110' == UUID('6c25207f-0ff6-4bd8-a48f-9b82f4d32110')
E    +  where '6c25207f0ff64bd8a48f9b82f4d32110' = <app.db.models.Document object at 0x000001A5C0AD6930>.id
E    +  and   UUID('6c25207f-0ff6-4bd8-a48f-9b82f4d32110') = <app.db.models.Document object at 0x000001A5C0E1F230>.id
____________________ test_proposal_writer_hitl_integration ____________________
tests\test_stage3_agents.py:14: in test_proposal_writer_hitl_integration
    lead = Lead(
<string>:4: in __init__
    ???
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\state.py:596: in _initialize_instance
    with util.safe_reraise():
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\util\langhelpers.py:224: in __exit__
    raise exc_value.with_traceback(exc_tb)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\decl_base.py:2179: in _declarative_constructor
    raise TypeError(
E   TypeError: 'hourly_rate' is an invalid keyword argument for Lead
______________________________ test_cmd_approve _______________________________
tests\test_telegram_bot.py:84: in test_cmd_approve
    await cmd_approve(update, context)
app\communication\telegram.py:140: in cmd_approve
    result = await session.execute(
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\ext\asyncio\session.py:449: in execute
    result = await greenlet_spawn(
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\util\_concurrency_py3k.py:201: in greenlet_spawn
    result = context.throw(*sys.exc_info())
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\session.py:2351: in execute
    return self._execute_internal(
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\session.py:2239: in _execute_internal
    conn = self._connection_for_bind(bind)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\session.py:2108: in _connection_for_bind
    return trans._connection_for_bind(engine, execution_options)
<string>:2: in _connection_for_bind
    ???
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\state_changes.py:137: in _go
    ret_value = fn(self, *arg, **kw)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\orm\session.py:1187: in _connection_for_bind
    conn = bind.connect()
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\engine\base.py:3285: in connect
    return self._connection_cls(self)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\engine\base.py:143: in __init__
    self._dbapi_connection = engine.raw_connection()
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\engine\base.py:3309: in raw_connection
    return self.pool.connect()
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:447: in connect
    return _ConnectionFairy._checkout(self)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:1264: in _checkout
    fairy = _ConnectionRecord.checkout(pool)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:711: in checkout
    rec = pool._do_get()
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\impl.py:177: in _do_get
    with util.safe_reraise():
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\util\langhelpers.py:224: in __exit__
    raise exc_value.with_traceback(exc_tb)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\impl.py:175: in _do_get
    return self._create_connection()
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:388: in _create_connection
    return _ConnectionRecord(self)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:673: in __init__
    self.__connect()
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:899: in __connect
    with util.safe_reraise():
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\util\langhelpers.py:224: in __exit__
    raise exc_value.with_traceback(exc_tb)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\pool\base.py:895: in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\engine\create.py:661: in connect
    return dialect.connect(*cargs, **cparams)
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\engine\default.py:630: in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)  # type: ignore[no-any-return]  # NOQA: E501
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\dialects\postgresql\asyncpg.py:955: in connect
    await_only(creator_fn(*arg, **kw)),
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\util\_concurrency_py3k.py:132: in await_only
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501
C:\Users\PC\miniconda3\Lib\site-packages\sqlalchemy\util\_concurrency_py3k.py:196: in greenlet_spawn
    value = await result
C:\Users\PC\miniconda3\Lib\site-packages\asyncpg\connection.py:2443: in connect
    return await connect_utils._connect(
C:\Users\PC\miniconda3\Lib\site-packages\asyncpg\connect_utils.py:1218: in _connect
    conn = await _connect_addr(
C:\Users\PC\miniconda3\Lib\site-packages\asyncpg\connect_utils.py:1054: in _connect_addr
    return await __connect_addr(params, True, *args)
C:\Users\PC\miniconda3\Lib\site-packages\asyncpg\connect_utils.py:1102: in __connect_addr
    await connected
E   asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "test"
____________________________ test_document_upload _____________________________
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connection.py:198: in _new_conn
    sock = connection.create_connection(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:787: in urlopen
    response = self._make_request(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connection.py:445: in request
    self.endheaders()
C:\Users\PC\miniconda3\Lib\http\client.py:1333: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
C:\Users\PC\miniconda3\Lib\http\client.py:1093: in _send_output
    self.send(msg)
C:\Users\PC\miniconda3\Lib\http\client.py:1037: in send
    self.connect()
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connection.py:276: in connect
    self.sock = self._new_conn()
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connection.py:213: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPConnection object at 0x000001A5C0A64E30>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
tests\test_upload.py:38: in test_document_upload
    upload_resp = await async_client.post(
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_client.py:1859: in post
    return await self.request(
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_client.py:1540: in request
    return await self.send(request, auth=auth, follow_redirects=follow_redirects)
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_client.py:1629: in send
    response = await self._send_handling_auth(
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_client.py:1657: in _send_handling_auth
    response = await self._send_handling_redirects(
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_client.py:1694: in _send_handling_redirects
    response = await self._send_single_request(request)
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_client.py:1730: in _send_single_request
    response = await transport.handle_async_request(request)
C:\Users\PC\miniconda3\Lib\site-packages\httpx\_transports\asgi.py:170: in handle_async_request
    await self.app(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\fastapi\applications.py:1159: in __call__
    await super().__call__(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\middleware\errors.py:186: in __call__
    raise exc
C:\Users\PC\miniconda3\Lib\site-packages\starlette\middleware\errors.py:164: in __call__
    await self.app(scope, receive, _send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\middleware\cors.py:87: in __call__
    await self.app(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\prometheus_fastapi_instrumentator\middleware.py:177: in __call__
    raise exc
C:\Users\PC\miniconda3\Lib\site-packages\prometheus_fastapi_instrumentator\middleware.py:175: in __call__
    await self.app(scope, receive, send_wrapper)
C:\Users\PC\miniconda3\Lib\site-packages\asgi_correlation_id\middleware.py:90: in __call__
    await self.app(scope, receive, handle_outgoing_request)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\middleware\exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\_exception_handler.py:53: in wrapped_app
    raise exc
C:\Users\PC\miniconda3\Lib\site-packages\starlette\_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
C:\Users\PC\miniconda3\Lib\site-packages\fastapi\middleware\asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\routing.py:736: in app
    await route.handle(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\routing.py:290: in handle
    await self.app(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\fastapi\routing.py:134: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
C:\Users\PC\miniconda3\Lib\site-packages\starlette\_exception_handler.py:53: in wrapped_app
    raise exc
C:\Users\PC\miniconda3\Lib\site-packages\starlette\_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
C:\Users\PC\miniconda3\Lib\site-packages\fastapi\routing.py:120: in app
    response = await f(request)
C:\Users\PC\miniconda3\Lib\site-packages\fastapi\routing.py:674: in app
    raw_response = await run_endpoint_function(
C:\Users\PC\miniconda3\Lib\site-packages\fastapi\routing.py:328: in run_endpoint_function
    return await dependant.call(**values)
app\routers\documents.py:33: in upload_document
    upload_success = upload_file("raw-documents", object_name, file_content, content_type=file.content_type)
app\core\minio_client.py:31: in upload_file
    minio_client.put_object(
C:\Users\PC\miniconda3\Lib\site-packages\minio\api.py:2015: in put_object
    raise exc
C:\Users\PC\miniconda3\Lib\site-packages\minio\api.py:1960: in put_object
    return self._put_object(
C:\Users\PC\miniconda3\Lib\site-packages\minio\api.py:1789: in _put_object
    response = self._execute(
C:\Users\PC\miniconda3\Lib\site-packages\minio\api.py:441: in _execute
    region = self._get_region(bucket_name)
C:\Users\PC\miniconda3\Lib\site-packages\minio\api.py:498: in _get_region
    response = self._url_open(
C:\Users\PC\miniconda3\Lib\site-packages\minio\api.py:306: in _url_open
    response = self._http.urlopen(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\poolmanager.py:443: in urlopen
    response = conn.urlopen(method, u.request_uri, **kw)
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:871: in urlopen
    return self.urlopen(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:871: in urlopen
    return self.urlopen(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:871: in urlopen
    return self.urlopen(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:871: in urlopen
    return self.urlopen(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:871: in urlopen
    return self.urlopen(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\connectionpool.py:841: in urlopen
    retries = retries.increment(
C:\Users\PC\miniconda3\Lib\site-packages\urllib3\util\retry.py:519: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9000): Max retries exceeded with url: /raw-documents?location= (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A64E30>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
---------------------------- Captured stdout call -----------------------------
HTTP Request: POST http://test/v1/auth/token "HTTP/1.1 200 OK"
Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A656D0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A66780>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A65730>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A67FE0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A67EC0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
------------------------------ Captured log call ------------------------------
INFO     httpx:_client.py:1740 HTTP Request: POST http://test/v1/auth/token "HTTP/1.1 200 OK"
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A656D0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A66780>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A65730>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A67FE0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A5C0A67EC0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it')': /raw-documents?location=
___________________________ test_hybrid_search_flow ___________________________
tests\test_vector_search.py:47: in test_hybrid_search_flow
    mock_qdrant = mocker.patch("app.db.qdrant_client.qdrant.query_points")
C:\Users\PC\miniconda3\Lib\site-packages\pytest_mock\plugin.py:448: in __call__
    return self._start_patch(
C:\Users\PC\miniconda3\Lib\site-packages\pytest_mock\plugin.py:266: in _start_patch
    mocked: MockType = p.start()
C:\Users\PC\miniconda3\Lib\unittest\mock.py:1624: in start
    result = self.__enter__()
C:\Users\PC\miniconda3\Lib\unittest\mock.py:1467: in __enter__
    original, local = self.get_original()
C:\Users\PC\miniconda3\Lib\unittest\mock.py:1437: in get_original
    raise AttributeError(
E   AttributeError: <coroutine object AsyncMockMixin._execute_mock_call at 0x000001A5BCC00640> does not have the attribute 'query_points'
_________________________ test_worker_settings_loads __________________________
tests\test_worker.py:11: in test_worker_settings_loads
    job_names = [cj.coroutine_name for cj in WorkerSettings.cron_jobs]
E   AttributeError: 'CronJob' object has no attribute 'coroutine_name'
============================== warnings summary ===============================
<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: Type google._upb._message.MessageMapContainer uses PyType_Spec with a metaclass that has custom tp_new. This is deprecated and will no longer be allowed in Python 3.14.

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: Type google._upb._message.ScalarMapContainer uses PyType_Spec with a metaclass that has custom tp_new. This is deprecated and will no longer be allowed in Python 3.14.

tests/test_stage3_agents.py::test_finance_manager_billing_flow
  F:\kannan\projects\CO_OS\services\api\tests\test_stage3_agents.py:52: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    due_date=datetime.utcnow() - timedelta(days=1)

tests/test_stage3_agents.py::test_project_tracker_alerts
  F:\kannan\projects\CO_OS\services\api\tests\test_stage3_agents.py:81: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    due_date=datetime.utcnow() + timedelta(hours=48)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_gold_path.py::test_v1_gold_path - AttributeError: <module '...
FAILED tests/test_lead_scout.py::test_run_lead_scout - assert 40.0 == 95.0
FAILED tests/test_morning_brief.py::test_run_morning_brief - AssertionError: ...
FAILED tests/test_repositories.py::test_user_repository_create_and_get - Asse...
FAILED tests/test_repositories.py::test_document_repository_create_and_get - ...
FAILED tests/test_stage3_agents.py::test_proposal_writer_hitl_integration - T...
FAILED tests/test_telegram_bot.py::test_cmd_approve - asyncpg.exceptions.Inva...
FAILED tests/test_upload.py::test_document_upload - urllib3.exceptions.MaxRet...
FAILED tests/test_vector_search.py::test_hybrid_search_flow - AttributeError:...
FAILED tests/test_worker.py::test_worker_settings_loads - AttributeError: 'Cr...
============ 10 failed, 35 passed, 4 warnings in 88.21s (0:01:28) =============
