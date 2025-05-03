# app\utils\base_schema\base_schema.py

from pydantic import BaseModel


class BaseResponse(BaseModel):
    resp_code: int
    responseDescription: str


# Global response definitions
GLOBAL_RESPONSES = {
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": BaseResponse(resp_code=422, responseDescription="Field 'name' - This field is required").model_dump()
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": BaseResponse(resp_code=500, responseDescription="Internal Server Error").model_dump()
            }
        },
    },
}