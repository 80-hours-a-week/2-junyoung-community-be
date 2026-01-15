# controllers/auth_controller.py
from fastapi import HTTPException
from models.user_model import UserModel
from utils import BaseResponse
from fastapi import Response


class AuthController:
    @staticmethod
    def signup(data: dict, response: Response):
        # 1. 필수값 체크
        if not data.get("email"): raise HTTPException(status_code=400, detail="EMAIL_REQUIRED")
        if not data.get("password"): raise HTTPException(status_code=400, detail="PASSWORD_REQUIRED")
        if not data.get("nickname"): raise HTTPException(status_code=400, detail="NICKNAME_REQUIRED")

        # 2. 중복 체크 (이 코드가 진짜 들어있어야 막힙니다!)
        if UserModel.find_by_email(data["email"]):
            raise HTTPException(status_code=409, detail="EMAIL_ALREADY_EXISTS")
        if UserModel.find_by_nickname(data["nickname"]):
            raise HTTPException(status_code=409, detail="NICKNAME_ALREADY_EXISTS")

        # 3. 저장 및 반환 (설계서 규격인 userId로 맞춤)
        user_id = UserModel.save_user(data)
        response.status_code = 201  # 상태 코드 설정
        return BaseResponse(
            message="REGISTER_SUCCESS", 
            data={"userId": user_id}
        )
    
    @staticmethod
    def login(data: dict, response: Response):
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise HTTPException(status_code=400, detail="EMAIL_REQUIRED")
        if not password:
            raise HTTPException(status_code=400, detail="PASSWORD_REQUIRED")
        
        user = UserModel.find_by_email(email)
        if not user or user["password"] != password:
            raise HTTPException(status_code=401, detail="LOGIN_FAILED")

        session_id = UserModel.create_session(email)
        
        # 보안을 위해 토큰은 따로 빼고 정보만 반환
        user_info = {
            "userId": user["user_id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profileImage": user.get("profileImage", "https://image.kr/img.jpg")
        }

        response.status_code = 200  # 상태 코드 설정
        return session_id, BaseResponse(message="LOGIN_SUCCESS", data=user_info)