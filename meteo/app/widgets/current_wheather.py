from gettext import gettext

import datetime
from meteo import defs
from meteo.conditions import WeatherDescription, UvRisk
from meteo.forecast import Forecast
from dash import Input, Output, html, Dash, dcc
from .widget import Widget


class CurrentWeatherWidget(Widget):
    def _current_temp(
        self,
        data: Forecast.CurrentWeather,
    ) -> html.Div:
        weather_condition = WeatherDescription.get_condition(
            data.weather_code, not data.is_day
        )
        return html.Div(
            className="flex items-start gap-6",
            children=[
                html.Img(
                    src=weather_condition.image,
                    alt=weather_condition.description,
                    width="128",
                    height="128",
                ),
                html.Div(
                    children=[
                        html.Div(
                            id="current-temperature",
                            className="text-6xl md:text-7xl font-bold mb-2",
                            children=f"{round(data.temperature, 1)}°{data.unit.upper()}",
                        ),
                        html.Div(
                            id="current-weather-description",
                            className="text-xl text-muted-foreground",
                            children=weather_condition.description,
                        ),
                        html.Div(
                            id="feels-like-temperature",
                            className="text-sm text-muted-foreground mt-1",
                            children=f"Feels like {round(data.feels_like, 1)}°{data.unit.upper()}",
                        ),
                    ],
                ),
            ],
        )

    def _secondary_info(self, *children: list) -> html.Div:
        return html.Div(className="bg-secondary rounded-xl p-4", children=children)

    def layout(self, className: str = "") -> html.Tbody:
        """Returns the layout of the current weather widget."""
        forecast = self.config.forecast
        current_weather_data = forecast.fetch_current_weather()
        daily_weather_data = forecast.fetch_daily_weather()
        uv_risk = UvRisk.from_index(daily_weather_data.uv_index_max)

        return self._create_layout(
            html.Div(
                className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6",
                children=[
                    self._current_temp(current_weather_data),
                    html.Div(
                        className="grid grid-cols-2 gap-4 w-full md:w-auto",
                        children=[
                            self._secondary_info(
                                html.Div(
                                    className="text-sm text-secondary-foreground mb-1",
                                    children=gettext("High / Low"),
                                ),
                                html.Div(
                                    className="text-2xl font-semibold",
                                    children=f"{round(daily_weather_data.temperature_max)}° / {round(daily_weather_data.temperature_min)}°",
                                ),
                            ),
                            self._secondary_info(
                                html.Div(
                                    className="text-sm text-secondary-foreground mb-1",
                                    children=gettext("UV Index"),
                                ),
                                html.Div(
                                    id="uv-index",
                                    className=f"text-2xl font-semibold text-accent text-{uv_risk.color}",
                                    children=f"{round(daily_weather_data.uv_index_max)} {uv_risk.label.capitalize()}",
                                ),
                            ),
                        ],
                    ),
                ],
            ),
            className=f"rounded-2xl p-6 md:p-8 mb-6 {className}",
        )

    def setup_callbacks(self, app: Dash) -> None:
        @app.callback(
            Output(defs.LAST_UPDATED_ID, "data"),
            Output("current-temperature", "children"),
            Output("current-weather-description", "children"),
            Output("feels-like-temperature", "children"),
            Output("uv-index", "children"),
            Output("uv-index", "className"),
            Input("current-weather-interval", "n_intervals"),
        )
        def update_current_weather(n_intervals: int):
            current_weather_data = self.config.forecast.fetch_current_weather()
            daily_weather_data = self.config.forecast.fetch_daily_weather()
            uv_risk = UvRisk.from_index(daily_weather_data.uv_index_max)

            temperature = f"{round(current_weather_data.temperature, 1)}°{current_weather_data.unit.upper()}"
            description = WeatherDescription.get_condition(
                current_weather_data.weather_code, not current_weather_data.is_day
            ).description
            feels_like = gettext(
                f"Feels like {round(current_weather_data.feels_like, 1)}°{current_weather_data.unit.upper()}"
            )
            uv_index = (
                f"{round(daily_weather_data.uv_index_max)} {uv_risk.label.capitalize()}"
            )
            uv_index_class = f"text-2xl font-semibold text-accent text-{uv_risk.color}"

            return (
                datetime.datetime.now().timestamp(),
                temperature,
                description,
                feels_like,
                uv_index,
                uv_index_class,
            )
