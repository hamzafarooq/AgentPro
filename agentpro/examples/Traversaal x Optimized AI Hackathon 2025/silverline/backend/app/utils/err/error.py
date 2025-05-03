# app\utils\err\error.py

from fastapi import HTTPException
from app.utils.base_schema.base_schema import BaseResponse

class InternalServerError(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail=BaseResponse(resp_code=500, responseDescription="Internal Server Error"))
