# utils.py
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import Request, Response, Cookie, HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute



# ⚠️ [위험] 여기서 모델을 가져옵니다. (지금은 괜찮지만...)
from models.user_model import UserModel

# 모든 응답의 표준 규격
class BaseResponse(BaseModel):
    message: str
    data: Any = None

# 게시글 상세 응답용 스키마
class PostDetail(BaseModel):
    postId: int
    title: str
    author: str
    content: str  # 목록 조회와 달리 본문이 포함됨
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
async def get_current_user(session_id: str | None = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="LOGIN_REQUIRED")
    
    user = UserModel.get_user_by_session(session_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="INVALID_SESSION")
    
    return user