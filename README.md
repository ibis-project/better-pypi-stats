# Better PyPI stats

You can use https://pypistats.org to see the downloads for a given PyPI package. However, the statistics and visualizations provided by the website are limited. The purpose of this project is to provide a better dynamic alternative with [Ibis](https://github.com/ibis-project/ibis), [ClickHouse](https://github.com/clickhouse/clickhouse), and [Shiny for Python](https://github.com/posit-dev/py-shiny).

## Dashboard

https://connect.posit.cloud/lostmygithubaccount/content/019180af-9e47-14bd-0955-38e6d98a5f98

## Connecting to  data

```python
import ibis

ibis.options.interactive = True

host = "clickpy-clickhouse.clickhouse.com"
port = 443
user = "play"
database = "pypi"

con = ibis.clickhouse.connect(
  host=host,
  port=port,
  user=user,
  database=database,
)

con.list_tables()
```

## Development

Install [`gh`](https://github.com/cli/cli) and [`just`](https://github.com/casey/just) and [`uv`](https://github.com/astral-sh/uv), then:

```bash
gh repo clone ibis-project/better-pypi-stats
cd better-pypi-stats
just setup
. .venv/bin/activate
just app
```

## Contributing

Contributions welcome. Please format your code:

```bash
just fmt
```
