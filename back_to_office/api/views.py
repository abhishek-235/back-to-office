# import all models from admin app
from backend.models import *
from django.db.models import Count

from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView

import logging

log = logging.getLogger("django")

from django.http import Http404
import json
from django.http.response import JsonResponse

# import JWT token
from back_to_office.jwtlib import createSignedToken, decryptToken

from django.utils.decorators import method_decorator
from back_to_office.decorators import authenticatedRequest, authenticateRequest
from api.serializersDir.locationSerializers import LocationSerializer
from api.serializersDir.bookingSerializers import BookingSerializer

import uuid
from datetime import datetime
from django.db import IntegrityError, transaction

@method_decorator(authenticatedRequest, name='dispatch')
class AvailableSeats(APIView):
    """
    List all available seats.
    """

    def get(self, request, *args, **kwargs):

        request_date = request.GET.get('date')
        location = request.GET.get('location')
        
        seats = available_seats(date=request_date, location=location, floor=None)
        
        return_dataset = {"data": seats}
        if not seats:
            return_dataset['message'] = "No seats are available."
            return_dataset['dev_message'] = ["No floor plan is available for this date and location."]

        return Response(return_dataset)

def available_seats(date, location, floor=None):
    """
    List available.
    """

    all_seats = FloorPlan.objects.filter(location=location).all()
    booked_seats = Booking.objects.filter(location=location,booked_for_date=date).all()
    
    floor_wise_seats = {}
    for floor_data in all_seats:
        try:
            floor_wise_seats[floor_data.floor]['total_seats'] += 1
            floor_wise_seats[floor_data.floor]['seats'].append(floor_data)
        except Exception:
            floor_wise_seats[floor_data.floor] = {
                                
                                                    'total_seats': 1,
                                                    'seats': [floor_data]
                                       
            }

    floor_wise_booked_seats = {}
    for floor_data in booked_seats:
        try:
            floor_wise_booked_seats[floor_data.seat_id.floor]['total_seats'] += 1
            floor_wise_booked_seats[floor_data.seat_id.floor]['seats'].append(floor_data.seat_id)
        except Exception:
            floor_wise_booked_seats[floor_data.seat_id.floor] = {
                                
                                                    'total_seats': 1,
                                                    'seats': [floor_data.seat_id]
            }

    available_seats = {}
    for floor_no, floor_seats in floor_wise_seats.items():
        if floor_no not in floor_wise_booked_seats.keys():
            available_seats[floor_no] = floor_seats
        else:
            total_available_seats = floor_wise_seats[floor_no]['total_seats'] - floor_wise_booked_seats[floor_no]['total_seats']
            obj_available_seats = set(floor_wise_seats[floor_no]['seats']) - set(floor_wise_booked_seats[floor_no]['seats'])
            available_seats[floor_no] = {
                'total_seats': total_available_seats,
                'seats': list(obj_available_seats)
            }

    if floor is None:
        return {floor_no:seats['total_seats'] for floor_no, seats in available_seats.items()}
    else:
        return available_seats[floor]


class Login(APIView):
    """
    Login.
    """

    def post(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get('employee_id', None)
            if not employee_id:
                responseData = {'message': 'Invalid employee id', 'status': False,
                            'status_code': status.HTTP_300_MULTIPLE_CHOICES, 'errors': ["Employee Id is required."]}
                return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)
            
            try:
                employee_details = Employee.objects.get(employee_id=employee_id)
                userPayload = {
                    "employee_id": employee_details.id,
                }
                encryptedToken = createSignedToken(payload=userPayload)
                return JsonResponse({"data": encryptedToken, "message": "login success."})
            except Exception as e:
                responseData = {'message': 'Invalid employee id', 'status': False, 'errors': [str(e)],
                            'status_code': status.HTTP_300_MULTIPLE_CHOICES}
                return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)
        except Exception as e:
            log.error("Exception in Login:" + str(e))
            responseData = {'message': str(e), 'status': False}
            return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)


@method_decorator(authenticatedRequest, name='dispatch')
class Location(APIView):
    """
    List all locations.
    """

    def get(self, request, *args, **kwargs):
        queryset = Locations.objects.all()

        resultSet = LocationSerializer(queryset, fields=['id', 'city'], many=True)
        return Response({'data':resultSet.data})


@method_decorator(authenticatedRequest, name='dispatch')
class SeatBooking(APIView):
    """
    Seat Booking.
    """

    def post(self, request, *args, **kwargs):
        try:
            login_employee_id = kwargs.get('employee_id', None)

            booked_seat_no = {}
            errors = []
            with transaction.atomic():
                for request_data in request.data:
                    location = request_data.get('location', None)
                    floor = request_data.get('floor', None)
                    date = request_data.get('date', None)
                    employee_details = request_data.get('employee_details')
                    booked_by = login_employee_id
                    number_of_seats_to_book = request_data.get('number_of_seats', 0)
                    

                    # check availability
                    available_seat_details = available_seats(date=date, location=location, floor=floor)
                    if available_seat_details['total_seats'] >= number_of_seats_to_book:
                        booking_reference_number = str(uuid.uuid4())[:8]
                        for i in range(number_of_seats_to_book):
                            seat_obj = available_seat_details['seats'][i]

                            employee_id = employee_details[i].get('employee_id', None)
                            lunch_type = employee_details[i].get('lunch_type', None)

                            try:
                                employee_instance = Employee.objects.get(employee_id=employee_id)
                            except Exception as e:
                                errors.append(f"No employee found with employee_id {employee_id}.")
                                raise IntegrityError
                                
                            booking_data = {
                                'location': location,
                                'seat_id': seat_obj.id,
                                'employee_id': employee_instance.id,
                                'booked_by': booked_by,
                                'booked_for_date': date,
                                'booking_reference_number': booking_reference_number,
                                'lunch_type': lunch_type
                            }

                            serializer = BookingSerializer(data=booking_data)
                            if serializer.is_valid():
                                serializer.save()
                                try:
                                    if location in booked_seat_no[date].keys():
                                        booked_seat_no[date][location].append(seat_obj.seat_number)
                                    else:
                                        booked_seat_no[date].update({
                                                            location: [seat_obj.seat_number]
                                    })
                                except:
                                    booked_seat_no[date] = {location: [seat_obj.seat_number]}

                            else:
                                responseData = {'message': serializer.errors, 'status': False,
                                    'status_code': status.HTTP_300_MULTIPLE_CHOICES}
                                return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)
                    else:
                        location_instance = Locations.objects.get(id=location)
                        errors.append(f"No seats are available for {date} on {location_instance.city} location.")

                if errors:
                    raise IntegrityError

                return JsonResponse({"data": booked_seat_no, "message": "Your desk has been reserved."})

        except IntegrityError:
            responseData = {'message': "Please check errors.", 'status': False, "errors": errors}
            return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)
        except Exception as e:
            log.error("Exception in Booking:" + str(e))
            responseData = {'message': str(e), 'status': False}
            return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)

    def get(self, request, *args, **kwargs):
        try:
            employee_id = kwargs.get('employee_id', None)
            bookings = Booking.objects.filter(employee_id=employee_id).all()
        except Exception as e:
            log.error("Exception in Login:" + str(e))
            responseData = {'message': str(e), 'status': False}
            return Response(responseData, status=status.HTTP_300_MULTIPLE_CHOICES)