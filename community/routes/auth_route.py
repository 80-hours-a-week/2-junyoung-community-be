# routes/auth_route.py
from fastapi import APIRouter, Body, Response
from controllers.auth_controller import AuthController
from utils import UserSignupRequest, UserLoginRequest, BaseResponse

router = APIRouter(prefix="/api/v1/auth")

@router.post("/signup", status_code=201, response_model=BaseResponse)
async def signup(response: Response, request: UserSignupRequest):
    return AuthController.signup(request, response)

@router.post("/login", response_model=BaseResponse)
async def login(response: Response, request: UserLoginRequest):
    # 튜플로 나누어 받아서 에러 해결
    session_id, response_obj = AuthController.login(request, response)

    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    # user_info를 반환해야 WrappedAPIRoute가 정상 작동합니다.
    return response_obj