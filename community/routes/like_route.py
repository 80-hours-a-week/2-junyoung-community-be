# routes/like_route.py
from fastapi import APIRouter, Path, Depends, Request, Response
from controllers.like_controller import LikeController
from utils import BaseResponse, UserInfo, get_current_user, limiter


router = APIRouter(prefix="/api/v1")

# 1. 좋아요 추가 (POST)
@router.post("/posts/{post_id}/likes", status_code=201, response_model=BaseResponse)
@limiter.limit("20/minute") # 도배 방지
async def add_like(
    request: Request,
    response: Response,
    post_id: int = Path(..., ge=1, description="게시글 ID"),
    user: UserInfo = Depends(get_current_user)
):
    return LikeController.add_like(post_id, user, response)

# 2. 좋아요 취소 (DELETE)
@router.delete("/posts/{post_id}/likes", response_model=BaseResponse)
@limiter.limit("20/minute") # 도배 방지
async def remove_like(
    request: Request,
    response: Response,
    post_id: int = Path(..., ge=1, description="게시글 ID"),
    user: UserInfo = Depends(get_current_user)
):
    return LikeController.remove_like(post_id, user, response)

# # 좋아요 토글 (누르면 켜지고, 다시 누르면 꺼짐)
# @router.post("/posts/{post_id}/likes", response_model=BaseResponse)
# @limiter.limit("10/minute")  # 분당 10회로 제한
# async def toggle_like(
#     request: Request,
#     post_id: int = Path(..., ge=1),
#     user: UserInfo = Depends(get_current_user)
# ):
#     return LikeController.toggle_like(post_id, user)