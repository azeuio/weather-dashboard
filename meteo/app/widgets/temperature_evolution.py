import math
from datetime import datetime
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go

from meteo import defs
from .widget import Widget


class TemperatureEvolutionWidget(Widget):
    GRAPH_ID = "temperature-evolution-graph"

    def layout(self) -> html.Div:
        """Returns the layout of the temperature evolution widget."""
        self._load_tailwind_config()
        colors = (
            self._tailwind_config.get("theme", {}).get("extend", {}).get("colors", {})
        )
        primary_color = colors.get("primary", "#FFFFFF")
        accent_color = colors.get("accent", "#FFFFFF")

        return super()._create_layout(
            dcc.Graph(
                id=self.GRAPH_ID,
                className="graph-container",
                config={
                    "displayModeBar": False,
                    "responsive": False,
                    "staticPlot": True,
                },
                figure={
                    "data": [
                        go.Scatter(
                            x=list(
                                datetime.now() + pd.Timedelta(hours=i)
                                for i in range(10)
                            ),
                            y=list(math.sin(x) for x in range(10)),
                            mode="lines",
                            line=dict(
                                color=f"{primary_color}", width=2, shape="spline"
                            ),  # Change line color here
                            marker={"colorbar": {"bgcolor": "rgb(255, 255, 255)"}},
                            showlegend=False,
                        ),
                        # vertical line for current time
                        go.Scatter(
                            x=[datetime.now(), datetime.now()],
                            y=[-1, 1],
                            mode="lines",
                            line=dict(color=accent_color, width=2, dash="dash"),
                            showlegend=False,
                        ),
                    ],
                    "layout": go.Layout(
                        title=dict(
                            text="Temperature Prediction",
                            font=dict(color="white"),
                        ),
                        coloraxis=dict(colorbar=dict(bgcolor="rgb(255, 255, 255)")),
                        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
                        paper_bgcolor="rgba(0,0,0,0)",  # Change background color here
                        font=dict(size=14),
                        xaxis=dict(
                            title=dict(text="Time", font=dict(color="white")),
                            color="gray",
                            showgrid=False,
                        ),
                        yaxis=dict(
                            title=dict(
                                text="Temperature (°C)", font=dict(color="white")
                            ),
                            color="gray",
                            gridcolor="gray",
                        ),
                    ),
                },
            ),
        )

    def setup_callbacks(self, app):
        super().setup_callbacks(app)

        @app.callback(
            Output(self.GRAPH_ID, "figure"),
            Input(defs.WEATHER_UPDATE_INTERVAL_ID, "n_intervals"),
            State(self.GRAPH_ID, "figure"),
        )
        def update_temperature_graph(n_intervals, existing_figure):
            forecast = self.config.forecast
            hourly_data = forecast.fetch_hourly_weather(past_days=1, forecast_days=1)
            # print(hourly_data[0:5])  # Print first 5 entries for debugging
            # return existing_figure

            fig = existing_figure
            fig["data"][0]["x"] = [
                data.time
                for data in hourly_data
                if data.time >= datetime.now() - pd.Timedelta(hours=6)
            ]
            fig["data"][0]["y"] = [
                data.temperature_2m
                for data in hourly_data
                if data.time >= datetime.now() - pd.Timedelta(hours=6)
            ]
            max_temp = max(
                data.temperature_2m
                for data in hourly_data
                if data.time >= datetime.now() - pd.Timedelta(hours=6)
            )
            min_temp = min(
                data.temperature_2m
                for data in hourly_data
                if data.time >= datetime.now() - pd.Timedelta(hours=6)
            )
            fig["data"][1]["x"] = [datetime.now(), datetime.now()]
            fig["data"][1]["y"] = [min_temp - 1, max_temp + 1]

            return fig


__all__ = ["TemperatureEvolutionWidget"]
