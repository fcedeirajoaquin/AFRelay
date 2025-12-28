
def build_error_response(method: str, error_type: str, details: str) -> dict:
    return {
        "status" : "error",
        "error" : {
            "method" : method,
            "error_type" : error_type,
            "details" : details
        }
    }