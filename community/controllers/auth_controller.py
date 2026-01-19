# controllers/auth_controller.py
from fastapi import HTTPException, Response
from models.user_model import UserModel
from utils import BaseResponse, UserSignupRequest, UserLoginRequest, UserInfo



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
        if not user or user["password"] != request.password:
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
            "profileImage": user.get("profileImage", "https://image.kr/img.jpg")
        }

        response.status_code = 200  # 상태 코드 설정
        return session_id, BaseResponse(message="LOGIN_SUCCESS", data=user_info)
    
    @staticmethod
    def get_me(user: UserInfo, session_id: str) -> BaseResponse:
        """
        내 정보 조회 비즈니스 로직
        """
        # 응답 데이터(Output Format)를 여기서 다 만듭니다.
        response_data = {
            "userId": user.userId,
            "email": user.email,
            "nickname": user.nickname,
            "profileImage": user.profileImage,
            "authToken": session_id 
        }

        # 최종 응답 객체 반환
        return BaseResponse(
            message="AUTH_SUCCESS",
            data=response_data
        )