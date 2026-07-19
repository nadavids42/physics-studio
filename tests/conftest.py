"""Session-wide test hooks."""

from __future__ import annotations

_BROWSER_SKIP_REASON = (
    "SKIPPED: browser tests require CHROMIUM_BIN; this run has NO browser coverage."
)


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    skipped = terminalreporter.stats.get("skipped", [])
    if any(_BROWSER_SKIP_REASON in str(report.longrepr) for report in skipped):
        terminalreporter.write_line(
            "WARNING: browser tests were skipped — this run has NO browser coverage. "
            "Set CHROMIUM_BIN and rerun to exercise them.",
            red=True,
            bold=True,
        )
