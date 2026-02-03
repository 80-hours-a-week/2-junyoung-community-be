# models/like_model.py
from sqlalchemy import text
from database import engine

class LikeModel:
    
    # @staticmethod
    # def toggle_like(user_nickname: str, post_id: int):
    #     """
    #     좋아요 토글 기능:
    #     - 이미 눌렀으면 -> 삭제 (False 반환)
    #     - 안 눌렀으면 -> 추가 (True 반환)
    #     """
    #     # 1. 이미 누른 기록이 있는지 찾기
    #     for like in likes_db:
    #         if like["nickname"] == user_nickname and like["postId"] == post_id:
    #             # 이미 있으면 삭제 (좋아요 취소)
    #             likes_db.remove(like)
    #             return False # "취소됨"을 알림
        
    #     # 2. 없으면 추가 (좋아요)
    #     likes_db.append({"nickname": user_nickname, "postId": post_id})
    #     return True # "추가됨"을 알림

    @staticmethod
    def has_liked(userId: int, post_id: int):
        """DB에서 유저의 좋아요 여부 확인"""
        with engine.connect() as conn:
            query = text("SELECT id FROM post_likes WHERE post_id = :post_id AND user_id = :user_id")
            result = conn.execute(query, {"post_id": post_id, "user_id": userId}).fetchone()
            return True if result else False
        
    @staticmethod
    def add_like(userId: int, post_id: int):
        """DB에 좋아요 추가"""
        with engine.connect() as conn:
            query = text("INSERT INTO post_likes (post_id, user_id) VALUES (:post_id, :user_id)")
            conn.execute(query, {"post_id": post_id, "user_id": userId})
            conn.commit()

    @staticmethod
    def remove_like(userId: int, post_id: int):
        """좋아요 삭제"""
        with engine.connect() as conn:
            query = text("DELETE FROM post_likes WHERE post_id = :post_id AND user_id = :user_id")
            conn.execute(query, {"post_id": post_id, "user_id": userId})
            conn.commit()

    @staticmethod
    def delete_likes_by_post_id(post_id: int):
        """게시글 삭제 시 관련 좋아요 기록도 싹 지우기 (Cascade Delete)"""
        with engine.connect() as conn:
            query = text("DELETE FROM post_likes WHERE post_id = :post_id")
            conn.execute(query, {"post_id": post_id})
            conn.commit()