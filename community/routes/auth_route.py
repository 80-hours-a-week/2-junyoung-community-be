# routes/auth_route.py
from fastapi import APIRouter, Body, Response, Request, Depends, Cookie
from controllers.auth_controller import AuthController
from utils import UserSignupRequest, UserLoginRequest, BaseResponse, limiter, get_current_user, UserInfo

router = APIRouter(prefix="/api/v1/auth")

@router.post("/signup", status_code=201, response_model=BaseResponse)
@limiter.limit("5/minute")  # 분당 5회로 제한
async def signup(request: Request, response: Response, user_request: UserSignupRequest):
    return AuthController.signup(user_request, response)

@router.post("/login", response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def login(request: Request, response: Response, user_request: UserLoginRequest):
    # 튜플로 나누어 받아서 에러 해결
    session_id, response_obj = AuthController.login(user_request, response)

    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    # user_info를 반환해야 WrappedAPIRoute가 정상 작동합니다.
    return response_obj

@router.get("/me", response_model=BaseResponse)
@limiter.limit("60/minute")
async def check_login_status(request: Request,user: UserInfo = Depends(get_current_user), session_id: str = Cookie(None)):

    return AuthController.get_me(user, session_id)