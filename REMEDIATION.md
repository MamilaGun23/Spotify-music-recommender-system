# Remediation evidence — 3 November 2026

## Verified changes

- README now describes the actual Streamlit entry point, CSV source, data flow,
  schema, local-only OAuth limitations and unverified dataset provenance.
- Runtime/dev requirements are pinned for Python 3.12; python-dotenv and dummy
  .env.example configuration use consistent SPOTIPY names.
- data.py resolves paths from the repository or SONGS_CSV_PATH, validates finite
  features and labels, preserves every CSV row and assigns stable row IDs.
- recommend.py and main.py preserve row identity through selection and playlist
  creation, remove the exact source row, break ties by CSV order and encode links.
- auth.py/login.py replace import-time failure, broad scopes, process exits and
  shared disk cache with recoverable errors and isolated in-memory login caches.
- playlist_utils.py resolves tracks before creating private playlists, batches
  additions, and reports API failure without exposing provider exception text.
- __init__.py repairs the package marker. Unsafe import-time live scripts were
  replaced by the explicitly invoked scripts/check_login.py.
- Analytics now reports catalogue statistics instead of an unsupported diversity
  quality score; recommendation history counts and short-dataset guards are fixed.
- Offline tests cover recommender, schema, OAuth/session, playlists and app flows.

## Actual validation

Environment: newly provisioned CPython 3.12.16; installed pinned runtime/dev
dependencies. Windows application policy blocked the venv launcher, so checks
used the separate interpreter directly. The documented venv activation path was
not fully exercised on this host.

Commands (python denotes that interpreter):

| Command | Observed result |
|---|---|
| python -m pytest -q | **21 passed in 10.59s**, no Spotify HTTP access |
| python -m ruff check . | Passed (one unused import removed during the initial check) |
| python -m compileall -q Recommender pages main.py scripts tests | Passed |
| git diff --check | Passed |
| Dependency installation dry run from requirements-dev.txt | All 11 direct packages already satisfied; no changes |
| python -m streamlit run main.py --server.headless=true --server.address=127.0.0.1 --server.port=18501 --browser.gatherUsageStats=false | Started successfully; /_stcore/health returned HTTP 200, 'ok'; server stopped afterwards |

The first cold-cache suite run had a 60-second Streamlit startup timeout and 20
passing tests. After the plotting-library cache warmed, the full suite passed.
AppTest verifies both the unauthenticated login page and an authenticated
mock-client recommendation for row zero. It is not a live OAuth check.

## Remaining limitations and safe claims

- Live Spotify OAuth, search matching and playlist changes remain **manually
  unverified** without personal credentials. No account mutations were performed.
- Loopback OAuth is for a local desktop, one concurrent login at a time. Hosted
  multiuser OAuth and deployment are not implemented.
- Dataset publisher/licence remain unknown. The CSV is unchanged (SHA-256
  959a5e499e6d0927da92d2c58204e0544f704a6d1e3d578f6ff94b477fcca6fc).
- Search selects Spotify's first result, which can differ from the CSV recording.
  Failed additions may leave a partial playlist. API access remains account dependent.
- Retrieval similarity is not a measured recommendation-quality benchmark.

Safe to describe: a tested CSV content-based Streamlit recommender with stable
track identity, explicit feature validation, offline regression tests and local
Spotify integration code. Do not claim live audio-feature ingestion, verified
live playlists, deployment, production readiness, recommendation accuracy or CI
success from these checks.
