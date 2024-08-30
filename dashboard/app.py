import ibis
import plotly.express as px

from shiny import reactive, render
from shinyswatch import theme
from shinywidgets import render_plotly
from shiny.express import input, ui

from datetime import datetime, timedelta

# connect to PyPI data in the ClickHouse Cloud playground
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

# get table and metadata
downloads_t = con.table(
    "pypi_downloads_per_day_by_version_by_installer_by_type_by_country"
)

# themes
px.defaults.template = "plotly_dark"
ui.page_opts(theme=theme.superhero)

# page options
ui.page_opts(
    title="Better PyPI stats",
    fillable=False,
    full_width=True,
)

# add page title and sidebar
with ui.sidebar(open="desktop"):
    ui.input_select(
        "version_style",
        "Version style",
        ["major", "major.minor", "major.minor.patch"],
        selected="major",
    )
    ui.input_date_range(
        "date_range",
        "Date range",
        start=(datetime.now() - timedelta(days=28)),
        end=datetime.now() + timedelta(days=1),
    )
    ui.input_action_button("last_7d", "Last 7 days")
    ui.input_action_button("last_14d", "Last 14 days")
    ui.input_action_button("last_28d", "Last 28 days")
    ui.input_action_button("last_91d", "Last 91 days")
    ui.input_action_button("last_182d", "Last 182 days")
    ui.input_action_button("last_365d", "Last 365 days")
    ui.input_action_button("last_730d", "Last 730 days")
    ui.input_action_button("last_all", "All available data")

    with ui.value_box(full_screen=True):
        "Total days in range"

        @render.express
        def total_days():
            start_date, end_date = date_range()
            days = (end_date - start_date).days - 1
            f"{days:,}"


with ui.layout_columns():
    with ui.card():
        ui.input_text(
            "package", "Package", value="pyarrow", placeholder="Enter package"
        )
    with ui.card():

        @render.express
        def title():
            f"PyPI package: {input.package()} from {input.date_range()[0]} to {input.date_range()[1]}"


with ui.layout_columns():
    with ui.value_box(full_screen=True):
        "Total downloads"

        @render.express
        def total_downloads():
            val = downloads_data()["count"].sum().to_pyarrow().as_py()
            f"{val:,}"

    with ui.value_box(full_screen=True):
        "Total versions"

        @render.express
        def total_versions():
            val = (
                downloads_data()
                .distinct(on="version")["version"]
                .to_pyarrow()
                .to_pylist()
            )
            f"{len(val):,}"


with ui.layout_columns():
    with ui.card(full_screen=True):
        "Rolling 28d downloads"

        @render_plotly
        def downloads_roll():
            t = _downloads_data()
            min_date, max_date = date_range()

            t = t.mutate(
                timestamp=t["date"].cast("timestamp"),
            )
            t = t.group_by("timestamp").agg(downloads=ibis._["count"].sum())
            t = (
                t.select(
                    "timestamp",
                    rolling_downloads=ibis._["downloads"]
                    .sum()
                    .over(
                        ibis.window(
                            order_by="timestamp",
                            preceding=28,
                            following=0,
                        )
                    ),
                )
                .filter(t["timestamp"] >= min_date, t["timestamp"] <= max_date)
                .order_by("timestamp")
            )

            c = px.line(
                t,
                x="timestamp",
                y="rolling_downloads",
            )

            return c

    with ui.card(full_screen=True):
        "Rolling 28d downloads by version"

        @render_plotly
        def downloads_by_version_roll():
            t = _downloads_data()
            min_date, max_date = date_range()

            t = t.mutate(
                timestamp=t["date"].cast("timestamp"),
            )
            t = t.group_by("timestamp", "version").agg(downloads=ibis._["count"].sum())
            t = (
                t.select(
                    "timestamp",
                    "version",
                    rolling_downloads=ibis._["downloads"]
                    .sum()
                    .over(
                        ibis.window(
                            order_by="timestamp",
                            group_by="version",
                            preceding=28,
                            following=0,
                        )
                    ),
                )
                .filter(t["timestamp"] >= min_date, t["timestamp"] <= max_date)
                .order_by("timestamp")
            )

            c = px.line(
                t,
                x="timestamp",
                y="rolling_downloads",
                color="version",
                category_orders={
                    "version": reversed(
                        sorted(
                            t.distinct(on="version")["version"]
                            .to_pyarrow()
                            .to_pylist(),
                            key=lambda x: tuple(
                                int(y) for y in x.split(".") if y.isdigit()
                            ),
                        )
                    )
                },
            )

            return c


