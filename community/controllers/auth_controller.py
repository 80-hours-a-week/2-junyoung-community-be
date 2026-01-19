# controllers/auth_controller.py
from fastapi import HTTPException, Response
from models.user_model import UserModel
from utils import BaseResponse, UserSignupRequest, UserLoginRequest



class AuthController:
    @staticmethod
    def signup(request: UserSignupRequest, response: Response):
        # # 1. 필수값 체크
        # if not request.email: raise HTTPException(status_code=400, detail="EMAIL_REQUIRED")
        # if not request.password: raise HTTPException(status_code=400, detail="PASSWORD_REQUIRED")
        # if not request.nickname: raise HTTPException(status_code=400, detail="NICKNAME_REQUIRED")
        
        # 2. 중복 체크 (이 코드가 진짜 들어있어야 막힙니다!)
        if UserModel.find_by_email(request.email):
            raise HTTPException(status_code=409, detail="EMAIL_ALREADY_EXISTS")
        if UserModel.find_by_nickname(request.nickname):
            raise HTTPException(status_code=409, detail="NICKNAME_ALREADY_EXISTS")

        # 3. 저장 및 반환 (설계서 규격인 userId로 맞춤)
        user_data = request.model_dump()
        user_id = UserModel.save_user(user_data)

        response.status_code = 201  # 상태 코드 설정
        return BaseResponse(
            message="REGISTER_SUCCESS", 
            data={"userId": user_id}
        )
    
    @staticmethod
    def login(request: UserLoginRequest, response: Response):

        user = UserModel.find_by_email(request.email)
        if not user or user["password"] != request.password:
            raise HTTPException(status_code=401, detail="LOGIN_FAILED")

        session_id = UserModel.create_session(request.email)
        # 보안을 위해 토큰은 따로 빼고 정보만 반환
        user_info = {
            "userId": user["user_id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profileImage": user.get("profileImage", "https://image.kr/img.jpg")
        }

        response.status_code = 200  # 상태 코드 설정
        return session_id, BaseResponse(message="LOGIN_SUCCESS", data=user_info)