# imports
import ibis
import streamlit as st
import plotly.express as px

from datetime import datetime, timedelta

# configuration
st.set_page_config(layout="wide")
px.defaults.template = "plotly_dark"
ibis.options.interactive = True

host = "clickpy-clickhouse.clickhouse.com"
port = 443
user = "play"
database = "pypi"

# connection
con = ibis.clickhouse.connect(
    host=host,
    port=port,
    user=user,
    database=database,
)

# user input
with st.form(key="dashboard"):
    project_name = st.text_input(
        "project name",
        value="pyarrow",
    )
    days = st.number_input(
        "X days",
        min_value=1,
        max_value=3650,
        value=90,
        step=30,
        format="%d",
    )
    timescale = st.selectbox(
        "timescale",
        ["D", "W", "M", "Q", "Y"],
        index=0,
    )
    update_button = st.form_submit_button(label="update")

# table(s)
pypi = con.table("pypi_downloads_per_day_by_version_by_python_by_country")
t = pypi.filter(
    (pypi["project"] == project_name)
    & (pypi["date"] > datetime.now() - timedelta(days=days))
).order_by(pypi["date"].desc())

# viz
c0 = px.line(
    t.group_by(t["date"].truncate(timescale).name("date"))
    .agg(t["count"].sum().name("downloads"))
    .order_by(ibis._["date"].desc())
    .mutate(
        ibis._["downloads"]
        .sum()
        .over(rows=(0, None), order_by=ibis._["date"].desc())
        .name("total_downloads")
    )
    .order_by(ibis._["date"].desc())
    .to_pandas(),
    x="date",
    y="downloads",
    title=f"downloads of {project_name} in the last {days} days",
    markers=True,
)
c0.update_yaxes(range=[0, c0.data[0].y.max() * 1.1])
st.plotly_chart(c0, use_container_width=True)

# cumulative downloads
c1 = px.line(
    t.group_by(t["date"].truncate(timescale).name("date"))
    .agg(t["count"].sum().name("downloads"))
    .order_by(ibis._["date"].desc())
    .mutate(
        ibis._["downloads"]
        .sum()
        .over(rows=(0, None), order_by=ibis._["date"].desc())
        .name("total_downloads")
    )
    .order_by(ibis._["date"].desc())
    .to_pandas(),
    x="date",
    y="total_downloads",
    title=f"cumulative downloads of {project_name} in the last {days} days",
)
st.plotly_chart(c1, use_container_width=True)

# daily downloads, stacked bar chart
c2 = px.bar(
    t.group_by(t["date"].truncate(timescale).name("date"), t["version"])
    .agg(t["count"].sum().name("downloads"))
    .order_by(ibis._["date"].desc())
    .mutate(
        ibis._["downloads"]
        .sum()
        .over(rows=(0, None), order_by=ibis._["date"].desc())
        .name("total_downloads")
    )
    .order_by(ibis._["date"].desc(), ibis._["downloads"].desc())
    .to_pandas(),
    x="date",
    y="downloads",
    title=f"daily downloads of {project_name} in the last {days} days",
    color="version",
)
st.plotly_chart(c2, use_container_width=True)

# daily downloads by country
c3 = px.bar(
    t.group_by(t["date"].truncate(timescale).name("date"), t["country_code"])
    .agg(t["count"].sum().name("downloads"))
    .order_by(ibis._["date"].desc())
    .mutate(
        ibis._["downloads"]
        .sum()
        .over(rows=(0, None), order_by=ibis._["date"].desc())
        .name("total_downloads")
    )
    .order_by(ibis._["date"].desc(), ibis._["downloads"].desc())
    .to_pandas(),
    x="date",
    y="downloads",
    title=f"daily downloads of {project_name} in the last {days} days by country",
    color="country_code",
)
st.plotly_chart(c3, use_container_width=True)

# downloads by python minor
c4 = px.bar(
    t.group_by(t["date"].truncate(timescale).name("date"), t["python_minor"])
    .agg(t["count"].sum().name("downloads"))
    .order_by(ibis._["date"].desc())
    .mutate(
        ibis._["downloads"]
        .sum()
        .over(rows=(0, None), order_by=ibis._["date"].desc())
        .name("total_downloads")
    )
    .order_by(ibis._["date"].desc(), ibis._["downloads"].desc())
    .to_pandas(),
    x="date",
    y="downloads",
    title=f"daily downloads of {project_name} in the last {days} days by python minor",
    color="python_minor",
)
st.plotly_chart(c4, use_container_width=True)
