# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import os
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

import requests
import time
import datetime
import json


from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome I am a weather bot.. Which city's weather would you like to know?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

#hello
class GetWeatherHandler(AbstractRequestHandler):
    """Handler for Get Weather Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetWeather")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        slots = handler_input.request_envelope.request.intent.slots
        city = slots['city'].value
        date = slots['date'].value
        index =0
        
        if date == None:
            api_address = "http://api.openweathermap.org/data/2.5/weather?appid=e74a0e76b219fdc73d7011c2190babfb&units=metric&q="
            url = api_address + city
            json_data = requests.get(url).json()
            formatted_json = json_data['weather'][0]['main']
            min_temp= json_data['main']['temp_min']
            temp = json_data['main']['temp']
            name = json_data['name']
            sys = json_data['sys']['country']
            description = json_data['weather'][0]['description']
            attributes_manager = handler_input.attributes_manager
            weather_attributes = {
            "city": city,
            "date": date,
            "index": index
         }
            attributes_manager.persistent_attributes = weather_attributes
            attributes_manager.save_persistent_attributes()
            if formatted_json == "Clouds":
                speak_output = "The temperature is {} degrees Celsius in {}. It is cloudy, with a minimum temperature of {}.".format(temp,city,min_temp)
                card_title ="Weather in {}.".format(city)
                card_text = "It is cloudy. The temperature is {}".format(temp)
                card_image =  "http://openweathermap.org/img/wn/10d@2x.png"
            elif description == "light rain":
                card_title = "Weather in {}".format(city)
                card_text = "It is {} degrees Celsius right now".format(temp)
                speak_output = "It is raining in {}. The average temperature is expected to be {:.2f} degree Celcius.".format(city,temp)
            else:
                card_title = "Weather in {}".format(city)
                card_text = "It is {} degrees Celsius right now".format(temp)
                speak_output = "The weather is {}, {} and temp is {} degrees celsius in {} {}.".format(formatted_json, description, temp, city, sys)
        else:
            date_string = date + ", 12:0:0"
            date1 = datetime.datetime.strptime(date_string, "%Y-%m-%d, %H:%M:%S")
            #date1 = datetime.datetime.strptime(date, "%Y-%m-%d")
            udate = datetime.datetime.timestamp(date1)
            #console.log("udate VALUE IS XX" + udate + "XX");
            # print(udate)
            speak_output = ''
            #api_address = "http://api.openweathermap.org/data/2.5/weather?appid=e74a0e76b219fdc73d7011c2190babfb&units=metric&q="
            api_address = "https://pro.openweathermap.org/data/2.5/forecast/climate?appid=e74a0e76b219fdc73d7011c2190babfb&units=metric&q="
            url = api_address + city
            json_data = requests.get(url).json()
            time_zone = json_data['city']['timezone']
            hr = (time_zone/60/60)
            hr = int(12-hr)
            date_string_2 = date + ", " +str(hr)+":0:0"
            print(date_string_2)
            date2 = datetime.datetime.strptime(date_string_2, "%Y-%m-%d, %H:%M:%S")
            udate2 = datetime.datetime.timestamp(date2)
            for i in range(30):
                if udate2 == json_data['list'][i]['dt']:
                    index = i;
                    
            
            attributes_manager = handler_input.attributes_manager
            weather_attributes = {
            "city": city,
            "date": date,
            "index": index
         }
            attributes_manager.persistent_attributes = weather_attributes
            attributes_manager.save_persistent_attributes()
            temp = json_data['list'][index]['temp']
            #description = json_data['list'][index]['description']
            description = json_data['list'][index]['weather'][0]['description']
            #print(temp)
            #temp_max = json_data['list'][index]['temp']['max']
            #temp_min = json_data['list'][index]['temp']['min']
            avg_temp = sum(temp.values())/6
            #temp = json_data['list'][0]['temp']['max']
            if description == "light rain":
                speak_output = "It is raining in {}. The average temperature is expected to be {:.2f} degree Celsius.".format(city,avg_temp)
                card_title = "Weather in {}".format(city)
                card_text = "It is {:.2f} degrees Celsius right now".format(avg_temp)
            else:
                speak_output = "{}, average temperature is expected to be {:.2f} degree Celsius in {}.".format(description,avg_temp,city)
                card_title = "Weather in {}".format(city)
                card_text = "{}, with a temperature of {:.2f} degrees Celsius".format(description,avg_temp)
            #speak_output = "The weather is {}, {} and temp is {} of {} in {}.".format(formatted_json, description, temp, name, sys)
        repromptOutput = " If you'd like to know the weather of any other city, please ask."
        return (
            handler_input.response_builder
                .speak(speak_output).set_card(SimpleCard(card_title, card_text))
                .ask(repromptOutput)
                .response
        )

class GetDetailsHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("city" in attr and "date" in attr and "index" in attr)
        
        return attributes_are_present and ask_utils.is_intent_name("GetDetails")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        city = attr['city']
        date = attr['date']
        index = attr['index']
        slots = handler_input.request_envelope.request.intent.slots
        if slots['request'].value == None:
            hum = slots['request'].slot_value.values[0].value
            wind = slots['request'].slot_value.values[1].value
        else:
            h_w = slots['request'].value
        #win = slots['request']['slotValue']
        
        if date == None:
            api_address = "http://api.openweathermap.org/data/2.5/weather?appid=e74a0e76b219fdc73d7011c2190babfb&units=metric&q="
            url = api_address + city
            json_data = requests.get(url).json()
            speak_output = "{}".format(slots['request'].value)
            if slots['request'].value == None:
                humidity = json_data['main']['humidity']
                wind_speed = json_data['wind']['speed']
                speak_output = "The wind speed is around {} kilometers per hour. The humidity should be {}%".format(wind_speed, humidity)
            else:
                if h_w == "humidity" or h_w == "humid":
                    humidity = json_data['main']['humidity']
                    speak_output = "The humidity will be {}%".format(humidity)
                else:
                    wind_speed = json_data['wind']['speed']
                    speak_output = "The wind speed is {} kilometers per hour".format(wind_speed)
        else:
            api_address = "https://pro.openweathermap.org/data/2.5/forecast/climate?appid=e74a0e76b219fdc73d7011c2190babfb&units=metric&q="
            url = api_address + city
            json_data = requests.get(url).json()
            if slots['request'].value == None:
                humidity = json_data['list'][index]['humidity']
                wind_speed = json_data['list'][index]['speed']
                speak_output = "The wind speed will be around {} kilometers per hour. The humidity will be {}%".format(wind_speed, humidity)
            else:
                if h_w == "humidity" or h_w == "humid":
                    humidity = json_data['list'][index]['humidity']
                    speak_output = "The humidity will be {}%".format(humidity)
                else:
                    wind_speed = json_data['list'][index]['speed']
                    speak_output = "The wind speed will be {} kilometers per hour".format(wind_speed)
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class OtherHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Other")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello,How we can help you? You can say that tell me new york tipsy weather."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello,How we can help you? You can say that tell me new york tipsy weather."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye! see you soon."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter=s3_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetWeatherHandler())
sb.add_request_handler(GetDetailsHandler())
sb.add_request_handler(OtherHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()