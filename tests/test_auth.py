from unittest.mock import MagicMock

import pytest

from Recommender import auth


def configure(monkeypatch):
    monkeypatch.setattr(auth, "load_dotenv", lambda *a, **kw: None)
    for key, value in {
        "SPOTIPY_CLIENT_ID": "dummy", "SPOTIPY_CLIENT_SECRET": "dummy",
        "SPOTIPY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
    }.items():
        monkeypatch.setenv(key, value)


def test_missing_config_is_recoverable(monkeypatch):
    configure(monkeypatch)
    monkeypatch.delenv("SPOTIPY_CLIENT_SECRET")
    with pytest.raises(auth.AuthenticationError, match="SPOTIPY_CLIENT_SECRET"):
        auth.get_spotify_client()


def test_login_caches_and_states_are_isolated(monkeypatch, capsys):
    configure(monkeypatch)
    oauth = MagicMock()
    monkeypatch.setattr(auth, "SpotifyOAuth", oauth)
    monkeypatch.setattr(auth.spotipy, "Spotify", MagicMock())
    auth.get_spotify_client()
    auth.get_spotify_client()
    first, second = [call.kwargs for call in oauth.call_args_list]
    assert first["scope"] == "playlist-modify-private"
    assert first["cache_handler"] is not second["cache_handler"]
    assert first["state"] != second["state"]
    first["cache_handler"].save_token_to_cache({"access_token": "private"})
    assert second["cache_handler"].get_cached_token() is None
    assert not capsys.readouterr().out


def test_failure_does_not_leak_provider_error(monkeypatch):
    configure(monkeypatch)
    monkeypatch.setattr(auth, "SpotifyOAuth", MagicMock(side_effect=RuntimeError("sensitive token")))
    with pytest.raises(auth.AuthenticationError) as error:
        auth.get_spotify_client()
    assert "sensitive" not in str(error.value)


def test_logout_clears_user_state(monkeypatch):
    from Recommender import login
    state = dict(sp=object(), user_id="user", display_name="User", authenticated=True,
                 recommendations=object(), recommendations_history=["history"], selected_song="song")
    monkeypatch.setattr(login.st, "session_state", state)
    login.logout()
    assert state == {}
