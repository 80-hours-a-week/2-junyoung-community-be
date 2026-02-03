# controllers/user_controller.py
import os
import uuid
from fastapi import HTTPException,UploadFile
from models.user_model import UserModel
from utils import BaseResponse, UserInfo, UserUpdateRequest, PasswordChangeRequest
from security import SecurityUtils
from utils import FileService, BaseResponse

BASE_URL = "http://127.0.0.1:8000"


class UserController:
    @staticmethod
    async def upload_profile(file: UploadFile):
        try:
            # 서비스 레이어를 통해 파일 저장
            file_url = await FileService.save_file(file)
            
            return BaseResponse(
                message="FILE_UPLOAD_SUCCESS",
                data={"profileImageUrl": file_url}
            )
        except Exception as e:
            # 시니어 팁: 로그는 상세히, 클라이언트 응답은 간결하게
            print(f"Upload error log: {e}")
            raise HTTPException(status_code=500, detail="IMAGE_UPLOAD_FAILED")

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

        # 프로필 이미지 경로 조립
        db_path = user.get("profileImage")
        full_url = f"{BASE_URL}{db_path}" if db_path else f"{BASE_URL}/public/images/default-profile.png"
        print(f"DB에서 가져온 경로: {user.get('profileImage')}")

        # 3. 반환 (비밀번호 제외)
        return BaseResponse(
            message="USER_INFO_SUCCESS",
            data={
                "userId": user["userId"],
                "email": user["email"],
                "nickname": user["nickname"],
                "profileImage": full_url,
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

        update_data = {
        "nickname": request.nickname,
        "profile_url": request.profileImage  # 프론트에서 보내는 필드명 확인 필요
        }
        
        UserModel.update_user(userId, update_data)
        
        return BaseResponse(message="USER_UPDATE_SUCCESS", data=None)

    @staticmethod
    def change_password(userId: int, request: PasswordChangeRequest, current_user: UserInfo):
        """비밀번호 변경"""
        UserController.check_permission(userId, current_user)

        # 2. 변경
        UserModel.update_password(userId, request.newPassword)
        
        return BaseResponse(message="PASSWORD_CHANGE_SUCCESS", data=None)

    @staticmethod
    def delete_account(userId: int, current_user: UserInfo):
        """회원 탈퇴"""
        UserController.check_permission(userId, current_user)
        
        UserModel.delete_user(userId)
        
        return BaseResponse(message="USER_DELETE_SUCCESS", data=None)