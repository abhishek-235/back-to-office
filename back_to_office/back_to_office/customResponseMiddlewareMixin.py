import json

from django.utils.deprecation import MiddlewareMixin

# from django.conf import settings

# import the logging library
import logging

# Get an instance of a logger
log = logging.getLogger("django")
log_info = logging.getLogger("django_info")
log_debug = logging.getLogger("django_debug")
import json


class MyMiddlewareClass(MiddlewareMixin):
    def process_request(self, request):
        # Process the request

        # log request
        try:
            request_body = json.loads(request.body)
        except:
            request_body = request.body
        request_data = {}
        request_data['header'] = request.headers
        request_data['data'] = request_body
        request_data['scheme'] = request.scheme
        request_data['path'] = request.path
        request_data['query_string'] = request.GET
        request_data['post_data'] = request.POST
        
        log_info.info("\n" + "*"* 100 + "\n")
        log_info.info("Log request: " + str(request_data))
        pass

    def process_response(self, request, response):
        requestedFormat = request.GET.get('format')
        # modify the response if the requested url is an API url
        if 'api' in request.path and requestedFormat == 'json':
            customResponse = {}
            responseData = json.loads(response.content.decode('utf-8'))
            if 'data' in responseData:
                customResponse = json.loads(response.content.decode('utf-8'))
            else:
                customResponse['data'] = []
            customResponse['status_code'] = responseData.get('status_code', 200)
            customResponse['status'] = responseData.get('status', True)
            customResponse['message'] = responseData.get('message', '')
            customResponse['dev_message'] = responseData.get('dev_message', [])

            if 'errors' in responseData:
                customResponse['errors'] = responseData.get('errors')

            # log response
            log_info.info("\n")
            if customResponse['status'] == False:
                customResponse['status_code'] = 300
                log_info.info("Log response: " + str(customResponse))                
            else:
                #log_info.info("Log response: " + str(customResponse))
                if 'final-submit' in request.path:
                    log_info.info("\n")
                    log_info.info("Log response: " + str(customResponse))

            response.content = json.dumps(customResponse).encode('utf-8')
        return response
