# controllers/auth_controller.py
from fastapi import HTTPException, Response
from models.user_model import UserModel
from utils import BaseResponse, UserSignupRequest, UserLoginRequest, UserInfo
from security import SecurityUtils

class AuthController:

    @staticmethod
    def signup(request: UserSignupRequest, response: Response):
                
        # 1. 중복 검사 (이메일, 닉네임)
        if UserModel.find_by_email(request.email):
            raise HTTPException(status_code=409, detail="EMAIL_ALREADY_EXISTS")
        if UserModel.find_by_nickname(request.nickname):
            raise HTTPException(status_code=409, detail="NICKNAME_ALREADY_EXISTS")

        # 2. 저장 및 반환 (설계서 규격인 userId로 맞춤)
        user_data = request.model_dump()
        userId = UserModel.save_user(user_data)

        response.status_code = 201  # 상태 코드 설정
        return BaseResponse(
            message="REGISTER_SUCCESS", 
            data={"userId": userId}
        )
    
    @staticmethod
    def login(request: UserLoginRequest, response: Response):

        user = UserModel.find_by_email(request.email)

        # 1. [401] 사용자 존재 여부 및 비밀번호 일치 여부 확인
        if not user or not SecurityUtils.verify_password(request.password, user["password"]):
            raise HTTPException(status_code=401, detail="LOGIN_FAILED")
        
        # 2. [403] 정지된 계정 체크 (ACCOUNT_SUSPENDED)
        if user.get("status") == "suspended":
            raise HTTPException(status_code=403, detail="ACCOUNT_SUSPENDED")
        
        # 3. [409] 이미 로그인된 계정 체크 (ALREADY_LOGIN)
        if UserModel.is_already_logged_in(request.email):
            raise HTTPException(status_code=409, detail="ALREADY_LOGIN")

        session_id = UserModel.create_session(request.email)
        # 보안을 위해 토큰은 따로 빼고 정보만 반환
        user_info = {
            "userId": user["userId"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profileImage": user.get("profileImage", "https://image.kr/img.jpg"),
            "authToken": session_id
        }

        response.status_code = 200  # 상태 코드 설정
        return session_id, BaseResponse(message="LOGIN_SUCCESS", data=user_info)
    
    @staticmethod
    def logout(session_id: str, response: Response):
        """
        로그아웃 비즈니스 로직
        """
        # 1. 서버 메모리에서 세션 삭제
        UserModel.delete_session(session_id)
        
        # 2. 브라우저 쿠키 삭제 (만료 시간을 0으로 설정하여 즉시 파기)
        response.delete_cookie(key="session_id")
        
        return BaseResponse(message="LOGOUT_SUCCESS", data=None)
