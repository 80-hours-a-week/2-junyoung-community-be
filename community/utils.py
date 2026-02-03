# utils.py
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import Request, Response, Cookie, HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from models.user_model import UserModel
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import uuid
from fastapi import UploadFile


# Rate limiter 설정
# key_func=get_remote_address : 요청한 사람의 IP 주소를 기준으로 카운팅
limiter = Limiter(key_func=get_remote_address)


class FileService:
    UPLOAD_DIR = "public/images"

    @classmethod
    async def save_file(cls, file: UploadFile) -> str:
        """파일을 저장하고 접근 가능한 상대 경로를 반환합니다."""
        # 파일명 생성 로직
        extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(cls.UPLOAD_DIR, filename)

        # 실제 저장 로직 (나중에 이 부분만 S3 업로드 코드로 바꾸면 됩니다)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return f"/public/images/{filename}"

# 모든 응답의 표준 규격
class BaseResponse(BaseModel):
    message: str
    data: Any = None

# 사용자 정보 스키마
class UserInfo(BaseModel):
    userId: int
    email: EmailStr
    nickname: str
    profileImage: str | None = None # 없을 수도 있음
    status: str

# 게시글 생성 요청 스키마
class PostCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50, description="제목")
    content: str = Field(min_length=5, max_length=10000, description="내용")
    image: str | None = Field(default=None, description="이미지 URL (선택 사항)")

# 게시글 수정 요청 스키마
class PostUpdateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50, description="수정할 제목")
    content: str = Field(min_length=5, max_length=10000, description="수정할 내용")
    image: str | None = Field(default=None, description="수정할 이미지 URL (선택 사항)")



class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nickname: str = Field(min_length=2, max_length=30)
    profileImage: str | None = Field(default=None, description="프로필 이미지 URL (선택 사항)")

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserUpdateRequest(BaseModel):
    nickname: str = Field(min_length=2, max_length=30, description="변경할 닉네임")
    profileImage: str | None = Field(default=None, description="변경할 프로필 이미지 URL")

# 비밀번호 변경 요청
class PasswordChangeRequest(BaseModel):
    currentPassword: str = Field(..., description="현재 비밀번호")
    newPassword: str = Field(min_length=8, description="새로운 비밀번호")

# 현재 로그인한 사용자를 확인하는 의존성 함수
async def get_current_user(session_id: str | None = Cookie(default=None)) -> UserInfo:
    
    if not session_id:
        raise HTTPException(status_code=401, detail="LOGIN_REQUIRED")
    
    user_dict = UserModel.get_user_by_session(session_id)

    if not user_dict:
        raise HTTPException(status_code=401, detail="INVALID_SESSION")
    
    if user_dict.get("status") == "suspended":
        raise HTTPException(status_code=403, detail="ACCOUNT_SUSPENDED")

    return UserInfo(**user_dict)

# 댓글 생성 요청 스키마
class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=200, description="댓글 내용")

class CommentUpdateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=200, description="수정할 댓글 내용")

# 댓글 상세 응답용 스키마
class AuthorDetail(BaseModel):
    userId: int
    nickname: str
    profileImageUrl: str | None = None

# 댓글 상세 응답 스키마
class CommentDetailResponse(BaseModel):
    commentId: int
    content: str
    postId: int
    createdAt: str
    author: AuthorDetail

# 댓글 간단 응답용 스키마
class CommentSimple(BaseModel):
    author: str
    content: str
    createdAt: str

# 게시글 상세 응답용 스키마 (댓글 포함)
class PostDetail(BaseModel):
    postId: int
    title: str
    author: AuthorDetail
    content: str
    image: str | None = None
    createdAt: str
    likeCount: int = 0
    commentCount: int = 0
    viewCount: int = 0
    comments: list['CommentSimple'] = []