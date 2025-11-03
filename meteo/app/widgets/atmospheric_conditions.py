from .widget import Widget
from dash import html
from dash_svg import Svg, Path

arrow = Svg(
    children=[
        Path(
            d="M14 5l7 7m0 0l-7 7m7-7H3",
            stroke="currentColor",
            strokeWidth="2",
            strokeLinejoin="round",
            strokeLinecap="round",
        )
    ],
    className="w-5 h-5 text-primary",
    fill="none",
    viewBox="0 0 24 24",
)


cloud = Svg(
    children=[
        Path(
            d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z",
            stroke="currentColor",
            strokeWidth="2",
            strokeLinejoin="round",
            strokeLinecap="round",
        )
    ],
    className="w-5 h-5 text-primary",
    fill="none",
    viewBox="0 0 24 24",
)

eye = Svg(
    children=[
        Path(
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z",
            stroke="currentColor",
            strokeWidth="2",
            strokeLinejoin="round",
            strokeLinecap="round",
        ),
        Path(
            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
            stroke="currentColor",
            strokeWidth="2",
            strokeLinejoin="round",
            strokeLinecap="round",
        ),
    ],
    className="w-5 h-5 text-primary",
    fill="none",
    viewBox="0 0 24 24",
)

rising = Svg(
    children=[
        Path(
            d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
            stroke="currentColor",
            strokeWidth="2",
            strokeLinejoin="round",
            strokeLinecap="round",
        )
    ],
    className="w-5 h-5 text-primary",
    fill="none",
    viewBox="0 0 24 24",
)


class AtmosphericConditionsWidgets(Widget):
    def _sub_widget_layout(
        self,
        icon: Svg,
        label: str,
        value: str,
        unit: str,
        section: bool = True,
    ) -> html.Div:
        """Returns the layout of a sub-widget for atmospheric conditions."""
        container_classes = (
            "bg-card border border-border rounded-xl p-5" if section else ""
        )
        return html.Div(
            children=[
                html.Div(
                    children=[
                        icon,
                        html.Span(
                            children=label,
                            className="text-sm text-muted-foreground",
                        ),
                    ],
                    className="flex items-center gap-2 mb-3",
                ),
                html.Div(
                    children=value,
                    className="text-3xl font-bold mb-1",
                ),
                html.Span(
                    children=unit,
                    className="text-sm text-secondary-foreground",
                ),
            ],
            className=container_classes,
        )

    def layout(self, className: str = "") -> html.Tbody:
        """Returns the layout of the current weather widget."""
        return html.Section(
            children=[
                self._sub_widget_layout(
                    label="Wind", value="12", unit="Km/h NW", icon=arrow
                ),
                self._sub_widget_layout(
                    label="Humidity", value="20", unit="%", icon=cloud
                ),
                self._sub_widget_layout(
                    label="Visibility", value="10", unit="Km", icon=eye
                ),
                self._sub_widget_layout(
                    label="Pressure", value="1000", unit="hectopascals", icon=rising
                ),
            ],
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-transparent border-0",
        )
