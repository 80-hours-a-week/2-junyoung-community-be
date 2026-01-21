# routes/auth_route.py
from fastapi import APIRouter, Response, Request, Depends
from controllers.auth_controller import AuthController
from utils import UserSignupRequest, UserLoginRequest, BaseResponse, limiter, get_current_user, UserInfo, UserUpdateRequest, PasswordChangeRequest

router = APIRouter(prefix="/api/v1/auth")

@router.post("/signup", status_code=201, response_model=BaseResponse)
@limiter.limit("5/minute")  # 분당 5회로 제한
async def signup(request: Request, response: Response, user_request: UserSignupRequest):
    return AuthController.signup(user_request, response)

@router.post("/login", response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def login(request: Request, response: Response, user_request: UserLoginRequest):

    session_id, response_obj = AuthController.login(user_request, response)

    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    return response_obj

@router.post("/logout", response_model=BaseResponse)
async def logout(
    request: Request, 
    response: Response,
    # 로그인 여부 체크 (로그인 안 한 사람은 로그아웃도 못함)
    user: UserInfo = Depends(get_current_user) 
):
    # 쿠키에서 직접 session_id를 꺼냅니다.
    session_id = request.cookies.get("session_id")
    
    return AuthController.logout(session_id, response)

