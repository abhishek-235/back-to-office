from django.contrib import admin

# Register your models here.
from backend.models import *
from django.utils.html import format_html

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ['first_name', 'last_name', 'employee_id']
    ordering = ('id',)

    def get_list_display(self, obj):
        return self.list_display

    list_display = ('id', 'first_name', 'last_name', 'employee_id', 'view_bookings')
    

    def view_bookings(self, object):
        return format_html(
            '<a href="/admin/backend/booking/?booked_by__id={0}">View</a>'.format(object.id))

    class Meta:
        model = Employee


@admin.register(Locations)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ['id', 'city', 'state']
    ordering = ('id',)
    
    class Meta:
        model = Locations

@admin.register(FloorPlan)
class FloorPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'floor', 'seat_number']
    ordering = ('id',)
    list_per_page = 20
    list_filter = ['location', ]
    
    class Meta:
        model = FloorPlan


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'seat_no', 'employee', 'booked_for_date', 'booking_reference_number', 'lunch_type']
    ordering = ('id',)
    list_per_page = 20

    def seat_no(self, obj):
        return obj.seat_id.seat_number

    def employee(self, obj):
        return obj.employee_id.employee_id
    
    class Meta:
        model = Booking
