"""Result-number bounds for `duden -r/--result` (offline, network stubbed)."""

import pytest

import duden.cli as cli


@pytest.fixture
def two_matches(monkeypatch):
    """Pretend the search found two words; fail if anything is fetched."""
    monkeypatch.setattr(cli, "search", lambda *args, **kwargs: ["url-first", "url-second"])

    def _boom(url_suffix, cache=True):
        raise AssertionError(f"must not fetch anything, got {url_suffix!r}")

    monkeypatch.setattr(cli, "get", _boom)


def test_result_zero_is_rejected(monkeypatch, capsys, two_matches):
    """`-r 0` must exit 1 instead of silently showing the last match."""
    monkeypatch.setattr("sys.argv", ["duden", "Haus", "-r", "0"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    assert "1 or higher" in capsys.readouterr().out


def test_negative_result_is_rejected(monkeypatch, capsys, two_matches):
    """`-r -3` must exit 1 instead of silently showing a match."""
    monkeypatch.setattr("sys.argv", ["duden", "Haus", "-r", "-3"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    assert "1 or higher" in capsys.readouterr().out
