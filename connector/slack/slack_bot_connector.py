import os
import time
import requests
from slackclient import SlackClient


# min required is SLACK_BOT_TOKEN
BOT_ID = os.environ.get("SLACK_BOT_ID")


def handle_command(user_id, user_entry, user_chan):
    response = "Hum ... I can't access to natural language processing service. :robot_face:"
    try:
        r = requests.get('http://nlp:5000/api/message/' + user_id + '/' + user_chan + '/' + user_entry + '/').json()
        if r and 'response' in r and r['response']['message']:
            print("chat_response: " + r['response']['message'].encode("utf8"))
            response = r['response']['message']
    except ValueError:
        print("chat_response: can't decode json from nlp api")
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                return output['user'], output['text'].encode("utf8"), output['channel']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    if slack_client.rtm_connect():
        print("gary connected, ready to handle command!")
        while True:
            # rtm_read() read everything from websocket !
            rtm_message = slack_client.rtm_read()
            user_id, command, channel = parse_slack_output(rtm_message)
            if command and channel and user_id != BOT_ID:
                handle_command(user_id, command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
