from rest_framework import serializers
from backend.models import *


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        print("\n\n Location Serializer called")
        model = Locations
        fields = ('id', 'city', 'state', 'address', 'primary_contact')

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(LocationSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
