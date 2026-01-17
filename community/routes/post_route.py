# routes/post_route.py
from fastapi import APIRouter, Query, Path, Response, Depends
from controllers.post_controller import PostController
from utils import BaseResponse, get_current_user, UserInfo, PostCreateRequest

# router = APIRouter(prefix="/api/v1")
# utils에 있는 함수로 문지기를 세움
router = APIRouter(
    prefix="/api/v1", 
    dependencies=[Depends(get_current_user)] 
)


# 전체 게시물 조회
@router.get("/posts", response_model=BaseResponse)
async def get_all_posts(
    response: Response,
    offset: int = Query(1, ge=1, description="조회 시작 게시글 ID"),
    size: int = Query(10, ge=0, le=100, description="가져올 게시글 개수")
):
    # Controller를 통해 데이터를 가져옵니다.    
    return PostController.get_posts(offset, size, response)

# 상세 게시물 조회
@router.get("/posts/{post_id}", response_model=BaseResponse)
async def get_post_detail(
    response: Response,
    # Path Parameter 검증: 1 이상의 정수만 허용
    post_id: int = Path(..., ge=1, description="게시글 ID (1 이상)"),
):
    return PostController.get_post_detail(post_id, response)

# 게시물 생성
@router.post("/posts", status_code=201, response_model=BaseResponse)
async def create_post(
    response: Response,
    request: PostCreateRequest,
    user: dict = Depends(get_current_user) 
):
    # 컨트롤러에게 요청 데이터와 유저 정보를 함께 넘김
    return PostController.create_post(request, user, response)