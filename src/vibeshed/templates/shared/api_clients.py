"""Common API client wrappers.

Add new clients here as you onboard new services. Each client should:
  - Accept its credential as a constructor arg, falling back to an env var.
  - Raise ``ValueError`` if no credential is available.
  - Use ``requests`` with explicit timeouts.
  - Return parsed JSON or domain objects, not raw responses.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

_DEFAULT_TIMEOUT = 30


class TodoistClient:
    """Minimal Todoist REST v2 client."""

    BASE_URL = "https://api.todoist.com/rest/v2"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TODOIST_API_TOKEN")
        if not self.token:
            raise ValueError("Todoist API token required (TODOIST_API_TOKEN)")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def get_today_tasks(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.BASE_URL}/tasks",
            headers=self._headers(),
            params={"filter": "today"},
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()


class WeatherClient:
    """Minimal OpenWeather current-weather client."""

    URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeather API key required (OPENWEATHER_API_KEY)")

    def get_forecast(self, city: str, units: str = "imperial") -> Dict[str, Any]:
        response = requests.get(
            self.URL,
            params={"q": city, "appid": self.api_key, "units": units},
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
