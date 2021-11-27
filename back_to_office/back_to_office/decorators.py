from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from back_to_office.jwtlib import decryptToken
from backend.models import Employee

def authenticateRequest(request=None):
    if request:
        # get token from header
        headerData = request.headers
        encryptToken = headerData.get('Authorization', None)

        # decrypt token
        decryptData = decryptToken(encryptToken)

        if not decryptData:
            resList = {}
            resList['data'] = []
            resList['status'] = False
            resList['status_code'] = status.HTTP_400_BAD_REQUEST
            resList['message'] = "Invalid Request"
            resList['dev_message'] = ["can not decrypt Data. Check whether token is passed in header."]
            return resList
            
        decoded_token = decryptData['claims']
        if decryptData['status']==True:
            employee_id = decoded_token.get('employee_id', None)
            
            user_details = Employee.objects.filter(id=employee_id).first()
            if user_details:
                return {
                    "status": True,
                    "employee_id": employee_id
                }
            else:
                return {'data': [],
                'status': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': "Invalid User",
                'dev_message': ["Either user is not registered or account is not verified."]
            }
        else:
            return {'data': [],
                'status': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': decoded_token.get('message', "Invalid Request"),
                'dev_message': decoded_token.get('message', ["can not decrypt Data. Check whether token is passed in header."])
            }
    else:
        return {'data': [],
            'status': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': "Invalid Request",
            'dev_message': ["request can not be null"]
        }


def authenticatedRequest(function):
   
    def wrap(request, *args, **kwargs):
        authResponse = authenticateRequest(request)
        if 'status' in authResponse and authResponse['status']:
            employee_id = authResponse['employee_id']
            
            #add data to kwargs to return in view, can access data in view from kwargs
            context = {'employee_id': employee_id}
            kwargs.update(context)
            return function(request, *args, **kwargs)
        else:
            resList = {'data': '',
                'status': False,
                'status_code': status.HTTP_401_UNAUTHORIZED,
                'message': authResponse['message'] if 'message' in authResponse else "Invalid Request",
                'dev_message': authResponse['dev_message'] if 'dev_message' in authResponse else []
            }

            response = Response(
                resList,
                content_type="application/json",
                status=status.HTTP_401_UNAUTHORIZED,
            )
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}

            return response
    return wrap

    
