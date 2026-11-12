import subprocess
import tempfile
from datetime import date
from pathlib import Path

from fastmcp import FastMCP


mcp = FastMCP("metricflow")

ALLOWED_METRICS = {"revenue", "orders"}
ALLOWED_GROUP_BY = {
    "metric_time__month",
    "metric_time__quarter",
    "order_id__region",
}
MAX_ROWS = 1_000
MAX_DAYS = 366
TIMEOUT_SECONDS = 60


def _run_metricflow(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run MetricFlow without a shell and with a hard timeout."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=True,
    )


def list_metrics_impl() -> str:
    return _run_metricflow(["mf", "list", "metrics"]).stdout


def query_metrics_impl(
    metrics: list[str],
    group_by: list[str],
    start_time: str,
    end_time: str,
) -> str:
    unknown_metrics = set(metrics) - ALLOWED_METRICS
    if not metrics or unknown_metrics:
        raise ValueError(f"Недопустимые метрики: {unknown_metrics}")

    unknown_dimensions = set(group_by) - ALLOWED_GROUP_BY
    if unknown_dimensions:
        raise ValueError(f"Недопустимые разрезы: {unknown_dimensions}")

    start = date.fromisoformat(start_time)
    end = date.fromisoformat(end_time)
    if not 0 <= (end - start).days <= MAX_DAYS:
        raise ValueError(f"Период должен быть от 0 до {MAX_DAYS} дней")

    with tempfile.TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory) / "result.csv"
        command = [
            "mf",
            "query",
            "--metrics",
            ",".join(metrics),
            "--start-time",
            start.isoformat(),
            "--end-time",
            end.isoformat(),
            "--limit",
            str(MAX_ROWS),
            "--csv",
            str(output),
        ]
        if group_by:
            command[4:4] = ["--group-by", ",".join(group_by)]
        _run_metricflow(command)
        return output.read_text(encoding="utf-8")


@mcp.tool
def list_metrics() -> str:
    """List metrics exposed by the configured MetricFlow project."""
    return list_metrics_impl()


@mcp.tool
def query_metrics(
    metrics: list[str],
    group_by: list[str],
    start_time: str,
    end_time: str,
) -> str:
    """Query only approved metrics and dimensions for a bounded date range."""
    return query_metrics_impl(metrics, group_by, start_time, end_time)


if __name__ == "__main__":
    mcp.run()
