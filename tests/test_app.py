import unittest
from app import app
import responses
from datetime import datetime, timezone

class TestWeatherApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.mock_weather_data = {
            "coord": {"lon": -0.1257, "lat": 51.7520},
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
            "base": "stations",
            "main": {"temp": 280.32, "feels_like": 278.15, "temp_min": 279.15, "temp_max": 281.15, "pressure": 1012, "humidity": 81},
            "visibility": 10000,
            "wind": {"speed": 1.5, "deg": 350},
            "clouds": {"all": 1},
            "dt": 1485789600,
            "sys": {"type": 1, "id": 5091, "country": "GB", "sunrise": 1485762037, "sunset": 1485794875},
            "id": 2643743,
            "name": "London",
            "cod": 200,
            "timezone": 0  # Add timezone to the mock data
        }

    @responses.activate
    def test_weather_api_call_success(self):
        responses.add(
            responses.GET,
            "http://api.openweathermap.org/data/2.5/weather",
            json=self.mock_weather_data,
            status=200,
        )
        response = self.app.post("/weather", data={"city": "London", "units": "metric"})
        data = response.data.decode()

        # Asserting for the successful API response (200)
        self.assertEqual(response.status_code, 200)
        # Asserting weather data in response
        self.assertIn("London", data)
        self.assertIn("280.32", data)
        self.assertIn("Feels like: 278.15\u00b0 Celsius", data)
        self.assertIn("clear sky", data)


    @responses.activate
    def test_weather_api_call_invalid_city(self):
        # Mocking the API response for an invalid city
        responses.add(
            responses.GET,
            "http://api.openweathermap.org/data/2.5/weather",
            json={"cod": "404", "message": "city not found"},
            status=404,
        )

        # Sending a request to the app with an invalid city
        response = self.app.post("/weather", data={"city": "InvalidCity", "units": "metric"})
        data = response.data.decode()

        # Asserting for a successful response (200), even though the city is invalid
        self.assertEqual(response.status_code, 200)

        # Check for error message that the city is not found
        self.assertIn("Oops! Something went wrong...", data)


    @responses.activate
    def test_weather_api_call_fahrenheit(self):
        # Create a copy of mock_weather_data and change the temperature to Fahrenheit
        mock_weather_data = self.mock_weather_data.copy()
        mock_weather_data['main']['temp'] = 80.6  # Fahrenheit temperature
        mock_weather_data['main']['feels_like'] = 78.8  # Fahrenheit feels_like temperature

        # Add a mock response for the API call with Fahrenheit temperature
        responses.add(
            responses.GET,
            "http://api.openweathermap.org/data/2.5/weather",
            json=mock_weather_data,
            status=200,
        )

        # Sending a request to the app with units set to imperial (Fahrenheit)
        response = self.app.post("/weather", data={"city": "London", "units": "imperial"})
        data = response.data.decode()

        # Asserting the response status code (200 - OK)
        self.assertEqual(response.status_code, 200)
        # Asserting data present in the response for London city
        self.assertIn("London", data)
        self.assertIn("80.6", data)
        self.assertIn("Feels like: 78.8\u00b0 Fahrenheit", data)  # Check feels like temp in Fahrenheit
        self.assertIn("Fahrenheit", data)


    @responses.activate
    def test_weather_api_call_missing_data(self):
        # Create a mock response with missing temperature data
        mock_weather_data = self.mock_weather_data.copy()
        mock_weather_data['main'].pop('temp')
        responses.add(
            responses.GET,
            "http://api.openweathermap.org/data/2.5/weather",
            json=mock_weather_data,
            status=200,
        )

        # Send a request to your app
        response = self.app.post("/weather", data={"city": "London", "units": "metric"})
        data = response.data.decode()

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if an error message is displayed
        self.assertIn("Oops! Something went wrong...", data)

if __name__ == "__main__":
    unittest.main()
