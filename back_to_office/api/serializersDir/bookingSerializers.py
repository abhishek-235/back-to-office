from rest_framework import serializers
from backend.models import *


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        print("\n\n Booking Serializer called")
        model = Booking
        fields = ('id', 'location', 'seat_id', 'employee_id', 'booked_by', 'booked_for_date', 'booking_reference_number', 'lunch_type')

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(BookingSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)