# routes/auth_route.py
from fastapi import APIRouter, Body, Response
from controllers.auth_controller import AuthController
from utils import WrappedAPIRoute

router = APIRouter(prefix="/api/v1/auth", route_class=WrappedAPIRoute)

@router.post("/signup", status_code=201)
async def signup(body: dict = Body(...)):
    return AuthController.signup(body)

@router.post("/login")
async def login(response: Response, body: dict = Body(...)):
    # 튜플로 나누어 받아서 에러 해결
    session_id, user_info = AuthController.login(body)
    
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    # user_info를 반환해야 WrappedAPIRoute가 정상 작동합니다.
    return user_info