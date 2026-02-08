from __future__ import annotations

import json

import click

from quantfi.backtest.engine import run_backtest
from quantfi.core.config import Settings
from quantfi.ops.pipeline import run_daily
from quantfi.warehouse.db import DB


@click.group()
def cli() -> None:
    """quantfi CLI"""


@cli.command("init_db")
@click.option("--config", "config_path", default=None)
def init_db_cmd(config_path: str | None) -> None:
    settings = Settings.from_file(config_path)
    DB(settings.database_url).init_db()
    click.echo("db initialized")


@cli.command("run_daily")
@click.option("--trade-date", required=True)
@click.option("--config", "config_path", default=None)
def run_daily_cmd(trade_date: str, config_path: str | None) -> None:
    settings = Settings.from_file(config_path)
    result = run_daily(trade_date, settings)
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


@cli.command("backtest")
@click.option("--decision-json", required=True, help="Path to decision records grouped by date")
@click.option("--returns-json", required=True, help="Path to realized next-day returns grouped by date")
def backtest_cmd(decision_json: str, returns_json: str) -> None:
    with open(decision_json, "r", encoding="utf-8") as f:
        decisions = json.load(f)
    with open(returns_json, "r", encoding="utf-8") as f:
        returns = json.load(f)
    res = run_backtest(decisions, returns)
    click.echo(json.dumps(res.__dict__, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
