from django.contrib import admin
from core.models import User, Item, OrderItem, Order, BillingAddress
from django.contrib.sessions.models import Session
import pprint

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return pprint.pformat(obj.get_decoded()).replace('\n', '<br>\n')
    _session_data.allow_tags=True
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['session_data']
    exclude = ['session_data']
    date_hierarchy = 'expire_date'


# Register your models here.
admin.site.register(User)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(BillingAddress)
admin.site.register(Session, SessionAdmin)