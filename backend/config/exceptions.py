from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "code": "error",
            "message": "An error occurred.",
            "fields": {}
        }

        if isinstance(exc, ValidationError):
            error_payload["code"] = "validation_error"
            error_payload["message"] = "Validation failed for one or more fields."
            if isinstance(response.data, dict):
                error_payload["fields"] = response.data
                # Set a clearer message if detail or non_field_errors exist
                if "non_field_errors" in response.data:
                    error_payload["message"] = response.data["non_field_errors"][0]
                elif len(response.data) > 0:
                    first_key = list(response.data.keys())[0]
                    first_err = response.data[first_key]
                    if isinstance(first_err, list) and len(first_err) > 0:
                        error_payload["message"] = f"{first_key}: {first_err[0]}"
                    elif isinstance(first_err, str):
                        error_payload["message"] = f"{first_key}: {first_err}"
        elif hasattr(exc, 'detail'):
            if isinstance(exc.detail, str):
                error_payload["message"] = exc.detail
            elif isinstance(exc.detail, dict):
                error_payload["fields"] = exc.detail
                error_payload["message"] = exc.detail.get("detail", "An error occurred.")
            error_payload["code"] = getattr(exc, 'default_code', 'error')

        response.data = {"error": error_payload}

    return response
