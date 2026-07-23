# v2.0.x Web CORS origin configuration

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED
Small commit: M-6

## Purpose

M-6 makes the FastAPI Web CORS origin list configurable without changing the released local-demo behavior. The default remains an all-origin wildcard because the smartphone Web demo is commonly served from changing local ports or LAN development hosts.

## Configuration contract

```text
WEB_CORS_ORIGINS=*
```

To restrict browser origins, provide a comma- or space-separated list:

```text
WEB_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:8080
```

Loading rules:

```text
- Missing or blank values use the local-demo default `*`.
- Separator-only values also use `*`.
- Explicit entries are stripped and stored as an ordered tuple.
- The configured tuple is passed to FastAPI CORSMiddleware.
- allow_credentials remains False.
- allow_methods and allow_headers remain ["*"].
```

`WEB_CORS_ORIGINS=*` is a local/demo compatibility default, not a production-hosting recommendation. A deployed operator must choose explicit origins as part of a separately accepted hosting and security model.

## Mock-safe regression boundary

The focused tests use a temporary FastAPI application and Starlette/FastAPI TestClient. They do not import the full production `app.main`, avoiding module-level DailyRecord persistence initialization. Source-tree checks separately verify that `backend/app/main.py` binds `config.web_cors_origins` to CORSMiddleware.

Coverage includes:

```text
- default wildcard configuration
- explicit origin-list parsing
- separator-only fallback
- wildcard preflight acceptance
- configured-origin preflight acceptance
- unlisted-origin preflight rejection
```

The tests require no credentials, external network, provider checkout, browser, local health token, or backend/local_data access.

## Non-goals

M-6 does not add:

```text
- user authentication or authorization
- production hosting readiness
- reverse-proxy or trusted-host policy
- TLS/certificate configuration
- CORS credential support
- origin regex configuration
- Flutter behavior changes
- real provider or health API execution
- a release ZIP, tag, GitHub Release, or v2.0.1 publication
```

## Verification

From the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py
python scripts\check_v20x_backend_mock_safe_regression.py
python scripts\check_v20x_framework_fallback_voice_artifact_regression.py
python scripts\check_v20x_temporary_lifecycle_limits.py
python scripts\check_v20x_web_cors_origins.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

M-6 was accepted on 2026-07-23 after compileall, M-1 through M-6 checks, 31 backend pytest tests, 39 Flutter tests, diff review, and operator approval passed. The published v2.0.0 history remains immutable, and v2.0.1 was not released by M-6.
