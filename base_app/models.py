from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Transaction(models.Model):
    INITIATED = 0
    PAID = 1
    CANCELLED = 2
    FAILED = 3
    REFUND_INITIATED = 4
    REFUND_FINISHED = 5
    STATUS_CHOICES = ((INITIATED, "Initiated"), (PAID, "Paid"), (CANCELLED, "Cancelled"), (FAILED, "Failed"),
                      (REFUND_INITIATED, "Refund_initiated"), (REFUND_FINISHED, "Refund_finished"))
    txnid = models.CharField(max_length=30, null=True)
    payment_id = models.CharField(max_length=30, null=True)  # payuMoneyId
    mihpay_id = models.CharField(max_length=30, null=True)  # don't know the use
    payu_status = models.BooleanField(default=0)  # 0-failure, 1-success
    status = models.IntegerField(choices=STATUS_CHOICES, default=INITIATED)
    user = models.ForeignKey(User, related_name='related_paid', null=True, on_delete=models.SET_NULL, default=None)
    amount = models.IntegerField()
    name = models.CharField(max_length=255)  # product_info
    error_code = models.CharField(max_length=255, null=True)
    error_message = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    payment_mode = models.CharField(max_length=255, null=True)
    payment_added_on = models.DateTimeField(null=True)  # payment_done_in_payu
    pg_type = models.CharField(max_length=255, null=True)  # payment_type
    bank_refnum = models.CharField(max_length=255, null=True)  # bank_ref num
    refund_amount = models.IntegerField(default=0, null=True)
    additional_charges = models.FloatField(default=0, null=True)  # not yet used
    field9 = models.TextField(max_length=512, null=True)

    def update(self):
        self.updated_at = timezone.now()
        self.save()

    def __unicode__(self):
        return self.name
    
class Booking(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.user.first_name
class MaintenanceDataStore(models.Model):
    IS_ONLINE = 0
    IS_UNDER_MAINTENANCE = 1

    STATUS_CHOICES = ((IS_ONLINE, "ONLINE"), (IS_UNDER_MAINTENANCE, "MAINTENANCE"))
    status = models.PositiveSmallIntegerField(default=IS_ONLINE, choices=STATUS_CHOICES)

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=12)
    is_transport_needed = models.BooleanField(default=False,null=True,blank=True)
    paid = models.BooleanField(default=False,null=True,blank=True)
    jnm_id = models.CharField(max_length=10,null=True)