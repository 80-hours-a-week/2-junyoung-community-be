# controllers/post_controller.py
from datetime import datetime
from fastapi import HTTPException, Response
from models.post_model import PostModel
from utils import BaseResponse, PostCreateRequest, PostDetail, UserInfo

class PostController:
    @staticmethod
    def get_posts(offset: int, size: int, response: Response):
        """전체 게시글 목록을 가져오는 흐름 제어"""
        
        # 2. 데이터 필터링 (Model에서 데이터 획득)
        all_posts = PostModel.get_all_posts()
        filtered_posts = [p for p in all_posts if p["postId"] >= offset]

        if not filtered_posts:
            raise HTTPException(status_code=404, detail="POSTS_NOT_FOUND")
        
        summaries = PostController._prepare_post_summaries(filtered_posts, size)
        
        response.status_code = 200  # 상태 코드 설정
        return BaseResponse(
            message="POST_RETRIEVAL_SUCCESS",
            data=summaries
        )

    @staticmethod
    def _prepare_post_summaries(posts, size):
        """게시글 상세 내용을 제거하고 요약본 생성"""
        
        summaries = []
        for post in posts[:size]:
            # content 필드를 제외한 post 생성
            summary = {
                "postId": post["postId"],
                "title": post["title"],
                "author": post["author"],
                "profileImage": post["profileImage"],
                "createdAt": post["createdAt"],
                "likeCount": post.get("likeCount", 0),
                "commentCount": post.get("commentCount", 0),
                "viewCount": post.get("viewCount", 0)
            }
            summaries.append(summary)

        return summaries
    
    @staticmethod
    def get_post_detail(post_id: int, response: Response) -> BaseResponse:
        """게시글 상세 조회 및 조회수 증가"""
        
        # 1. 게시글 찾기
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
        
        # 2. 조회수 증가 (비즈니스 로직)
        # 실제 DB라면 update 쿼리를 날려야겠지만, 메모리 DB라 직접 수정
        post["viewCount"] = post.get("viewCount", 0) + 1
        
        # 3. 응답 객체 변환 (Pydantic 모델 사용)
        post_detail = PostDetail(**post)

        response.status_code = 200
        return BaseResponse(
            message="POST_DETAIL_GET_SUCCESS",
            data=post_detail
        )

    @staticmethod
    def create_post(request: PostCreateRequest, user: UserInfo, response: Response):

        new_post = {
            "title": request.title,       # 클라이언트가 보낸 제목
            "content": request.content,   # 클라이언트가 보낸 내용
            "author": user.nickname,      
            "profileImage": user.profileImage or "https://image.kr/img.jpg",
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likeCount": 0, "commentCount": 0, "viewCount": 0
        }
        
        # Model에게 저장을 부탁함
        post_id = PostModel.create_post(new_post)

        response.status_code = 201
        return BaseResponse(
            message="POST_CREATE_SUCCESS",
            data={"postId": post_id}
        )