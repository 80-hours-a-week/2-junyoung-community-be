# controllers/post_controller.py
from fastapi import HTTPException
from models.post_model import PostModel

class PostController:
    @staticmethod
    def get_posts(post_id: int, size: int):
        if size <= 0:
            raise HTTPException(status_code=400, detail="INVALID_REQUEST")

        all_posts = PostModel.get_all_posts()
        filtered_posts = [p for p in all_posts if p["postId"] >= post_id]

        if not filtered_posts:
            raise HTTPException(status_code=404, detail="NOT_FOUND")

        # [핵심 로직] 각 게시글 딕셔너리에서 'content' 필드만 제외하고 새로운 리스트 생성
        posts_without_content = []
        for post in filtered_posts[:size]:
            # content 항목을 뺀 나머지 데이터만 복사
            summary_post = {key: value for key, value in post.items() if key != "content"}
            posts_without_content.append(summary_post)

        return posts_without_content