from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_starts_without_credentials():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "main.py")).run(timeout=60)
    assert not app.exception
    assert any("Welcome" in title.value for title in app.title)


def test_authenticated_recommendation_for_first_row():
    from unittest.mock import MagicMock

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "main.py"))
    for key, value in dict(authenticated=True, sp=MagicMock(), user_id="dummy", display_name="Dummy").items():
        app.session_state[key] = value
    app.run(timeout=60)
    assert not app.exception
    next(button for button in app.button if "Find Similar" in button.label).click().run(timeout=60)
    assert not app.exception
    recs = app.session_state["recommendations"]
    assert len(recs) == 10
    assert 0 not in recs.row_id.values
