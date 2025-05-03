# app\middleware\middleware_handler.py

import time
from fastapi import FastAPI, Request
from app.utils.logging.logger import LOG
from app.middleware.usage import usage_middleware


def register_middleware_handler(app: FastAPI):
    
    @app.middleware("http")
    async def middleware_handler(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        
        # api_type = request.scope.get("type", "Unknown")
        route = request.scope.get("path", "Unknown")
        http_method = request.method

        response = await usage_middleware(response=response)

        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        LOG.info(f"- {http_method} \"{route}\" Time Taken: {process_time:.2f} s 🚀")
        
        return response