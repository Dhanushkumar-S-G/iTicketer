from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from sentry_sdk import capture_exception
from .models import *

from base_app.tasks import payment_check_txnid, send_whatsapp_msg
from .models import Booking,Transaction
from django.conf import settings
from hashlib import sha512
from django.urls import reverse
from django.utils import timezone
from uuid import uuid1
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse

# Create your views here.
def index(request):
    context = {}
    last_date = datetime(2024, 1, 4).date()
    current_date = datetime.now().date()
    no_of_bookings = Booking.objects.all().count()
    if current_date > last_date or no_of_bookings >= settings.MAX_BOOKINGS :
        messages.warning(request,"Payment has been closed")
        is_payment_enabled = False
        print("payment enabled")
        return redirect('/dashboard')
    else:
        is_payment_enabled = True
        if current_date < last_date:
            amount = 150
        else:
            amount = 250
    
        # context['booking'] = None
        context['amount'] = amount
    return render(request,'base_app/index.html',context)

@login_required()
def dashboard(request):
    context = {}
    try:
        
        BASE_URL = settings.BASE_URL
        print(BASE_URL)
        usr = request.user
        context['base_url'] = BASE_URL
        try:
            context['booking'] = Booking.objects.get(user=usr)
            context['request'] = request
            
            profile = Profile.objects.get(user=usr)
            context['jnm_id'] = profile.jnm_id
        except Exception as e:
            last_date = datetime(2024, 1, 4).date()
            current_date = datetime.now().date()
            total_bookings = Booking.objects.all().count()
            # seated_bookings = Profile.objects.filter(paid=True,bay = Profile.SEATED).count()
            # first_bay_bookings = Profile.objects.filter(paid=True,bay = Profile.FIRST_BAY).count()
            # second_bay_bookings = Profile.objects.filter(paid=True,bay = Profile.SECOND_BAY).count()

            if total_bookings >= settings.MAX_BOOKINGS :
                messages.warning(request,"Payment has been closed")
                is_payment_enabled = False
                print("payment enabled")
                return redirect('/dashboard')
            
            # if seated_bookings >= settings.SEATED_MAX_BOOKINGS:
            #     is_seated_available = False
            # else:
            #     is_seated_available = True 
            
            # if first_bay_bookings >= settings.FIRST_BAY_MAX_BOOKINGS:
            #     is_first_bay_available = False
            # else:
            #     is_first_bay_available = True

            # if second_bay_bookings >= settings.SECOND_BAY_MAX_BOOKINGS:
            #     second_bay_bookings = False
            # else: 
            #     second_bay_bookings = True


            is_payment_enabled = True
            if current_date < last_date:
                amount = 150
            else:
                amount = 250
            
            context = {
                'booking' : None,
                'enabled' : is_payment_enabled,
                'amount'  : amount,
                
            }
            context['tickets'] = Tickets.objects.filter(is_filled=False)

        return render(request,'base_app/dashboard.html',context)
    except Exception as e:
        print(e)
        return redirect('/')

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

@login_required()
def pay_show(request):
    try:
            # payment_enable,amount = is_payment_enable(request)
            # print(is_payment_enable())
            last_date = datetime(2024, 1, 4).date()
            current_date = datetime.now().date()
            no_of_bookings = Booking.objects.all().count()
            usr = request.user
            if current_date > last_date or no_of_bookings >= settings.MAX_BOOKINGS :
                messages.warning(request,"Payment has been closed")
                is_payment_enabled = False
                print("payment enabled")
                return redirect('/dashboard')
            else:
                is_payment_enabled = True
                if current_date < last_date:
                    amount = 150
                else:
                    amount = 250
                    usr = request.user
            # amount = 1
            isBooking = Booking.objects.filter(user=usr).exists()
            if isBooking:
                messages.success(request, 'You have already booked a show')
                return redirect('/dashboard')
            
            else:

                if request.method == "POST" or "GET":
                    if 'ticket' in request.POST:
                        ticket_id = request.POST.get('ticket')
                        ticket = Tickets.objects.get(id=ticket_id)
                        amount = ticket.price    
                    usr = request.user    
                    firstname = usr.username
                    title = "JANANAM 2023"
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
                    return render(request, 'base_app/pay_redirect.html', {'form': data,'amount':amount,'enabled':is_payment_enabled})
                else:
                    raise SuspiciousOperation("Invalid request")
    except Exception as e:
        print(e)
        capture_exception(e)
        return redirect('/dashboard')

@csrf_exempt
def failure(request):
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
            
            payment_check_txnid.delay(data['txnid'])

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
            profile = Profile.objects.get(user=trns.user)
            profile.paid = True
            profile.save()
            messages.success(request, 'Payment Successfull!')
            profile = Profile.objects.get(user=trns.user)
            message = "Your Ticket has been Booked"
            send_whatsapp_msg.delay(to=profile.phone,msg=settings.MESSAGE_TEMPLATE)
            send_whatsapp_msg.delay(to=profile.phone,msg=f"Your Payment has been sucessfull - JANANAM \n\n Your JANANAM ID is {profile.jnm_id}")
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
            payment_check_txnid.delay(data['txnid'])
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
            gender = request.POST.get('gender')
            user = request.user
            
            user_id = user.id
            
            id = f'JNM{user_id:03d}'
           
            if is_transport == 'on':
                is_transport = True
            else:
                is_transport = False
            Profile.objects.create(user=user,phone=phone_number,is_transport_needed=is_transport,jnm_id=id,gender=gender)            
            messages.success(request,'Profile Created Successfully')
            return redirect('dashboard')
        except Exception as e:
            print(str(e))
            capture_exception(e)
            messages.error(request,'Profile Creation Failed')
            return redirect('dashboard')
        
def admin_dashboard(request):
    context = {}
    context['bookings'] = Booking.objects.all()
    return render(request,'base_app/admin_dashboard.html',context)