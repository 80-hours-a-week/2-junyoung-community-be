# utils.py
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import Request, Response, Cookie, HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from models.user_model import UserModel
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter 설정
# key_func=get_remote_address : 요청한 사람의 IP 주소를 기준으로 카운팅
limiter = Limiter(key_func=get_remote_address)

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

# 게시글 생성 요청 스키마
class PostCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50, description="제목")
    content: str = Field(min_length=5, max_length=10000, description="내용")
    image: str | None = Field(default=None, description="이미지 URL (선택 사항)")

# 게시글 수정 요청 스키마
class PostUpdateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50, description="수정할 제목")
    content: str = Field(min_length=5, max_length=10000, description="수정할 내용")

# 게시글 상세 응답용 스키마
class PostDetail(BaseModel):
    postId: int
    title: str
    author: str
    content: str  # 목록 조회와 달리 본문이 포함됨
    image: str | None = None
    profileImage: str
    createdAt: str
    likeCount: int = 0
    commentCount: int = 0
    viewCount: int = 0

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nickname: str = Field(min_length=2, max_length=30)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

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