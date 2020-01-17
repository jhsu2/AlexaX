import logging
import os

from flask import Flask
from flask_ask import Ask, request, session, question, statement

import globalFile
import deez

globalFile.init()

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

STATUSON = ['on', 'high', 'start']
STATUSOFF = ['off', 'low', 'stop']


@ask.launch
def launch():
    speech_text = 'Welcome to Raspberry Pi Automation.'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)


@ask.intent('GpioIntent', mapping={'status': 'status', 'music': 'music'})
def Gpio_Intent(status, music, room):
    if status in STATUSON:
        print("nibba")
        globalFile.taygaloo_cat_en = True
        return statement('turning {} tracking'.format(status))
    elif status in STATUSOFF:
        print("nibber")
        globalFile.taygaloo_cat_en = False
        return statement('turning {} tracking'.format(status))
    elif music != '' and status == '':
        return statement('playing {}'.format(music))
    else:
        return statement('Sorry not possible.')


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False

    app.run(debug=True)
    deez.main()
