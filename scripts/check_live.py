"""One live user check using the production auth/recommendation/playlist code.

With --playlist, creates one diagnostic playlist for review. No secrets, tokens or user IDs print.
"""
import argparse
import logging
from datetime import datetime, timedelta, timezone

from Recommender.auth import AuthenticationError, get_spotify_client
from Recommender.data import load_songs_from_csv
from Recommender.playlist_utils import create_playlist_from_selected_songs, search_spotify_uri
from Recommender.recommend import recommend_from_song
from spotipy.exceptions import SpotifyException


class ObservedClient:
    def __init__(self, client):
        self.client = client
        self.created = None
        self.added = 0

    def __getattr__(self, name):
        return getattr(self.client, name)

    def current_user_playlist_create(self, **kwargs):
        self.created = self.client.current_user_playlist_create(**kwargs)
        return self.created

    def _post(self, path, **kwargs):
        result = self.client._post(path, **kwargs)
        if not result or not result.get('snapshot_id'):
            raise RuntimeError('No playlist snapshot acknowledgement.')
        self.added += len(kwargs['payload']['uris'])
        return result


def main():
    logging.disable(logging.CRITICAL)
    parser = argparse.ArgumentParser(description='Live OAuth, refresh and search checks; optionally create one diagnostic playlist.')
    parser.add_argument('--playlist', action='store_true', help='Create and retain one diagnostic playlist with two tracks.')
    options = parser.parse_args()
    
    stage = 'OAuth login'
    observed = None
    try:
        print('Starting live user OAuth; complete the Spotify consent page in your browser.', flush=True)
        client = get_spotify_client()
        profile = client.current_user()
        assert profile and profile.get('id')
        print('PASS: user OAuth and current-user profile.', flush=True)
    
        stage = 'Token refresh'
        manager = client.auth_manager
        cached = manager.cache_handler.get_cached_token()
        assert cached and cached.get('refresh_token')
        refreshed = manager.refresh_access_token(cached['refresh_token'])
        assert refreshed and refreshed.get('access_token')
        assert client.current_user()['id'] == profile['id']
        print('PASS: token refresh preserves the authenticated account.', flush=True)
    
        stage = 'Catalogue recommendations and live search'
        catalogue = load_songs_from_csv()
        recommendations = recommend_from_song(0, catalogue, n=1)
        assert not recommendations.empty and 0 not in recommendations.row_id.values
        selected = catalogue[catalogue.row_id.isin([0, int(recommendations.iloc[0].row_id)])]
        expected = [search_spotify_uri(client, row.song, row.artist) for row in selected.itertuples()]
        assert len(expected) == 2 and all(expected)
        print('PASS: CSV recommendation, exact self-exclusion and live search for two tracks.', flush=True)
    
        if not options.playlist:
            print('Read-only checks completed. Use --playlist to exercise playlist creation and read-back.', flush=True)
            raise SystemExit(0)
    
        stage = 'Diagnostic playlist creation and additions'
        observed = ObservedClient(client)
        name = 'Music Recommender Live Check ' + datetime.now(timezone(timedelta(hours=2))).strftime('%Y-%m-%d %H:%M SAST')
        create_playlist_from_selected_songs(
            observed, profile['id'], name,
            'Diagnostic playlist created to verify this application. Safe to remove after review.', selected,
        )
        assert observed.created and observed.created.get('public') is False
        assert observed.created.get('owner', {}).get('id') == profile['id']
        assert observed.added == 2
        print('PASS: current-user playlist created with public=false; two additions acknowledged by snapshot ID.', flush=True)
        print('Diagnostic playlist retained for inspection: ' + name, flush=True)
    
        stage = 'Playlist read-back'
        try:
            page = client.playlist_items(observed.created['id'], limit=10)
            actual = [(entry.get('item') or entry.get('track') or {}).get('uri') for entry in page['items']]
            assert actual == expected
            print('PASS: persisted playlist items match the two requested tracks.', flush=True)
        except SpotifyException as error:
            if error.http_status == 403:
                print('LIMITED: playlist read-back returned HTTP 403; app scope omits playlist-read-private.', flush=True)
            else:
                raise
        print('Completed live user checks; no credentials or tokens were written to logs.', flush=True)
    except AuthenticationError:
        print('FAIL: OAuth login; check the registered redirect, app access and browser consent.', flush=True)
        raise SystemExit(1) from None
    except Exception as error:
        status = getattr(error, 'http_status', None)
        print(f'FAIL: {stage}' + (f' (HTTP {status})' if status else '') + '; provider details suppressed.', flush=True)
        if observed and observed.created:
            print('A diagnostic playlist was created; inspect your account before retrying.', flush=True)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
