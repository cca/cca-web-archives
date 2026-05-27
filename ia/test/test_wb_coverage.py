import csv
from pathlib import Path

from click.testing import CliRunner

from ia import wb_coverage


def test_compact_coverage_csv_keeps_latest_per_surt(tmp_path: Path) -> None:
    input_csv = tmp_path / "coverage.csv"
    output_csv = tmp_path / "coverage-compact.csv"

    with open(input_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "sorting key",
                "url",
                "timestamp",
                "status code",
                "mime type",
                "archived url",
                "wayback url",
            ]
        )
        writer.writerow(
            [
                "edu,cca)/",
                "https://cca.edu",
                "2026-01-01 00:00:00+00:00",
                "200",
                "text/html",
                "a",
                "va",
            ]
        )
        writer.writerow(
            [
                "edu,cca)/",
                "https://cca.edu",
                "2026-01-02 00:00:00+00:00",
                "200",
                "text/html",
                "b",
                "vb",
            ]
        )
        writer.writerow(
            [
                "edu,cca,library)/",
                "https://library.cca.edu",
                "2026-01-01 12:00:00+00:00",
                "200",
                "text/html",
                "c",
                "vc",
            ]
        )

    row_count, surt_count = wb_coverage.compact_coverage_csv(input_csv, output_csv)

    assert row_count == 3
    assert surt_count == 2

    with open(output_csv, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert rows[0]["sorting key"] == "edu,cca)/"
    assert rows[0]["timestamp"] == "2026-01-02 00:00:00+00:00"
    assert rows[1]["sorting key"] == "edu,cca,library)/"


def test_default_command_routes_to_search(tmp_path: Path, monkeypatch) -> None:
    output_csv = tmp_path / "out.csv"

    class FakeClient:
        def search(self, **_kwargs):
            return iter(())

    monkeypatch.setattr(wb_coverage, "WaybackClient", lambda: FakeClient())

    runner = CliRunner()
    result = runner.invoke(
        wb_coverage.cli,
        ["--output", str(output_csv), "example.com"],
    )

    assert result.exit_code == 0
    assert output_csv.exists()

    with open(output_csv, "r", encoding="utf-8") as f:
        header = f.readline().strip()

    assert (
        header
        == "sorting key,original,timestamp,status code,mime type,archived url,wayback url"
    )
