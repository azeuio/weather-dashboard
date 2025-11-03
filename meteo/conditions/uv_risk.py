from gettext import gettext
from dataclasses import dataclass


@dataclass
class UvRisk:
    lower_bound: float
    upper_bound: float
    label: str
    color: str

    _UV_RISK_LEVELS = [
        (-float("inf"), 2, gettext("Low"), "green-300"),
        (3, 5, gettext("Moderate"), "yellow-400"),
        (6, 7, gettext("High"), "orange-400"),
        (8, 10, gettext("Very High"), "red-400"),
        (11, float("inf"), gettext("Extreme"), "violet-400"),
    ]

    @staticmethod
    def from_index(uv_index: float) -> "UvRisk":
        for lower, upper, label, color in UvRisk._UV_RISK_LEVELS:
            if lower <= uv_index <= upper:
                return UvRisk(lower, upper, label, color)
        raise ValueError("UV index out of range")
