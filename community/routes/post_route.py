# routes/post_route.py
from fastapi import APIRouter, Query
from controllers.post_controller import PostController
from utils import WrappedAPIRoute

router = APIRouter(prefix="/api/v1", route_class=WrappedAPIRoute)

@router.get("/posts")
async def get_all_posts(
    offset: int = Query(1, description="조회 시작 게시글 ID"),
    size: int = Query(10, description="가져올 게시글 개수")
):
    # Controller를 통해 데이터를 가져옵니다.    
    return PostController.get_posts(offset, size)