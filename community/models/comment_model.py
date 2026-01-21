# models/comment_model.py
from datetime import datetime

# 댓글 저장소 (In-Memory DB)
comments_db = []

class CommentModel:
    
    @staticmethod
    def create_comment(comment_data: dict):
        '''새 댓글 생성 및 저장'''
        new_id = 1
        if comments_db:
            new_id = max(comment["commentId"] for comment in comments_db) + 1
            
        comment_data["commentId"] = new_id
        comments_db.append(comment_data)
        return new_id

    @staticmethod
    def update_comment(comment_id: int, content: str):
        '''댓글 내용 수정'''
        for comment in comments_db:
            if comment["commentId"] == comment_id:
                comment["content"] = content
                comment["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False

    @staticmethod
    def get_comments_by_post_id(post_id: int):
        '''특정 게시글의 댓글 목록 조회'''
        # 리스트 컴프리헨션으로 필터링 (SQL의 WHERE post_id = ? 와 같음)
        return [comment for comment in comments_db if comment["postId"] == post_id]

    @staticmethod
    def get_comment_by_id(comment_id: int):
        '''특정 댓글 조회'''
        for comment in comments_db:
            if comment["commentId"] == comment_id:
                return comment
        return None

    @staticmethod
    def delete_comment(comment_id: int):
        '''특정 댓글 삭제'''
        for comment in comments_db:
            if comment["commentId"] == comment_id:
                comments_db.remove(comment)
                return True
        return False
    
    @staticmethod
    def delete_comments_by_post_id(post_id: int):
        '''특정 게시글에 달린 모든 댓글 삭제'''
        # postId가 지우려는 post_id와 다른 댓글만 남기고 삭제
        comments_db[:] = [c for c in comments_db if c["postId"] != post_id]