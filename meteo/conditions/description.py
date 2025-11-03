from dataclasses import dataclass
import os
import json


@dataclass
class WeatherCondition:
    code: int
    description: str
    image: str


class WeatherDescription:
    """A class to get weather descriptions based on weather codes."""

    JSON_PATH = os.path.join(os.path.dirname(__file__), "weather_descriptions.json")
    _descriptions = None

    @classmethod
    def _load_descriptions(cls):
        if cls._descriptions is None:
            with open(cls.JSON_PATH, "r", encoding="utf-8") as f:
                cls._descriptions = json.load(f)

    @classmethod
    def get_condition(cls, weather_code: int, is_night: bool) -> WeatherCondition:
        cls._load_descriptions()
        desc = cls._descriptions.get(str(int(weather_code)), {})
        if is_night:
            desc = desc.get("night")
        else:
            desc = desc.get("day")
        return WeatherCondition(
            code=weather_code,
            description=desc.get("description", "No description available"),
            image=desc.get("image", "unknown.png"),
        )
