from rest_framework import status
from rest_framework.decorators import api_view

from common.response import NetworkResponse
from utils.models import SupportingInformation


# ----------------------------@amit--------------------------------
# View to get all supporting information
@api_view(['GET'])
def get_all_supporting_information(request):
    try:
        # Get all supporting information
        supporting_information = SupportingInformation.objects.all()

        supporting_information = [supporting_information1 for supporting_information1 in supporting_information]

        # Create a list of dicts
        supporting_information_list = []
        for supporting_information_obj in supporting_information:
            supporting_information_list.append(supporting_information_obj.as_dict)

        # Return the list of dicts
        return NetworkResponse.get_json_response(
            message_code="SUCCESS",
            message="Successfully fetched all supporting information",
            data=supporting_information_list,
            status=status.HTTP_200_OK
        )

    # If any error occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
