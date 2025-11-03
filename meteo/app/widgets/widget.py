import dataclasses
from dash import html, Dash
from meteo.forecast import Forecast


class Widget:
    @dataclasses.dataclass
    class Config:
        app: Dash
        forecast: Forecast

    def __init__(self, config: Config):
        self.config = config

    def _create_layout(
        self, *children: list[html.Tbody], className: str = "", section: bool = True
    ) -> html.Tbody:
        tag = html.Section if section else html.Div
        return tag(
            className=f"bg-card border border-border rounded-xl p-5 {className}",
            children=children,
        )

    def layout(self, className: str = "") -> html.Tbody:
        """Returns the layout of the widget."""
        raise NotImplementedError("Subclasses must implement the layout method.")

    def setup_callbacks(self, app: Dash) -> None:
        """Sets up the callbacks for the widget."""
        pass
