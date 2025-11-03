from gettext import gettext
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from flask import Flask
from datetime import datetime

from meteo.app.widgets.temperature_evolution import TemperatureEvolutionWidget
from meteo.extensions import babel, get_locale
from meteo import defs
from meteo.app.widgets import AtmosphericConditionsWidgets, CurrentWeatherWidget, Widget
from meteo.forecast.forecast import Forecast

# Sample data
# df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10, 11, 12, 13, 14]})

server = Flask(__name__)
server.config["BABEL_TRANSLATIONS_DIRECTORIES"] = "/home/nico/Dev/t/python-dash/locales"
# Initialize the Dash app
app = dash.Dash(
    __name__,
    title=gettext("Weather Dashboard"),
    description=gettext("A dashboard to display weather information."),
    external_scripts=[
        {"src": "https://cdn.tailwindcss.com"},  # tailwind cdn
        {"src": "/assets/tailwind-config.js"},  # custom configuration for tailwind
    ],
    server=server,
)

babel.init_app(app.server, locale_selector=get_locale)


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body class="min-h-screen p-4 md:p-8" id="body">
        <div class="max-w-7xl mx-auto">
        {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

forecast = Forecast.build(app)

header = html.Header(
    id="main-header",
    className="mb-8",
    children=[
        html.Div(
            className="flex items-center justify-between mb-2",
            children=[
                html.H1(
                    gettext("Weather Dashboard"),
                    id="main-title",
                    className="text-3xl md:text-4xl font-bold text-balance",
                ),
                html.Div(
                    id="last-updated",
                    className="text-sm text-muted-foreground flex items-center gap-2",
                    children=[
                        "Last updated:",
                        html.Div(id="last-updated-timestamp"),
                    ],
                ),
            ],
        ),
        html.P("Paris, France", id="location", className="text-muted-foreground"),
        dcc.Store(id="last-updated-store", data=None),
        dcc.Interval(
            id=defs.FAST_REFRESH_INTERVAL_ID,
            interval=defs.FAST_REFRESH_INTERVAL_MS,
            n_intervals=0,
        ),
        dcc.Interval(
            id=defs.WEATHER_UPDATE_INTERVAL_ID,
            interval=defs.WEATHER_UPDATE_INTERVAL_MS,
            n_intervals=0,
        ),
    ],
)

global_config = Widget.Config(app, forecast=forecast)
widgets = [
    CurrentWeatherWidget(global_config),
    AtmosphericConditionsWidgets(global_config),
    TemperatureEvolutionWidget(global_config),
]
app.layout = html.Div(children=[header, *[widget.layout() for widget in widgets]])

for widget in widgets:
    if not isinstance(widget, Widget):
        continue
    widget.setup_callbacks(app)


@app.callback(
    Output("last-updated-timestamp", "children"),
    Input(defs.LAST_UPDATED_ID, "data"),
    Input(defs.FAST_REFRESH_INTERVAL_ID, "n_intervals"),
)
def update_last_updated(last_updated: int, n_intervals: int) -> str:
    if last_updated is None:
        return gettext("Never")

    now = datetime.now()
    diff = now.timestamp() - last_updated
    if diff < 20:
        return gettext("Just now")
    if diff < 60:
        return gettext("Less than a minute ago")

    minutes = int(diff // 60)
    if minutes < 60:
        return gettext(f"{minutes} minute(s) ago")
    hours = minutes // 60
    if hours < 24:
        return gettext(f"{hours} hour(s) ago")
    return gettext(f"{hours // 24} day(s) ago")


if __name__ == "__main__":
    app.run(debug=True)
