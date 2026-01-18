# routes/like_route.py
from fastapi import APIRouter, Path, Depends
from controllers.like_controller import LikeController
from utils import BaseResponse, UserInfo, get_current_user


router = APIRouter(prefix="/api/v1")

# 좋아요 토글 (누르면 켜지고, 다시 누르면 꺼짐)
@router.post("/posts/{post_id}/likes", response_model=BaseResponse)
async def toggle_like(
    post_id: int = Path(..., ge=1),
    user: UserInfo = Depends(get_current_user)
):
    return LikeController.toggle_like(post_id, user)