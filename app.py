from flask import Flask, render_template, request
import requests
import os
from datetime import datetime, timezone

app = Flask(__name__, static_folder='static', static_url_path='/static')  # Initialize Flask app
api_key = '270569dd4a03b630b13d0cbf67f0cab5'  # API key for OpenWeatherMap

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for weather data
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    # Handling form submission
    if request.method == 'POST':
        city = request.form['city']  # Get city name from form
        units = request.form['units']  # Get units from form
    else:
        # If not a POST request, retrieve city and units from query parameters
        city = request.args.get('city')
        units = request.args.get('units', 'metric')  # Default to metric if units not provided

    # Construct API URL with city name and units
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}'
    response = requests.get(url)  # Send request to OpenWeatherMap API

    # Handling API response
    if response.status_code == 200:
        data = response.json()  # Convert response to JSON format
        # Extract weather data from JSON response
        temperature = data['main'].get('temp', None)
        feels_like = data['main'].get('feels_like', None)
        pressure = data['main'].get('pressure', None)
        humidity = data['main'].get('humidity', None)
        description = data['weather'][0].get('description', None)
        icon = data['weather'][0].get('icon', None)
        wind_speed = data['wind'].get('speed', None)
        wind_deg = data['wind'].get('deg', None)
        cloudiness = data['clouds'].get('all', None)

        # Get timezone offset from API response (in seconds)
        timezone_offset = data['timezone']

        # Convert Unix timestamps to datetime objects in the location's timezone
        sunrise_dt = datetime.fromtimestamp(data['sys']['sunrise'] + timezone_offset, timezone.utc)
        sunset_dt = datetime.fromtimestamp(data['sys']['sunset'] + timezone_offset, timezone.utc)

        # Format datetime objects to desired format
        sunrise_time = sunrise_dt.strftime('%I:%M %p')
        sunset_time = sunset_dt.strftime('%I:%M %p')

        # Determine display units based on selected units
        units_display = "Celsius" if units == "metric" else "Fahrenheit"
        latitude = data['coord'].get('lat', None)
        longitude = data['coord'].get('lon', None)

        # Handle missing data
        if any(value is None for value in
               [temperature, feels_like, pressure, humidity, description, icon, wind_speed, wind_deg, cloudiness,
                sunrise_time, sunset_time, latitude, longitude]):
            return render_template('error.html', error_message="Incomplete weather data received from the API.")

        # Render weather template with retrieved data
        return render_template('weather.html', city=city, temperature=temperature, feels_like=feels_like,
                               pressure=pressure, humidity=humidity, description=description, icon=icon,
                               wind_speed=wind_speed, wind_deg=wind_deg, cloudiness=cloudiness,
                               sunrise_time=sunrise_time, sunset_time=sunset_time, units_display=units_display,
                               latitude=latitude, longitude=longitude)
    else:
        # Render error template if API request fails
        return render_template('error.html', error_message="Failed to get weather data from the API.")

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app

