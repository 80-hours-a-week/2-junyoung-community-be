# routes/post_route.py
from fastapi import APIRouter, Query, Path, Response, Depends, Request
from controllers.post_controller import PostController
from utils import BaseResponse, get_current_user, UserInfo, PostCreateRequest, PostUpdateRequest, limiter

# router = APIRouter(prefix="/api/v1")
router = APIRouter(
    prefix="/api/v1", 
    dependencies=[Depends(get_current_user)] 
)


# 전체 게시물 조회
@router.get("/posts", response_model=BaseResponse)
@limiter.limit("20/minute")  # 분당 20회로 제한
async def get_all_posts(
    request: Request,
    response: Response,
    offset: int = Query(1, ge=1, description="조회 시작 게시글 ID"),
    size: int = Query(10, ge=0, le=100, description="가져올 게시글 개수")
):
    # Controller를 통해 데이터를 가져옵니다.    
    return PostController.get_posts(offset, size, response)

# 상세 게시물 조회
@router.get("/posts/{post_id}", response_model=BaseResponse)
@limiter.limit("20/minute")  # 분당 30회로 제한
async def get_post_detail(
    request: Request,
    response: Response,
    post_id: int = Path(..., ge=1, description="게시글 ID (1 이상)"),
):
    return PostController.get_post_detail(post_id, response)

# 게시물 추가
@router.post("/posts", status_code=201, response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def create_post(
    request: Request,
    response: Response,
    post_request: PostCreateRequest,
    user: UserInfo = Depends(get_current_user)
):
    # 컨트롤러에게 요청 데이터와 유저 정보를 함께 넘김
    return PostController.create_post(post_request, user, response)

# 게시물 수정
@router.put("/posts/{post_id}", response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def update_post(
    request: Request,
    response: Response,
    post_request: PostUpdateRequest,
    # 1. Path 파라미터로 수정할 글 번호를 받음
    post_id: int = Path(..., ge=1, description="게시글 ID"),
    user: UserInfo = Depends(get_current_user)
):
    return PostController.update_post(post_id, post_request, user, response)

# 게시물 삭제
@router.delete("/posts/{post_id}", response_model=BaseResponse)
@limiter.limit("10/minute")  # 분당 10회로 제한
async def delete_post(
    request: Request,
    response: Response,
    post_id: int = Path(..., ge=1, description="삭제할 게시글 ID"),
    user: UserInfo = Depends(get_current_user)
):
    return PostController.delete_post(post_id, user, response)