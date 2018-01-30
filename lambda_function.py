"""
Komponentenbasierte Softwareentwicklung
Alexa Skill
Philipp Clausing
"""

from __future__ import print_function
import socket
import sys
import json
import requests

# --------------- Hilfe funktionen zum bauen der antworten ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Computersteuerung - ' + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Willkommen"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me your favorite color by saying, " \
                    "my favorite color is red"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your favorite color by saying, " \
                    "my favorite color is red."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session beendet"
    speech_output = "Danke das du unseren Alexa Skill verwendet hast." \
                    "Einen schoenen Tag!"
    # Beendet die Sitzung und den Skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def koppeln(intent, session):
    """ Koppelt den VA mit dem Server """
    host = "ec2-54-93-34-8.eu-central-1.compute.amazonaws.com"
    port = 51337

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'secretw_one' in intent['slots']:
        word1 = intent['slots']['secretw_one']['value']
        word2 = intent['slots']['secretw_two']['value']
        userID = session['user']['userId']
        session_attributes = create_koppeln_attributes(word1,word2,userID)
        speech_output = "Koppeln beginnt mit " + \
                        word1 + \
                        " und " + \
                        word2 + \
                        " ."
        reprompt_text = "Du kannst mir sagen ich soll mich koppeln mit " \
                        "wort1 und wort2"
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(None)
            sock.connect((host,port))
            sock.sendall(json.dumps(session_attributes))
            
            received = sock.recv(1024)
        finally:
            sock.close()
            
        
    else:
        speech_output = "Da hat irgendwas nicht geklappt. " \
                        "Bitte versuche es erneut."
        reprompt_text = "Ich bin nicht sicher was nicht geklappt hat. " \
                        "Du kannst mir sagen ich soll mich koppeln, mit: " \
                        "verbinden mit wort1 word2."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def create_koppeln_attributes(w1,w2,userid):
    koppeln_data = {}
    koppeln_data['koppeln'] = {}
    koppeln_data['koppeln']['word1'] = w1
    koppeln_data['koppeln']['word2'] = w2
    koppeln_data['device'] = 'alexa'
    koppeln_data['deviceID'] = userid
    return koppeln_data


def entkoppeln(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def befehl(intent, session):
    """ Sendet Befehl an Server """
    host = "ec2-54-93-34-8.eu-central-1.compute.amazonaws.com"
    port = 41337
    
    session_attributes = {}
    reprompt_text = None
    card_title = intent['name']
    userID = session['user']['userId']
    should_end_session = True
    utterance_recognized = False

    """ Utterance: starte {program_name} """
    if 'program_name' in intent['slots'] and 'value' not in intent['slots']['command']:
        utterance_recognized = True
        program = intent['slots']['program_name']['value']
        instruction = program
        
        session_attributes = create_befehl_attributes(instruction,userID)
        speech_output = "Der Befehl: " + \
                        instruction + \
                        " wurde gesendet."
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(None)
            sock.connect((host,port))
            sock.sendall(json.dumps(session_attributes))
            
            received = sock.recv(1024)
        finally:
            sock.close()
            
    """ Utterance: sag {program_name} {command} """
    if 'value' in intent['slots']['program_name'] and 'value' in intent['slots']['command']:
        utterance_recognized = True
        program = intent['slots']['program_name']['value']
        command = intent['slots']['command']['value']
        instruction = program
        
        session_attributes = create_befehlcommand_attributes(instruction,command,userID)
        speech_output = "Der Befehl: " + \
                        instruction + \
                        " " + \
                        command + \
                        " wurde gesendet."
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(None)
            sock.connect((host,port))
            sock.sendall(json.dumps(session_attributes))
            
            received = sock.recv(1024)
        finally:
            sock.close()
            
    """ fuehre {command} aus """
    """ serverseitig noch nicht implementiert"""
    
    if utterance_recognized == False:
        speech_output = "Da hat irgendwas nicht geklappt. " \
                        "Bitte versuche es erneut."
        reprompt_text = "Ich bin nicht sicher was nicht geklappt hat. " \
                        "Du kannst mir sagen ich soll ein Programm starten, mit: " \
                        "starte Programmname."

    # reprompt_text auf none setzen signalisiert das den skill beenden wollen
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def create_befehl_attributes(instruction,userid):
    befehl_data = {}
    befehl_data['instruction'] = instruction
    befehl_data['device'] = 'alexa'
    befehl_data['deviceID'] = userid
    return befehl_data
    
def create_befehlcommand_attributes(instruction,task,userid):
    befehl_data = {}
    befehl_data['instruction'] = instruction
    befehl_data['task'] = task
    befehl_data['device'] = 'alexa'
    befehl_data['deviceID'] = userid
    return befehl_data


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "koppeln":
        return koppeln(intent, session)
    elif intent_name == "entkoppeln":
        return entkoppeln(intent, session)
    elif intent_name == "befehl":
        return befehl(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
