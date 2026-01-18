# routes/comment_route.py
from fastapi import APIRouter, Path, Response, Depends
from controllers.comment_controller import CommentController
from utils import BaseResponse, CommentCreateRequest, UserInfo, get_current_user

router = APIRouter(prefix="/api/v1")

# 1. 댓글 목록 조회 (로그인 안 해도 볼 수 있게 할지, 해야 볼 수 있게 할지 결정. 여기선 누구나 가능하게)
@router.get("/posts/{post_id}/comments", response_model=BaseResponse)
async def get_comments(
    post_id: int = Path(..., ge=1)
):
    return CommentController.get_comments(post_id)

# 2. 댓글 작성 (로그인 필수)
@router.post("/posts/{post_id}/comments", status_code=201, response_model=BaseResponse)
async def create_comment(
    response: Response,
    request: CommentCreateRequest,
    post_id: int = Path(..., ge=1),
    user: UserInfo = Depends(get_current_user)
):
    return CommentController.create_comment(post_id, request, user, response)

# 3. 댓글 삭제 (로그인 필수)
# 주의: URL이 /posts/... 가 아니라 /comments/... 입니다. 댓글 ID는 유니크하니까요.
@router.delete("/comments/{comment_id}", response_model=BaseResponse)
async def delete_comment(
    comment_id: int = Path(..., ge=1),
    user: UserInfo = Depends(get_current_user)
):
    return CommentController.delete_comment(comment_id, user)