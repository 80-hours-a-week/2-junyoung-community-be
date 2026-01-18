# models/like_model.py

# 좋아요 저장소: [{"nickname": "junyoung", "postId": 1}, ...]
likes_db = []

class LikeModel:
    
    @staticmethod
    def toggle_like(user_nickname: str, post_id: int):
        """
        좋아요 토글 기능:
        - 이미 눌렀으면 -> 삭제 (False 반환)
        - 안 눌렀으면 -> 추가 (True 반환)
        """
        # 1. 이미 누른 기록이 있는지 찾기
        for like in likes_db:
            if like["nickname"] == user_nickname and like["postId"] == post_id:
                # 이미 있으면 삭제 (좋아요 취소)
                likes_db.remove(like)
                return False # "취소됨"을 알림
        
        # 2. 없으면 추가 (좋아요)
        likes_db.append({"nickname": user_nickname, "postId": post_id})
        return True # "추가됨"을 알림

    @staticmethod
    def has_liked(user_nickname: str, post_id: int):
        """특정 유저가 해당 글에 좋아요를 눌렀는지 확인"""
        for like in likes_db:
            if like["nickname"] == user_nickname and like["postId"] == post_id:
                return True
        return False
        
    @staticmethod
    def delete_likes_by_post_id(post_id: int):
        """게시글 삭제 시 관련 좋아요 기록도 싹 지우기 (Cascade Delete)"""
        likes_db[:] = [l for l in likes_db if l["postId"] != post_id]