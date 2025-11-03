import dataclasses
import datetime
import openmeteo_requests
from enum import Enum
from typing import Literal

import pandas as pd
import requests_cache
from retry_requests import retry
from dash import Dash


class Forecast:
    class Coordinates(Enum):
        BERLIN = (52.52, 13.41)
        PARIS = (48.85, 2.35)
        LONDON = (51.51, -0.13)
        NEW_YORK = (40.71, -74.01)
        TOKYO = (35.68, 139.76)

    cache_session: requests_cache.CachedSession
    retry_session: requests_cache.CachedSession
    openmeteo: openmeteo_requests.Client
    _instance = None

    @property
    def hourly_dataframe(self) -> pd.DataFrame:
        return self._hourly_dataframe

    def __init__(self, app: Dash, coordinates: tuple[float, float]):
        self._date_range = range(-2, 3)
        self._hourly_dataframe = pd.DataFrame()
        self._last_update = datetime.datetime.min
        self.app = app
        self.coordinates = coordinates
        self._instance = self

    @classmethod
    def build(
        cls,
        app: Dash,
        date_range: range = range(-2, 8),
        coordinates: Coordinates | tuple[float, float] | None = None,
    ) -> "Forecast":
        """Build a Forecast object with data from Open-Meteo API.

        Args:
            app (Dash): The Dash app instance.
            date_range (range, optional): Range of days for past and forecast data.
                Defaults to range(-2, 3), which includes 2 past days and 3 forecast days.

        Returns:
            Forecast: An instance of the Forecast class with populated data.
        """
        # Setup the Open-Meteo API client with cache and retry on error
        cls.cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        cls.retry_session = retry(cls.cache_session, retries=5, backoff_factor=0.2)
        cls.openmeteo = openmeteo_requests.Client(session=cls.retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below

        forecast = Forecast(
            app,
            (
                (coordinates if isinstance(coordinates, tuple) else coordinates.value)
                if coordinates
                else cls.Coordinates.PARIS.value
            ),
        )
        forecast._date_range = date_range
        forecast._hourly_dataframe = forecast.fetch_data()
        return forecast

    def fetch_data(self):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.coordinates[0],
            "longitude": self.coordinates[1],
            "hourly": "temperature_2m",
            "daily": ["sunrise", "sunset"],
            "current": "temperature_2m",
            "past_days": abs(min(0, self._date_range.start)),
            "forecast_days": self._date_range.stop - 1,
        }
        responses = self.openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }

        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        daily = response.Daily()
        daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()
        return (hourly_dataframe, daily_sunrise, daily_sunset)

    @dataclasses.dataclass
    class CurrentWeather:
        temperature: int = 0
        is_day: int = 0
        feels_like: int = 0
        surface_pressure: int = 0
        weather_code: int = 0
        wind_speed: float = 0.0
        wind_direction: int = 0
        relative_humidity: int = 0
        unit: Literal["C", "F"] = "C"

    def fetch_current_weather(
        self, farenheit: bool = False
    ) -> "Forecast.CurrentWeather":
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 52.52,
            "longitude": 13.41,
            "current": [
                "temperature_2m",
                "is_day",
                "apparent_temperature",
                "surface_pressure",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "relative_humidity_2m",
            ],
            "temperature_unit": "fahrenheit" if farenheit else "celsius",
        }
        responses = self.openmeteo.weather_api(url, params=params)
        response = responses[0]
        current = response.Current()
        if not current:
            return self.CurrentWeather()
        return self.CurrentWeather(
            *(current.Variables(i).Value() for i in range(current.VariablesLength())),
        )

    @dataclasses.dataclass
    class DailyWeather:
        date: str = ""
        temperature_max: float = 0.0
        temperature_min: float = 0.0
        weather_code: int = 0
        sunrise: str = ""
        sunset: str = ""
        uv_index_max: float = 0.0
        uv_index_clear_sky_max: float = 0.0

    def fetch_daily_weather(self, farenheit: bool = False):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 52.52,
            "longitude": 13.41,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "weather_code",
                "sunrise",
                "sunset",
                "uv_index_max",
                "uv_index_clear_sky_max",
            ],
            "temperature_unit": "fahrenheit" if farenheit else "celsius",
        }
        responses = self.openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        if not daily:
            return self.DailyWeather()
        return self.DailyWeather(
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            temperature_max=daily.Variables(0).ValuesAsNumpy()[0],
            temperature_min=daily.Variables(1).ValuesAsNumpy()[0],
            weather_code=daily.Variables(2).ValuesAsNumpy()[0],
            sunrise=daily.Variables(3).ValuesInt64AsNumpy()[0],
            sunset=daily.Variables(4).ValuesInt64AsNumpy()[0],
            uv_index_max=daily.Variables(5).ValuesAsNumpy()[0],
            uv_index_clear_sky_max=daily.Variables(6).ValuesAsNumpy()[0],
        )
