# controllers/user_controller.py
from fastapi import HTTPException
from models.user_model import UserModel
from utils import BaseResponse, UserInfo, UserUpdateRequest, PasswordChangeRequest
from security import SecurityUtils

class UserController:

    @staticmethod
    def check_permission(userId: int, current_user: UserInfo):
        """[보안] 요청한 userId와 로그인한 사람(current_user)이 같은지 확인"""
        if userId != current_user.userId:
            raise HTTPException(status_code=403, detail="PERMISSION_DENIED")

    @staticmethod
    def get_user_info(userId: int, current_user: UserInfo):
        """회원 정보 조회"""
        # 1. 권한 확인 (내 정보만 볼 수 있음)
        UserController.check_permission(userId, current_user)
        
        # 2. 유저 조회
        user = UserModel.find_by_id(userId)
        if not user:
            raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

        # 3. 반환 (비밀번호 제외)
        return BaseResponse(
            message="USER_INFO_SUCCESS",
            data={
                "userId": user["userId"],
                "email": user["email"],
                "nickname": user["nickname"],
                "profileImage": user.get("profileImage"),
                "status": user.get("status", "suspended")
            }
        )

    @staticmethod
    def update_user_info(userId: int, request: UserUpdateRequest, current_user: UserInfo):
        """회원 정보 수정 (닉네임, 프사)"""
        UserController.check_permission(userId, current_user)
        
        # 닉네임 중복 체크 (변경하려는 닉네임이 다를 경우에만)
        if request.nickname != current_user.nickname:
            if UserModel.find_by_nickname(request.nickname):
                raise HTTPException(status_code=409, detail="NICKNAME_ALREADY_EXISTS")

        UserModel.update_user(userId, request.model_dump())
        
        return BaseResponse(message="USER_UPDATE_SUCCESS", data=None)

    @staticmethod
    def change_password(userId: int, request: PasswordChangeRequest, current_user: UserInfo):
        """비밀번호 변경"""
        UserController.check_permission(userId, current_user)

        # 1. 현재 비밀번호 확인 (DB에서 직접 조회하여 비교)
        user = UserModel.find_by_id(userId)
        if not SecurityUtils.verify_password(request.currentPassword, user["password"]):
            raise HTTPException(status_code=401, detail="PASSWORD_MISMATCH")
        
        # 2. 변경
        UserModel.update_password(userId, request.newPassword)
        
        return BaseResponse(message="PASSWORD_CHANGE_SUCCESS", data=None)

    @staticmethod
    def delete_account(userId: int, current_user: UserInfo):
        """회원 탈퇴"""
        UserController.check_permission(userId, current_user)
        
        UserModel.delete_user(userId)
        
        return BaseResponse(message="USER_DELETE_SUCCESS", data=None)