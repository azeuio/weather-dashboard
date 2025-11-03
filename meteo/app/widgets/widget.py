import dataclasses
from dash import html, Dash
import js2py
from meteo.forecast import Forecast


class Widget:
    _tailwind_config: dict = {}

    @dataclasses.dataclass
    class Config:
        app: Dash
        forecast: Forecast

    def __init__(self, config: Config):
        self.config = config

    def _load_tailwind_config(self) -> None:
        if not self._tailwind_config:
            try:
                context = js2py.EvalJs()
                with open("assets/tailwind-config.js", "r") as f:
                    js_code = f.read().replace("tailwind.config =", "tailwind_config =")
                    context.execute(js_code)
                self._tailwind_config = context["tailwind_config"].to_dict()
            except Exception as e:
                print(f"Error loading Tailwind config: {e}")
                self._tailwind_config = {}

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
