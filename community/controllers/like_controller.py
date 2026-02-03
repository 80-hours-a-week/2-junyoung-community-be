# controllers/like_controller.py
from fastapi import HTTPException, Response
from models.like_model import LikeModel
from models.post_model import PostModel
from utils import BaseResponse, UserInfo

BASE_URL = "http://127.0.0.1:8000"


class LikeController:
    
    @staticmethod
    def add_like(post_id: int, user: UserInfo, response: Response):
        """좋아요 추가 (POST)"""
        
        # 1. 게시글 존재 확인
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")

        # 2. 중복 좋아요 방지 (409 Conflict)
        if LikeModel.has_liked(user.userId, post_id):
            raise HTTPException(status_code=409, detail="POST_ALREADY_LIKE")

        # 3. 데이터 업데이트
        LikeModel.add_like(user.userId, post_id)
        post["likeCount"] = post.get("likeCount", 0) + 1 # 동기화

        # 4. 응답 (201 Created)
        response.status_code = 201
        return BaseResponse(
            message="REGISTER_SUCCESS",
            data={
                "isLiked": True,
                "likeCount": post["likeCount"]
            }
        )

    @staticmethod
    def remove_like(post_id: int, user: UserInfo, response: Response):
        """좋아요 취소 (DELETE)"""
        
        # 1. 게시글 존재 확인
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")

        # 2. [409] 좋아요를 누른 적이 없는 경우 (POST_ALREADY_DELETE_LIKE)
        if not LikeModel.has_liked(user.userId, post_id):
            raise HTTPException(status_code=409, detail="POST_ALREADY_DELETE_LIKE")
        
        # 3. 데이터 업데이트
        LikeModel.remove_like(user.userId, post_id)
        post["likeCount"] -= 1 # 동기화

        if post["likeCount"] < 0:
            raise HTTPException(status_code=500, detail="DATA_INTEGRITY_ERROR")

        # 4. 응답 (200 OK - No Content 메시지)
        response.status_code = 200
        return BaseResponse(
            message="POST_LIKE_DELETE", # 좋아요가 사라졌음을 의미
            data={
                "isLiked": False,
                "likeCount": post["likeCount"]
            }
        )

    # @staticmethod
    # def toggle_like(post_id: int, user: UserInfo):
    #     """좋아요 추가/취소 (토글 방식)"""
        
    #     # 1. 게시글 존재 확인 (원본 객체 가져옴)
    #     post = PostModel.get_post_by_id(post_id)
    #     if not post:
    #         raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
            
        

    #     # 2. 모델에게 토글 요청 (User + Post 조합)
    #     is_liked = LikeModel.toggle_like(user.nickname, post_id)
        
    #     # 3. 결과에 따라 게시글의 likeCount 숫자 조정
    #     if is_liked:
    #         post["likeCount"] += 1
    #         message = "LIKE_ADDED"
    #     else:
    #         if post["likeCount"] <= 0:
    #             raise HTTPException(status_code=500, detail="DATA_INTEGRITY_ERROR")
            
    #         post["likeCount"] -= 1
    #         message = "LIKE_REMOVED"
            
    #     return BaseResponse(message=message, data={"currentLikeCount": post["likeCount"]})