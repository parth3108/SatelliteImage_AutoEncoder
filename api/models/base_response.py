from fastapi import Response
 
 
class BaseResponse:
 
    def __init__(self, is_success: bool, status_code: int, message: str, data=None):
        self.status_code = status_code
        self.is_success = is_success
        self.message = message
        self.data = data
 
    def to_dict(self):
        if self.data is None:
            return {
                "isSuccess": self.is_success,
                "statusCode": self.status_code,
                "message": self.message
            }
        else:
            return {
                "isSuccess": self.is_success,
                "statusCode": self.status_code,
                "message": self.message,
                "data": self.data
            }
 
    def respond(self, response: Response):
        response.status_code = self.status_code
        return self.to_dict()