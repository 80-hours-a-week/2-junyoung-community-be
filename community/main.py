# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes.post_route import router as post_router
from routes.auth_route import router as auth_router
from utils import WrappedAPIRoute

app = FastAPI()

# 공통 예외 처리기는 이미 작성된 것을 그대로 사용합니다.
# 그러면 400, 409 에러도 자동으로 {"message": "...", "data": null} 형식이 됩니다.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "data": None}
    )

app.include_router(post_router)
app.include_router(auth_router)