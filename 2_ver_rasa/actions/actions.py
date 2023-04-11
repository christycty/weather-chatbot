from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import spacy
import requests

# function to get current weather for a city using OpenWeatherMap API
def get_weather(city, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(city, api_key)
    response = requests.get(url)
    data = response.json()
    weather = {
        "description": data["weather"][0]["description"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }
    return weather

# function to get rainfall prediction for a city using OpenWeatherMap API
def get_rainfall(city, api_key):
    url = "http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}".format(city, api_key)
    response = requests.get(url)
    data = response.json()
    rain = []
    for item in data["list"]:
        if "rain" in item and "3h" in item["rain"]:
            rain.append(item["rain"]["3h"])
        else:
            rain.append(0)
    return sum(rain) / len(rain)

# function to get typhoon signal for a city using OpenWeatherMap API
def get_typhoon(city, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(city, api_key)
    response = requests.get(url)
    data = response.json()
    if "typhoon" in data["weather"][0]["description"]:
        return "Typhoon signal is up in {}.".format(city)
    else:
        return "There are currently no typhoon signal in {}.".format(city)

def get_message(query, text):
    # insert your own api key
    api_key = ""

    # Get location
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    loc = None
    for ent in doc.ents:
        # a geopolitical entity is found
        if ent.label_ == "GPE" or ent.label_ == "LOC":
            loc = ent.text
            break
    
    # check location
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(loc, api_key)
    response = requests.get(url).json()
    
    if loc == None or response["cod"] == "404":
        message = "cannot identify your location specified :( Please enter another location"
        return message
    
    if query == "weather":
        weather = get_weather(loc, api_key)
        message = "Weather in {}: {}°C, {}% humidity, {} m/s windspeed, {}.".format(loc, weather["temperature"], weather["humidity"], weather["wind_speed"], weather["description"])

    elif query == "rainfall":
        rainfall = get_rainfall(loc, api_key)
        message = "Rainfall prediction for {} in the next 5 days: {} mm.".format(loc, rainfall)

    elif query == "typhoon":
        message = get_typhoon(loc, api_key)

    else:
        message = "Sorry, I cannot understand your query. Please query the weather, rainfall prediction or typhoon signal for a specific location"
    
    return message


class ActionAskWeather(Action):
    def name(self) -> Text:
        return "action_ask_weather"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = get_message("weather", (tracker.latest_message)['text'])
        dispatcher.utter_message(text=message)

        return []

class ActionAskRainfall(Action):
    def name(self) -> Text:
        return "action_ask_rainfall"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = get_message("rainfall", (tracker.latest_message)['text'])
        dispatcher.utter_message(text=message)

        return []

class ActionAskTyphoon(Action):
    def name(self) -> Text:
        return "action_ask_typhoon"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = get_message("typhoon", (tracker.latest_message)['text'])
        dispatcher.utter_message(text=message)

        return []