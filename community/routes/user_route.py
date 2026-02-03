# routes/user_route.py
from fastapi import APIRouter, Path, Request, Depends, UploadFile, File
from controllers.user_controller import UserController
from utils import BaseResponse, UserInfo, UserUpdateRequest, PasswordChangeRequest, get_current_user, limiter

router = APIRouter(prefix="/api/v1/users")

# 1. 회원 정보 조회
@router.get("/{userId}", response_model=BaseResponse)
@limiter.limit("30/minute")
async def get_user_info(
    request: Request,
    userId: int = Path(..., ge=1, description="사용자 ID"),
    current_user: UserInfo = Depends(get_current_user)
):
    return UserController.get_user_info(userId, current_user)

# 2. 회원 정보 수정 (닉네임, 프로필 등)
@router.put("/{userId}", response_model=BaseResponse)
@limiter.limit("10/minute")
async def update_user_info(
    request: Request,
    user_request: UserUpdateRequest,
    userId: int = Path(..., ge=1),
    current_user: UserInfo = Depends(get_current_user)
):
    return UserController.update_user_info(userId, user_request, current_user)

@router.post("/upload-profile")
async def upload_profile_image(file: UploadFile = File(...)):
    # 로직은 컨트롤러에게 전적으로 맡깁니다.
    return await UserController.upload_profile(file)

# 3. 비밀번호 변경
@router.put("/{userId}/password", response_model=BaseResponse)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    password_request: PasswordChangeRequest,
    userId: int = Path(..., ge=1),
    current_user: UserInfo = Depends(get_current_user)
):
    return UserController.change_password(userId, password_request, current_user)

# 4. 회원 탈퇴
@router.delete("/{userId}", response_model=BaseResponse)
@limiter.limit("5/minute")
async def delete_account(
    request: Request,
    userId: int = Path(..., ge=1),
    current_user: UserInfo = Depends(get_current_user)
):
    return UserController.delete_account(userId, current_user)