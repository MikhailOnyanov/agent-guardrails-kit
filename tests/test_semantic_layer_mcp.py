import subprocess
from pathlib import Path

import pytest

from semantic_layer_mcp import server


def test_list_metrics_runs_fixed_command(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str]) -> subprocess.CompletedProcess[str]:
        assert command == ["mf", "list", "metrics"]
        return subprocess.CompletedProcess(command, 0, stdout="revenue\n", stderr="")

    monkeypatch.setattr(server, "_run_metricflow", fake_run)
    assert server.list_metrics_impl() == "revenue\n"


def test_query_builds_bounded_metricflow_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    def fake_run(command: list[str]) -> subprocess.CompletedProcess[str]:
        captured.extend(command)
        output = Path(command[command.index("--csv") + 1])
        output.write_text("region,revenue\nМосква,42\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(server, "_run_metricflow", fake_run)
    result = server.query_metrics_impl(
        ["revenue"],
        ["order_id__region"],
        "2026-07-01",
        "2026-09-30",
    )

    assert result == "region,revenue\nМосква,42\n"
    assert captured[:4] == ["mf", "query", "--metrics", "revenue"]
    assert captured[captured.index("--limit") + 1] == "1000"


@pytest.mark.parametrize(
    ("metrics", "group_by", "start", "end"),
    [
        (["gross_margin"], [], "2026-01-01", "2026-01-02"),
        (["revenue"], ["customer__email"], "2026-01-01", "2026-01-02"),
        (["revenue"], [], "2026-01-02", "2026-01-01"),
        (["revenue"], [], "2025-01-01", "2026-02-01"),
    ],
)
def test_query_rejects_arguments_outside_policy(
    metrics: list[str], group_by: list[str], start: str, end: str
) -> None:
    with pytest.raises(ValueError):
        server.query_metrics_impl(metrics, group_by, start, end)
