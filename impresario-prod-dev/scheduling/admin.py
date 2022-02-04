from django.contrib import admin
from .models import Organization, Groups, Membershiplevel, Teamrequest, Event
# Register your models here.
admin.site.register(Organization)
admin.site.register(Groups)
admin.site.register(Membershiplevel)
admin.site.register(Teamrequest)
admin.site.register(Event)
