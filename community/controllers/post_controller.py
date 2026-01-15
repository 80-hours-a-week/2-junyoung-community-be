# controllers/post_controller.py
from fastapi import HTTPException, Response
from models.post_model import PostModel
from utils import BaseResponse

class PostController:
    @staticmethod
    def get_posts(offset: int, size: int, response: Response):
        """전체 게시글 목록을 가져오는 흐름 제어"""
        
        # 1. 입력 유효성 검증
        if size <= 0:
            raise HTTPException(status_code=400, detail="SIZE_REQUIRED_POSITIVE")

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