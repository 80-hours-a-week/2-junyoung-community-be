# utils.py
import json
from typing import Callable, Any
from fastapi.routing import APIRoute
from fastapi import Request, Response
from fastapi.responses import JSONResponse

SUCCESS_MESSAGES = {
    "/api/v1/auth/signup": "REGISTER_SUCCESS",
    "/api/v1/auth/login": "LOGIN_SUCCESS",
    "/api/v1/posts": "POST_RETRIEVAL_SUCCESS",
}

class WrappedAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Any:
            data = await original_handler(request)
            
            # 에러 응답은 건드리지 않고 통과시킵니다.
            if isinstance(data, Response) and data.status_code >= 400:
                return data

            # 1. 데이터 본체 추출
            if isinstance(data, Response):
                try:
                    # 기존 응답 바디를 읽어옵니다.
                    body = json.loads(data.body.decode())
                except:
                    body = None
                status_code = data.status_code
                headers = dict(data.headers)
            else:
                body = data
                status_code = 200
                headers = {}

            # 2. 메시지 결정
            message = SUCCESS_MESSAGES.get(request.url.path, "SUCCESS")

            # 3. 새로운 JSONResponse 생성 (Content-Length 문제를 원천 차단)
            # headers에서 content-length를 삭제하여 자동 재계산되게 합니다.
            headers.pop("content-length", None) 
            
            return JSONResponse(
                content={"message": message, "data": body},
                status_code=status_code,
                headers=headers
            )

        return custom_handler