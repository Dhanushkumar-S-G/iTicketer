from django.db import models

# Create your models here.

class MaintenanceDataStore(models.Model):
    IS_ONLINE = 0
    IS_UNDER_MAINTENANCE = 1

    STATUS_CHOICES = ((IS_ONLINE, "ONLINE"), (IS_UNDER_MAINTENANCE, "MAINTENANCE"))
    status = models.PositiveSmallIntegerField(default=IS_ONLINE, choices=STATUS_CHOICES)