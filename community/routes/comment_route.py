# routes/comment_route.py
from fastapi import APIRouter, Path, Response, Depends, Request
from controllers.comment_controller import CommentController
from utils import BaseResponse, CommentCreateRequest, UserInfo, get_current_user, limiter, CommentUpdateRequest

router = APIRouter(prefix="/api/v1")

# 1. 댓글 목록 조회 
@router.get("/posts/{post_id}/comments", response_model=BaseResponse)
@limiter.limit("20/minute")  # 분당 10회로 제한
async def get_comments(
    request: Request,
    post_id: int = Path(..., ge=1),
    user: UserInfo = Depends(get_current_user)
):
    return CommentController.get_comments(post_id)

# 2. 댓글 작성 (로그인 필수)
@router.post("/posts/{post_id}/comments", status_code=201, response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def create_comment(
    request: Request,
    response: Response,
    comment_request: CommentCreateRequest,
    post_id: int = Path(..., ge=1),
    user: UserInfo = Depends(get_current_user)
):
    return CommentController.create_comment(post_id, comment_request, user, response)

# 3. 댓글 수정
@router.put("/comments/{comment_id}", response_model=BaseResponse)
@limiter.limit("10/minute") # 도배 방지
async def update_comment(
    request: Request,
    response: Response,
    comment_request: CommentUpdateRequest, # Body 데이터 (content)
    comment_id: int = Path(..., ge=1),     # Path 파라미터
    user: UserInfo = Depends(get_current_user) # 로그인 필수
):
    return CommentController.update_comment(comment_id, comment_request, user, response)

# 3. 댓글 삭제 (로그인 필수)
@router.delete("/comments/{comment_id}", response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def delete_comment(
    request: Request,
    comment_id: int = Path(..., ge=1),
    user: UserInfo = Depends(get_current_user)
):
    return CommentController.delete_comment(comment_id, user)