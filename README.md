# Better PyPI stats

Anyone can use https://pypistats.org/ to see the downloads for a given PyPI
package. However, the statistics and visualizations provided by the website are
limited. The purpose of this project is to provide a better alternative with
Ibis, ClickHouse, and ML-powered predictive analytics.

Then entire `pypi` dataset is approaching a trillion rows of data. Fortunately,
with the aggregated data provided by ClickHouse on a public playground instance
and Ibis for transformation, we can easily process this data in an embedded
dashboard application.

**WARNING**: work in progress

## Connecting to  data

```
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

## Work needed

We need to finalize on a dashboarding framework (Quarto dashboard has some
issues with interactive inputs and plotly), replicate the existing PyPI stats
visualizations, add new visualizations, and more.

A user should be able to input their package name and see all relevant stats,
then be able to drill into specific metrics and visualizations for a given
package.

### ML predictions

Using IbisML and time-series forecasting frameworks, we can predict the
downloads over time and show visualizations for these predictions.

