# Response Class
from django.http import JsonResponse


class NetworkResponse:
    def __init__(self, message_code, message, data=None, token=None):
        self.message_code = message_code
        self.message = message
        self.data = data
        self.token = token

    # Response to JSON
    def to_json(self):
        json = {
            'status': self.message_code,
            'message': self.message,
        }
        if self.token:
            json['token'] = self.token

        json['data'] = self.data

        return json

    # Method to get the response
    @staticmethod
    def get_json_response(status, message_code, message, data=None, token=None):
        return JsonResponse(NetworkResponse(message_code=message_code, message=message, data=data, token=token).to_json(),
                            status=status, safe=False)
