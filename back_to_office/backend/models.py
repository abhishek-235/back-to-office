from django.db import models

# Create your models here.
class Employee(models.Model):
    employee_id = models.CharField(max_length=20, default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, default=None)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Employees"
        db_table = "employees"

class Locations(models.Model):
    address = models.TextField()
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    longitude = models.CharField(max_length=250)
    latitutde = models.CharField(max_length=250)
    google_maps_link = models.URLField()
    primary_contact = models.CharField(max_length=250)
    secondary_contact = models.CharField(max_length=250, blank=True, null=True)
    
    def __str__(self):
        return str(f"{self.id} - {self.city.upper()}")

    class Meta:
        verbose_name_plural = "Locations"
        db_table = "locations"


class FloorPlan(models.Model):
    FLOOR_CHOICES = (
        ('', '---'),
        ('floor1','Floor 1'),
        ('floor2','Floor 2'),
        ('floor3','Floor 3'),
        ('floor4','Floor 4'),
        ('floor5','Floor 5'),
    )
    location = models.ForeignKey(Locations, on_delete=models.PROTECT)
    floor = models.CharField(choices=FLOOR_CHOICES, max_length=10)
    seat_number = models.CharField(max_length=250)    
    
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Floor Plan"
        db_table = "floor_plan"


class Booking(models.Model):
    location = models.ForeignKey(Locations, on_delete=models.PROTECT)
    seat_id = models.ForeignKey(FloorPlan, on_delete=models.PROTECT)
    employee_id = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='booked_for')
    booked_by = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='booking_by')
    booked_for_date = models.DateField(default=None)
    booking_reference_number = models.CharField(max_length=50)
    lunch_type = models.CharField(max_length=50, default=None, blank=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Bookings"
        db_table = "bookings"

