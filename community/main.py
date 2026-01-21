# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from routes.post_route import router as post_router
from routes.auth_route import router as auth_router
from routes.comment_route import router as comment_router
from routes.like_route import router as like_router
from routes.user_route import router as user_router
from slowapi.errors import RateLimitExceeded
from utils import limiter

app = FastAPI()


# Rate Limiter
app.state.limiter = limiter
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    도배(Limit)가 걸렸을 때 실행되는 함수입니다.
    라이브러리 기본 메시지 대신, 해당 웹만의 포맷으로 429를 리턴합니다.
    """
    return JSONResponse(
        status_code=429, # Too Many Requests
        content={"message": "TOO_MANY_REQUESTS", "data": None}
    )

app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"message": "INVALID_REQUEST", "data": None}
    )

# 공통 예외 처리기는 이미 작성된 것을 그대로 사용합니다.
# 그러면 400, 409 에러도 자동으로 {"message": "...", "data": null} 형식이 됩니다.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "data": None}
    )

# 전역 500 에러 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    # 클라이언트에게는 깔끔한 500 응답 반환
    return JSONResponse(
        status_code=500,
        content={"message": "INTERNAL_SERVER_ERROR", "data": None}
    )

app.include_router(post_router)
app.include_router(auth_router)
app.include_router(comment_router)
app.include_router(like_router)
app.include_router(user_router)