from celery import shared_task
from django.conf import settings
import requests



@shared_task()
def send_whatsapp_msg(to,msg):

    url = f"{settings.WHATSAPP_API_IP}/message/text?key={settings.WHATSAPP_INSTANCE_KEY}"
    to = f"+91{to}"
    print(type(to))
    to = int(to)
    payload = f'id={to}&message={msg}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload,timeout=10)
        print(response.text)
    except requests.exceptions.Timeout:
        print("Timeout for the student ",to)
    except Exception as e:
        print(e)
    return