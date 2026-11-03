"""Exercise the real pinned Spotipy client, intercepting only HTTP transport."""
import json

import pandas as pd
import pytest
import requests
import spotipy

from Recommender.playlist_utils import create_playlist_from_selected_songs


@pytest.mark.parametrize("count", [1, 101, 201])
def test_current_endpoints_json_body_and_batch_boundaries(monkeypatch, count):
    client = spotipy.Spotify(auth="offline-dummy-token", retries=0)
    calls = []
    playlist_id = "p" * 22
    track_uri = "spotify:track:" + "t" * 22

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        response = requests.Response()
        if method == "GET" and url.endswith("/search"):
            assert kwargs["params"]["limit"] == 1
            body = {"tracks": {"items": [{"uri": track_uri}]}}
            response.status_code = 200
        elif method == "POST" and url.endswith("/me/playlists"):
            assert json.loads(kwargs["data"])["public"] is False
            body = {"id": playlist_id, "external_urls": {"spotify": "https://example.test/playlist"}}
            response.status_code = 201
        elif method == "POST" and url.endswith(f"/playlists/{playlist_id}/items"):
            body = {"snapshot_id": "offline-snapshot"}
            response.status_code = 201
        else:
            pytest.fail(f"Unexpected Spotify endpoint: {method} {url}")
        response._content = json.dumps(body).encode()
        return response

    monkeypatch.setattr(client._session, "request", request)
    tracks = pd.DataFrame({"song": ["Déjà / &?"] * count, "artist": ["Björk"] * count})
    assert create_playlist_from_selected_songs(client, "unused-legacy-user-id", "Transport check", "", tracks)
    additions = [json.loads(kwargs["data"]) for method, url, kwargs in calls if url.endswith("/items")]
    assert [len(body["uris"]) for body in additions] == [
        min(100, count - offset) for offset in range(0, count, 100)
    ]
    assert [uri for body in additions for uri in body["uris"]] == [track_uri] * count
    assert not any("/users/" in url or url.endswith("/tracks") for _, url, _ in calls)
