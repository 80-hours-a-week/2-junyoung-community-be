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
from fastapi.middleware.cors import CORSMiddleware
from database import engine  # DB 엔진 가져오기
from models.user_model import UserModel  # 수정한 유저 모델
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# 허용할 프론트엔드 주소 목록
origins = [
    "http://localhost:5500",      # 로컬 개발 환경 (localhost)
    "http://127.0.0.1:5500",    # 로컬 개발 환경 (IP 주소)
    # "https://your-domain.com",  # 나중에 실제 배포할 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 특정 주소만 허용
    allow_credentials=True,      # 쿠키/인증 정보 포함 허용 (로그인 구현 시 필수)
    allow_methods=["*"],         # 모든 HTTP 메서드(GET, POST, PUT, DELETE 등) 허용
    allow_headers=["*"],         # 모든 HTTP 헤더 허용
)

@app.get("/")
def read_root():
    return {"message": "CORS 설정이 완료되었습니다."}

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

# main.py (진짜 딱 연결만 확인하는 용도)
@app.get("/db-ping")
def db_ping():
    from database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 'OK'")).fetchone()
        return {"result": result[0]} # 'OK'가 나오면 DB 연결은 완벽하다는 뜻!

app.include_router(post_router)
app.include_router(auth_router)
app.include_router(comment_router)
app.include_router(like_router)
app.include_router(user_router)

app.mount("/public", StaticFiles(directory="public"), name="public")