from pathlib import Path

from alertmanager_report_manager.cli import main


def test_init_db_command_creates_database(tmp_path: Path, capsys) -> None:
    database_path = tmp_path / "alerts.db"

    exit_code = main(["init-db", str(database_path)])

    assert exit_code == 0
    assert database_path.exists()
    assert str(database_path) in capsys.readouterr().out
