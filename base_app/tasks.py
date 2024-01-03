from celery import shared_task 
from django.conf import settings
import requests
from celery import shared_task
from base_app.models import CheckStatusLog, Transaction



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

Webservicekeys = ("key", "command", "var1")

def get_webservice_hash(data):
    from hashlib import sha512
    hash_value = sha512(''.encode("utf-8"))
    for key in Webservicekeys:
        hash_value.update(("%s%s" % (str(data.get(key, '')), '|')).encode("utf-8"))
    hash_value.update(("Z8llz8rm").encode("utf-8"))
    return hash_value.hexdigest().lower()


def post(params):
    import urllib.request
    try:
        from urllib import urlencode
    except ImportError:
        from urllib.parse import urlencode
    import json

    params = params
    params['key'] = "QlHn7C"

    params['hash'] = get_webservice_hash(params)

    url = 'https://info.payu.in/merchant/postservice.php?form=2'
    payload = urlencode(params)

    request = urllib.request.Request(url, payload.encode('utf-8'))
    # request.data=payload
    response = (urllib.request.urlopen(request))

    return json.loads(response.read())

@shared_task()
def payment_check_txnid(transaction_id):
    from django.conf import settings
    from sentry_sdk import capture_exception
    from django.utils import timezone

    failed_transaction = Transaction.objects.get(txnid=transaction_id)
    try:
        trns_id = failed_transaction.id
        trn = failed_transaction
        mkey = settings.PAYU_INFO['merchant_key']
        data = dict(key=mkey, command="verify_payment", var1=trns_id)
        response = post(data)
        if int(response['status']) == 1:
            x = response["transaction_details"]
        postBackParam = x[list(x.keys())[0]]
        status = (postBackParam['status'] == 'success')
        if status:
            try:
                trn.payment_id = postBackParam['mihpayid']
                trn.payu_status = (postBackParam['status'] == 'success')  # Boolean
                trn.status = Transaction.PAID
                trn.error_code = postBackParam['error_code']  # should return no_error e000
                trn.error_message = postBackParam['error_Message']
                trn.bank_refnum = postBackParam['bank_ref_num']
                trn.mihpay_id = postBackParam['mihpayid']
                trn.payment_added_on = postBackParam['addedon']
                trn.pg_type = postBackParam['PG_TYPE']
                trn.payment_mode = postBackParam['mode']
                trn.update()
                trn.field9 = postBackParam['field9']
                trn.save()
                CheckStatusLog.objects.create(transaction=trn, changed_at=timezone.now(), is_changed=True)
                print(trn.user.user_info_object.admission_number)
            except Exception as E:
                capture_exception(E)
                print(E)
    except Exception as e:
        print(e)
        capture_exception(e)
    print('Finished...')