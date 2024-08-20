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
