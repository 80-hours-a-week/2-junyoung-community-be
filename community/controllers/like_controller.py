# controllers/like_controller.py
from fastapi import HTTPException, Response
from models.like_model import LikeModel
from models.post_model import PostModel
from utils import BaseResponse, UserInfo

class LikeController:
    
    @staticmethod
    def toggle_like(post_id: int, user: UserInfo):
        """좋아요 추가/취소 (토글 방식)"""
        
        # 1. 게시글 존재 확인 (원본 객체 가져옴)
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
            
        # 2. 모델에게 토글 요청 (User + Post 조합)
        is_liked = LikeModel.toggle_like(user.nickname, post_id)
        
        # 3. 결과에 따라 게시글의 likeCount 숫자 조정
        if is_liked:
            post["likeCount"] += 1
            message = "LIKE_ADDED"
        else:
            if post["likeCount"] <= 0:
                raise HTTPException(status_code=500, detail="DATA_INTEGRITY_ERROR")
            
            post["likeCount"] -= 1
            message = "LIKE_REMOVED"
            
        return BaseResponse(message=message, data={"currentLikeCount": post["likeCount"]})