#!/usr/bin/python3
import redis
import sys
import time
import re
import urllib
from slackclient.client import SlackClient

def __main__():
    speak_response("The cooker bot is starting now.")
    token='xxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    sc = SlackClient(token)
    if sc.rtm_connect():
        print("success.")

        order = re.compile('.*set_temperature:(\d+).*')
        order_report = re.compile('.*report_temperature.*')

        try:
            while True:
                messages = sc.rtm_read()
                for m in messages:
                    if 'attachments' in m and 'pretext' in m['attachments'][0]:
                        match = order.match(m['attachments'][0]['pretext'])
                        match_report = order_report.match(m['attachments'][0]['pretext'])
                        if match:
                            print(match.group(1))
                            value=float(match.group(1))
                            print("ok, let's set %s" % {value})
                            current = set_temp(value)
                            speak_response("The target temperature has been updated to %s degrees" % {current})
                        elif match_report:
                            current = get_current_temp()
                            print("current " + current)
                            speak_response("The cooker's current temperature is %s degrees" % {current})
                        else:
                            print(m['content'])
                    else:
                        print(messages)
        except KeyboardInterrupt:
            print("done")
            return 0
        
        time.sleep(1)
            
    else:
        print("failed")

def speak_response(message):
    try:
        base='http://192.168.xxx.xxx:5000/say/?%s' # google-home-notifier
        query=urllib.parse.urlencode({'text':message, 'lang':'en'})
        print(query)
        url=base % {query}
        print(url)
        c = urllib.request.urlopen(url).read()
        print(c)
    except urllib.error.HTTPError:
        print ("Failed to request to say.")

def set_temp(temperature):
    pi_host='192.168.xxx.xxx' # Redis
    r = redis.Redis(host=pi_host, port=6379, db=0)
    if (r.set('cooker_target_temperature', str(temperature))):
        print ("succeed.")
    else:
        print ("failed to set value")

    current = str(float(r.get('cooker_target_temperature')))
    print ("current setpoint: %s" % {current})
    return current

def get_current_temp():
    pi_host='192.168.xxx.xxx'
    r = redis.Redis(host=pi_host, port=6379, db=0)
    current = str(float(r.get('cooker_current_temperature')))
    print ("current temperature: %s" % {current})
    return current

    
__main__()

