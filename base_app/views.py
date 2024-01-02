from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from .models import *
from django.conf import settings
from hashlib import sha512
from django.urls import reverse
from django.utils import timezone
from uuid import uuid1
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse

# Create your views here.
def index(request):
    return render(request,'base_app/index.html')

@login_required
def dashboard(request):
    context = {}
    try:
        usr = request.user
        try:
            context['booking'] = Booking.objects.get(user=usr)
            context['request'] = request
            
        except Exception as e:
            context['booking'] = None
        return render(request,'base_app/dashboard.html',context)
    except Exception as e:
        print(e)
        return redirect('/login')

KEYS = ('txnid', 'amount', 'productinfo', 'firstname', 'email',
        'udf1', 'udf2', 'udf3', 'udf4', 'udf5', 'udf6', 'udf7', 'udf8',
        'udf9', 'udf10')

def generate_hash(data):
    hash_value = sha512(str(settings.PAYU_INFO.get('merchant_key')).encode('utf-8'))
    # hash_value = sha512(str(getattr(settings, 'PAYU_MERCHANT_KEY', None)).encode('utf-8'))
    print(hash_value)
    for key in KEYS:
        # enc_value = data.get(key)
        # print(enc_value)
        # print(type(enc_value))
        # a = "|"
        hash_value.update(str("%s%s" % ('|', data.get(key, ''))).encode('utf-8'))

    hash_value.update(str("%s%s" % ('|', settings.PAYU_INFO.get('merchant_salt'))).encode('utf-8'))

    return hash_value.hexdigest().lower()

def key_collect(request):
    data = {'key': request.POST.get('key'), 'txnid': request.POST.get('txnid'), 'amount': request.POST.get('amount'),
            'productinfo': request.POST.get('productinfo'), 'firstname': request.POST.get('firstname'),
            'email': request.POST.get('email'), 'hash': request.POST.get('hash'), 'status': request.POST.get('status')}
    try:
        data.update({'additionalCharges': request.POST.get('additionalCharges')})
    except:
        pass
    return data

def verify_hash(data):
    Reversedkeys = reversed(KEYS)
    if data.get('additionalCharges'):
        # if the additionalCharges parameter is posted in the transaction response,then hash formula is:
        # sha512(additionalCharges|SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key)

        hash_value = sha512(data.get('additionalCharges').encode('utf-8'))
        hash_value.update(("%s%s" % ('|', settings.PAYU_INFO.get('merchant_salt'))).encode('utf-8'))
    else:
        # If additionalCharges parameter is not posted in the transaction response, then hash formula is the generic reverse hash formula
        # sha512(SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key)

        hash_value = sha512(settings.PAYU_INFO.get('merchant_salt').encode('utf-8'))

    hash_value.update(("%s%s" % ('|', str(data.get('status', '')))).encode('utf-8'))

    for key in Reversedkeys:
        hash_value.update(("%s%s" % ('|', str(data.get(key, '')))).encode('utf-8'))

    hash_value.update(("%s%s" % ('|', settings.PAYU_INFO.get('merchant_key'))).encode('utf-8'))

    return hash_value.hexdigest().lower() == data.get('hash')

@login_required
def pay_show(request):
    try:
        usr = request.user
        isBooking = Booking.objects.filter(user=usr).exists()
        if isBooking:
            messages.success(request, 'You have already booked a show')
            return redirect('/dashboard')
        else:
            if request.method == "POST" or "GET":
                usr = request.user    
                firstname = usr.username
                title = "JANANAM 2023"
                amount = settings.GENERAL_ENTRANCE_FEE
                email = usr.email
                mkey = settings.PAYU_INFO['merchant_key']
                surl = request.build_absolute_uri(reverse('succ_pay'))
                curl = request.build_absolute_uri(reverse('cancel'))
                furl = request.build_absolute_uri(reverse('failure'))
                txnid = str(uuid1().int >> 64)  # converted to 20 digits uuid
                # sha512(key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||salt)
                data = dict(key=mkey, txnid=txnid, amount=amount, productinfo=title, firstname=firstname, email=email)
                hash = generate_hash(data)
                data.update({'hash': hash, 'surl': surl, 'curl': curl, 'furl': furl})
                Transaction.objects.create(txnid=txnid, status=Transaction.INITIATED, user=usr,
                                        amount=amount,
                                        name=title)
                return render(request, 'base_app/pay_redirect.html', {'form': data})
            else:
                raise SuspiciousOperation("Invalid request")
    except Exception as e:
        print(e)
        return redirect('/dashboard')

