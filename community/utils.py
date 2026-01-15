# utils.py
from typing import Any
from pydantic import BaseModel
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

# 모든 응답의 표준 규격
class BaseResponse(BaseModel):
    message: str
    data: Any = None

class WrappedAPIRoute(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Any:
            result = await original_handler(request)
            
            # 이미 완벽한 응답(Response) 객체라면 그대로 내보냄 (쿠키 등 포함)
            if isinstance(result, Response):
                return result

            # [핵심] 아무 고민 없이 JSON으로 포장만 해서 보냄
            # status_code는 이미 요리사가 찍어둔 걸 FastAPI가 알아서 사용함
            return JSONResponse(content=result.model_dump())

        return custom_handler