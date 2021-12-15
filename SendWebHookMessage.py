import os
import requests
import json
from datetime import date, datetime
from dotenv import load_dotenv


webhookurl = os.getenv('webhook')


def SendMessage(title:str,description:str, username:str = "StealthyBotAlerts",url:str =webhookurl):
    """sends a web hook to the specified channel

    Args:
        title (str): title of the webhook
        description (str): description of the webhook
        username (str, optional): username of the webhook. Defaults to "StealthyBotAlerts".
        url (str, optional): url of the webhook.
    """    
    data = {
    "content" : "",
    "username" : username
    }
    data["embeds"] = [
        {
            "description" : description,
            "title" : title
        }
    ]
    result = requests.post(url, json= data)