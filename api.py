from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# Replace with your OpenWeatherMap API key
API_KEY = '84b9c8b8572c7ea2ffcf336acafda876'

# Replace with your Google Maps API key
GOOGLE_MAPS_API_KEY = 'AIzaSyC9wrCfjEeDkByiR4Gxba_LQUou3F2mqdw'

@app.route('/')
def map_view():
    city = request.args.get('city', 'London')
    weather_data = get_weather_data(city)

    # Determine the alert color, message, and voice alert
    if weather_data['temp'] >= 20:
        alert_color = 'red'
        alert_message = 'Extreme heat alert! Temperature is 40°C or above.'
        voice_alert = 'Extreme heat alert! Temperature is 40 degrees Celsius or above.'
    elif weather_data['temp'] >= 15:
        alert_color = 'yellow'
        alert_message = 'Heat alert! Temperature is between 30°C and 35°C.'
        voice_alert = 'Heat alert! Temperature is between 30 and 35 degrees Celsius.'
    elif 'rain' in weather_data['description'].lower():
        if weather_data['temp'] >= 15:
            alert_color = 'red'
            alert_message = 'Heavy rainfall alert! Temperature is 30°C or above with rainfall.'
            voice_alert = 'Heavy rainfall alert! Temperature is 30 degrees Celsius or above with rainfall.'
        else:
            alert_color = 'yellow'
            alert_message = 'Rainfall alert. It is raining.'
            voice_alert = 'Rainfall alert. It is raining.'
    else:
        alert_color = 'green'
        alert_message = 'No severe weather alerts.'
        voice_alert = 'No severe weather alerts.'

    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Forecasting Map</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            #map {
                height: 500px;
                width: 100%;
            }
            .alert {
                padding: 10px;
                color: white;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
            }
            .red {
                background-color: red;
            }
            .yellow {
                background-color: yellow;
                color: black;
            }
            .green {
                background-color: green;
            }
        </style>
    </head>
    <body>
        <h1>Weather Forecasting Map</h1>
        <form method="get">
            <label for="city">City:</label>
            <input type="text" id="city" name="city" value="{{ city }}">
            <input type="submit" value="Get Weather">
        </form>
        <div class="alert {{ alert_color }}">{{ alert_message }}</div>
        <div id="map"></div>
        <script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}"></script>
        <script>
            function initMap() {
                var cityLocation = { lat: {{ lat }}, lng: {{ lon }} };
                var map = new google.maps.Map(document.getElementById('map'), {
                    zoom: 13,
                    center: cityLocation
                });

                var contentString = '<div><strong>{{ city }}</strong><br>' +
                                    '<img src="{{ icon_url }}" alt="Weather Icon"><br>' +
                                    'Temperature: {{ temp }}°C<br>' +
                                    'Weather: {{ description }}</div>';

                var infowindow = new google.maps.InfoWindow({
                    content: contentString
                });

                var marker = new google.maps.Marker({
                    position: cityLocation,
                    map: map,
                    title: '{{ city }}'
                });

                marker.addListener('click', function() {
                    infowindow.open(map, marker);
                });

                infowindow.open(map, marker);
            }
            
            function playVoiceAlert(message) {
                var utterance = new SpeechSynthesisUtterance(message);
                utterance.pitch = 1;
                utterance.rate = 1;
                utterance.volume = 1;
                window.speechSynthesis.speak(utterance);
            }
            
            google.maps.event.addDomListener(window, 'load', function() {
                initMap();
                {% if alert_color == 'red' or alert_color == 'yellow' %}
                playVoiceAlert('{{ voice_alert }}');
                {% endif %}
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content, city=city, lat=weather_data['lat'], lon=weather_data['lon'], 
                                  temp=weather_data['temp'], description=weather_data['description'], 
                                  icon_url=weather_data['icon_url'], google_maps_api_key=GOOGLE_MAPS_API_KEY,
                                  alert_color=alert_color, alert_message=alert_message, voice_alert=voice_alert)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and 'coord' in data:
        weather = {
            'city': data['name'],
            'lat': data['coord']['lat'],
            'lon': data['coord']['lon'],
            'temp': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
        }
    else:
        weather = {
            'city': 'Unknown',
            'lat': 0,
            'lon': 0,
            'temp': 'N/A',
            'description': 'N/A',
            'icon_url': 'http://openweathermap.org/img/wn/01d@2x.png'
        }

    return weather

if __name__ == "__main__":
    app.run(debug=True)
    