@csrf_exempt
def failure(request):
    print('.................................payment failed......................................................')
    if request.method == "POST":
        data = key_collect(request)
        if verify_hash(data):
            trns = Transaction.objects.get(txnid=data['txnid'])
            trns.payment_id = request.POST.get('payuMoneyId')
            trns.payu_status = (request.POST.get('status') == 'success')  # Boolean
            trns.status = Transaction.CANCELLED
            trns.error_code = request.POST.get('error')  # should return no_error e000
            trns.error_message = request.POST.get('error_Message')
            trns.bank_refnum = request.POST.get('bank_ref_num')
            trns.mihpay_id = request.POST.get('mihpayid')
            trns.payment_added_on = request.POST.get('addedon')
            trns.pg_type = request.POST.get('PG_TYPE')
            trns.payment_mode = request.POST.get('mode')
            trns.additional_charges = data.get("additionalCharges", 0)
            trns.field9 = request.POST.get('field9')
            trns.update()
            trns.save()
            messages.error(request, 'Payment Failed.Please try again later')
            
            # payment_check_txnid.delay(data['txnid'])

            return redirect('/dashboard')
        else:
            print("data has been tampered ", data)
    else:
        raise SuspiciousOperation("Invalid access")


@csrf_exempt
def succ_pay(request):
    if request.method == "POST":
        data = key_collect(request)
        if verify_hash(data):
            trns = Transaction.objects.get(txnid=data['txnid'])
            trns.payment_id = request.POST.get('payuMoneyId')
            trns.payu_status = (request.POST.get('status') == 'success')  # Boolean
            trns.status = Transaction.PAID
            trns.error_code = request.POST.get('error')  # should return no_error e000
            trns.error_message = request.POST.get('error_Message')
            trns.bank_refnum = request.POST.get('bank_ref_num')
            trns.mihpay_id = request.POST.get('mihpayid')
            trns.payment_added_on = request.POST.get('addedon')
            trns.pg_type = request.POST.get('PG_TYPE')
            trns.payment_mode = request.POST.get('mode')
            trns.update()
            trns.additional_charges = data.get("additionalCharges", 0)
            trns.field9 = request.POST.get('field9')
            trns.save()
            booking = Booking.objects.create(user=trns.user, transaction=trns)
            booking.save()
            messages.success(request, 'Payment Cancelled Successfully!')
            return redirect('/dashboard')
        else:
            print('Date tampered')
    else:
        raise SuspiciousOperation("Invalid access")


@csrf_exempt
def cancel(request):
    if request.method == "POST":
        print('.................................payment Canceled......................................................')
        data = key_collect(request)
        if verify_hash(data):
            trns = Transaction.objects.get(txnid=data['txnid'])
            trns.payment_id = request.POST.get('payuMoneyId')
            trns.payu_status = (request.POST.get('status') == 'success')  # Boolean
            trns.status = Transaction.CANCELLED
            trns.error_code = request.POST.get('error')  # should return no_error e000
            trns.error_message = request.POST.get('error_Message')
            trns.bank_refnum = request.POST.get('bank_ref_num')
            trns.mihpay_id = request.POST.get('mihpayid')
            trns.payment_added_on = request.POST.get('addedon')
            trns.pg_type = request.POST.get('PG_TYPE')
            trns.payment_mode = request.POST.get('mode')
            trns.additional_charges = data.get("additionalCharges", 0)
            trns.field9 = request.POST.get('field9')
            trns.update()
            trns.save()
            # payment_check_txnid.delay(data['txnid'])
            messages.error(request, 'Payment Cancelled Successfully!')
            return redirect('/dashboard')
        else:
            print("data has been tampered ", data)
    else:
        raise SuspiciousOperation("Invalid access")


def logout_user(request):
    logout(request)
    return redirect("/")

@api_view(['GET'])
def check_profile(request,id):
    user = User.objects.get(id=id)
    try:
        prf = Profile.objects.get(user=user)
        if prf:
            return JsonResponse({'status':True,'message':'Profile is complete','data':True})
        else:
            return JsonResponse({'status':False,'message':'Profile is not complete','data':False})
    except Exception as e:
        return JsonResponse({'status':False,'message':'Profile is not complete','error':str(e)})
    return JsonResponse({'status':False,'message':'Profile is not complete','error':str(e)})
    
@api_view(['POST'])
def create_profile(request):
    if request.method == 'POST':
        print(request.POST)
        try:
            print('hii')
            phone_number = request.POST.get('phone_number')
            is_transport = request.POST.get('is_transport')
            user = request.user
            
            user_id = user.id
            
            id = f'JNM{user_id:03d}'
           
            if is_transport == 'on':
                is_transport = True
            else:
                is_transport = False
            Profile.objects.create(user=user,phone=phone_number,is_transport_needed=is_transport,jnm_id=id)            
            return redirect('dashboard')
        except Exception as e:
            print(str(e))
            return redirect('dashboard')