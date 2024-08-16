# imports
import re
import os
import sys
import ibis

import plotly.io as pio
import ibis.selectors as s
import plotly.express as px

from rich import print
from datetime import datetime, timedelta, date

## ibis config
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 20
ibis.options.repr.interactive.max_columns = None

# variables
NOW = datetime.now()
NOW_7 = NOW - timedelta(days=7)
NOW_30 = NOW - timedelta(days=30)
NOW_90 = NOW - timedelta(days=90)
NOW_180 = NOW - timedelta(days=180)
NOW_365 = NOW - timedelta(days=365)
NOW_10 = NOW - timedelta(days=3650)

# connect to database
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