with ui.card(full_screen=True):
    "Downloads by..."

    with ui.card_header(class_="d-flex justify-content-between align-items-center"):
        with ui.layout_columns():
            ui.input_select(
                "group_by_downloads",
                "Group by:",
                [None, "version", "country_code", "installer", "type"],
                selected="version",
            )

    @render_plotly
    def downloads_flex():
        group_by = input.group_by_downloads()

        t = downloads_data()
        t = t.mutate(timestamp=t["date"].cast("timestamp"))
        t = t.group_by(["timestamp", group_by] if group_by else "timestamp").agg(
            downloads=ibis._["count"].sum()
        )
        t = t.order_by("timestamp", ibis.desc("downloads"))

        c = px.bar(
            t,
            x="timestamp",
            y="downloads",
            color=group_by if group_by else None,
            barmode="stack",
            category_orders={
                "version": reversed(
                    sorted(
                        t.distinct(on="version")["version"].to_pyarrow().to_pylist(),
                        key=lambda x: tuple(
                            int(y) for y in x.split(".") if y.isdigit()
                        ),
                    )
                )
            }
            if group_by == "version"
            else None,
        )

        return c


with ui.layout_columns():
    with ui.card(full_screen=True):
        "Downloads by day of week"

        @render_plotly
        def downloads_day_of_week():
            t = downloads_data()
            t = t.mutate(day_of_week=t["date"].day_of_week.full_name())
            t = t.group_by("day_of_week").agg(downloads=ibis._["count"].sum())
            c = px.bar(
                t,
                x="day_of_week",
                y="downloads",
                category_orders={
                    "day_of_week": [
                        "Sunday",
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                    ]
                },
            )

            return c

    with ui.card(full_screen=True):
        "Downloads by version table"

        @render.data_frame
        def downloads_by_version():
            t = downloads_data()

            t = (
                t.group_by("version")
                .agg(downloads=ibis._["count"].sum())
                .order_by(ibis.desc("downloads"))
            )

            return render.DataGrid(t.to_polars())


# reactive calculations and effects
@reactive.calc
def date_range():
    start_date, end_date = input.date_range()

    return start_date, end_date


@reactive.calc
def downloads_data(downloads_t=downloads_t):
    package = input.package()
    version_style = input.version_style()
    start_date, end_date = input.date_range()

    t = downloads_t.filter(downloads_t["project"] == package)
    t = t.filter(downloads_t["date"] >= start_date, downloads_t["date"] <= end_date)

    match version_style:
        case "major":
            t = t.mutate(version=t["version"].split(".")[0])
        case "major.minor":
            t = t.mutate(
                version=t["version"].split(".")[0] + "." + t["version"].split(".")[1]
            )
        case _:
            pass

    return t


@reactive.calc
def _downloads_data(downloads_t=downloads_t):
    package = input.package()
    version_style = input.version_style()

    t = downloads_t.filter(downloads_t["project"] == package)

    match version_style:
        case "major":
            t = t.mutate(version=t["version"].split(".")[0])
        case "major.minor":
            t = t.mutate(
                version=t["version"].split(".")[0] + "." + t["version"].split(".")[1]
            )
        case _:
            pass

    return t


def _update_date_range(days):
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now() + timedelta(days=1)
    ui.update_date_range(
        "date_range",
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
    )


@reactive.effect
@reactive.event(input.last_7d)
def _():
    _update_date_range(days=7)


@reactive.effect
@reactive.event(input.last_14d)
def _():
    _update_date_range(days=14)


@reactive.effect
@reactive.event(input.last_28d)
def _():
    _update_date_range(days=28)


@reactive.effect
@reactive.event(input.last_91d)
def _():
    _update_date_range(days=91)


@reactive.effect
@reactive.event(input.last_182d)
def _():
    _update_date_range(days=182)


@reactive.effect
@reactive.event(input.last_365d)
def _():
    _update_date_range(days=365)


@reactive.effect
@reactive.event(input.last_730d)
def _():
    _update_date_range(days=730)


@reactive.effect
@reactive.event(input.last_all)
def _():
    # TODO: pretty hacky
    min_all_tables = [
        (col, t[col].cast("timestamp").min().to_pyarrow().as_py())
        for t in [_downloads_data()]
        for col in t.columns
        if ("timestamp" in str(t[col].type()) or "date" in str(t[col].type()))
    ]
    min_all_tables = min([x[1] for x in min_all_tables]) - timedelta(days=1)
    max_now = datetime.now() + timedelta(days=1)

    ui.update_date_range(
        "date_range",
        start=(min_all_tables).strftime("%Y-%m-%d"),
        end=max_now.strftime("%Y-%m-%d"),
    )
