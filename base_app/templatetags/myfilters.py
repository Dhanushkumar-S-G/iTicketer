from django import template
from datetime import datetime


register = template.Library()


@register.filter(name="get_price")
def get_price(ticket_obj):
    last_date = datetime(2024, 1, 2).date()
    current_date = datetime.now().date()
    if current_date > last_date:
        return str(ticket_obj.bay) + " - " + str(ticket_obj.price + 50)
    else:
        return str(ticket_obj.bay) + " - " + str(ticket_obj.price)