# Live Spotify verification — 3 November 2026

Live checks completed on the local machine at approximately 03:34 SAST using
the configured application and a user-approved Spotify OAuth session. Credentials,
tokens and user IDs are excluded from this report. The local .env is git-ignored.

| Check | Observed result |
|---|---|
| Application client-credentials token exchange | HTTP 200, token issued |
| Application-token track search | HTTP 200, one result returned |
| User OAuth and current-user profile | Passed after browser consent |
| Explicit refresh-token exchange | Passed; subsequent profile matched the same account |
| CSV load and recommendation for row zero | Passed; selected row excluded |
| Live search for source and recommended tracks | Both resolved |
| Current-user playlist creation | Passed; API returned public=false and the authenticated owner |
| Adding the two tracks | Passed; API returned a snapshot acknowledgement |
| Persisted playlist read-back | Passed; both returned URIs matched the requested tracks in order |
| Offline regression suite with local configuration present | 24 passed in 11.35s |
| Streamlit launch on port 8502 | Started; health endpoint returned HTTP 200, ok; stopped after checking |

The diagnostic playlist was retained for inspection, with the exact name
`Music Recommender Live Check 2026-11-03 01:34 UTC` (03:34 SAST). No existing
playlists were edited. The tokens stayed in the diagnostic process's memory.

## Reproduce

Configure a private .env from .env.example and register its exact redirect URI
in Spotify's application settings. Keep the callback port separate from the UI.
The checked callback was http://127.0.0.1:8501/; use port 8502 for Streamlit:

```sh
python -m streamlit run main.py --server.address 127.0.0.1 --server.port 8502
python -m scripts.check_live
python -m scripts.check_live --playlist
```

Run the last two commands individually from a terminal and complete browser
consent. The default diagnostic is read-only. The --playlist variant creates one
clearly named diagnostic playlist and retains it so it can be inspected/removed
in Spotify. Do not launch concurrent logins on the same callback port.

The observed run used a one-off harness importing the production auth, CSV,
recommendation and playlist functions; the reusable scripts/check_live.py follows
that same sequence with an explicit flag for writes. Its help/compilation checks
were run without creating a second playlist.

## Scope of this evidence

This verifies the actual API flow for one configured application, account,
catalogue selection and session. It does not establish access for other accounts,
unattended/hosted OAuth, rate-limit behaviour, or perfect search matching. Private
read-back can require playlist-read-private; it succeeded for this account, and
the diagnostic reports HTTP 403 as limited rather than expanding app permissions
silently. No live audio-feature ingestion or deployment was tested.

The earlier credential-blocked result in REMEDIATION.md is historical; user
configuration and browser approval resolved it. A shared client secret should
be rotated in Spotify's dashboard and replaced in the private local .env.
