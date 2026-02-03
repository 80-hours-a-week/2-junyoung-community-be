# controllers/auth_controller.py
from fastapi import HTTPException, Response
from models.user_model import UserModel
from utils import BaseResponse, UserSignupRequest, UserLoginRequest, UserInfo
from security import SecurityUtils

BASE_URL = "http://127.0.0.1:8000"


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
        if user.get("status") == "suspended_perm":
            raise HTTPException(status_code=403, detail="ACCOUNT_SUSPENDED")
        
        elif user.get("status") == "suspended_temp":
            # 일시 정지의 경우, 언제 정지됐는지 정보를 함께 주면 더 친절하겠지?
            detail_msg = f"ACCOUNT_TEMPORARILY_SUSPENDED (Started at: {user.get('suspensionStart')})"
            raise HTTPException(status_code=403, detail=detail_msg)

        # 3. [409] 이미 로그인된 계정 체크 (ALREADY_LOGIN)
        if UserModel.is_already_logged_in(request.email):
            raise HTTPException(status_code=409, detail="ALREADY_LOGIN")

        session_id = UserModel.create_session(user["userId"])
        # 보안을 위해 토큰은 따로 빼고 정보만 반환
        db_path = user.get("profile_url")
        full_url = f"{BASE_URL}{db_path}" if db_path else f"{BASE_URL}/public/images/default-profile.png"

        user_info = {
            "userId": user["userId"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profileImage": full_url, # 여기서 이미 전체 주소를 담아 보냄
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
