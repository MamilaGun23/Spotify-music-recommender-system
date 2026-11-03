from urllib.parse import unquote
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from Recommender.data import load_songs_from_csv
from Recommender.features import FEATURE_COLS
from Recommender.recommend import get_song_mapping, recommend_from_song
from Recommender.playlist_utils import PlaylistError, create_playlist_from_selected_songs


@pytest.fixture
def tracks():
    df = pd.DataFrame({col: [1., 1., 1., 1.] for col in FEATURE_COLS})
    df["song"] = ["Same", "Same", "Déjà / &?", "A - B"]
    df["artist"] = ["First", "Second", "Björk #1", "First"]
    df["row_id"] = [0, 1, 2, 3]
    return df


def test_exact_self_exclusion_with_identical_features_and_nonrange_index(tracks):
    tracks.index = [10, 20, 30, 40]
    assert recommend_from_song(1, tracks, n=99).row_id.tolist() == [0, 2, 3]
    assert recommend_from_song(1, tracks, n=99).equals(recommend_from_song(1, tracks, n=99))


def test_duplicate_titles_and_artists_preserved(tmp_path, tracks):
    path = tmp_path / "songs.csv"
    tracks.to_csv(path, index=False)
    loaded = load_songs_from_csv(path)
    assert len(loaded) == 4
    assert list(get_song_mapping(loaded).values()) == [0, 1, 2, 3]
    assert recommend_from_song(0, loaded).row_id.tolist() == [1, 2, 3]
    assert list(tmp_path.iterdir()) == [path]


def test_empty_short_and_zero_requests(tracks):
    assert recommend_from_song(0, tracks.iloc[:0]).empty
    assert recommend_from_song(0, tracks.iloc[:1]).empty
    assert recommend_from_song(0, tracks, n=0).empty
    with pytest.raises(ValueError):
        recommend_from_song(0, tracks, n=-1)
    with pytest.raises(ValueError):
        recommend_from_song(999, tracks)


@pytest.mark.parametrize("bad", [None, np.inf, "bad"])
def test_bad_feature_values_rejected(tracks, bad):
    tracks["tempo"] = tracks["tempo"].astype(object)
    tracks.loc[1, "tempo"] = bad
    with pytest.raises(ValueError, match="finite"):
        recommend_from_song(0, tracks)


def test_schema_rejects_missing_features_and_ignores_identifiers(tracks):
    with pytest.raises(ValueError, match="Missing audio"):
        recommend_from_song(0, tracks.drop(columns="energy"))
    before = recommend_from_song(0, tracks)
    tracks["numeric_identifier"] = [123, 99999, -1000, 4]
    assert before.row_id.tolist() == recommend_from_song(0, tracks).row_id.tolist()


@pytest.mark.parametrize("content", ["", "song,artist\n", "wrong,columns\nx,y\n", "song,artist\na,b\n"])
def test_empty_malformed_csv(tmp_path, content):
    path = tmp_path / "bad.csv"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_songs_from_csv(path)


def test_portable_configured_path(tmp_path, tracks, monkeypatch):
    path = tmp_path / "songs.csv"
    tracks.to_csv(path, index=False)
    monkeypatch.setenv("SONGS_CSV_PATH", str(path))
    assert len(load_songs_from_csv()) == 4


def test_encoded_search_links(tracks):
    link = recommend_from_song(0, tracks).iloc[1].spotify_link
    assert unquote(link.rsplit("/", 1)[1]) == "Björk #1 Déjà / &?"
    assert "#" not in link and "?" not in link


def test_playlist_offline_search_and_batching(tracks):
    sp = MagicMock()
    sp.search.return_value = {"tracks": {"items": [{"uri": "spotify:track:dummy"}]}}
    sp.current_user_playlist_create.return_value = {"id": "p", "external_urls": {"spotify": "https://example.test/p"}}
    result = create_playlist_from_selected_songs(sp, "user", "Mix", "CSV mix", tracks)
    assert result == "https://example.test/p"
    assert sp.search.call_args_list[1].kwargs["q"] == "track:Same artist:Second"
    assert sp.current_user_playlist_create.call_args.kwargs["public"] is False
    sp.user_playlist_create.assert_not_called()
    assert len(sp._post.call_args.kwargs["payload"]["uris"]) == 4


def test_failed_search_does_not_create_orphan_playlist(tracks):
    sp = MagicMock()
    sp.search.return_value = {"tracks": {"items": []}}
    with pytest.raises(PlaylistError):
        create_playlist_from_selected_songs(sp, "user", "Mix", "", tracks)
    sp.current_user_playlist_create.assert_not_called()
