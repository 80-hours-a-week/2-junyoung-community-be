# controllers/comment_controller.py
from datetime import datetime
from fastapi import HTTPException, Response
from models.comment_model import CommentModel
from models.post_model import PostModel # 게시글 존재 확인용
from utils import BaseResponse, CommentCreateRequest, UserInfo, CommentUpdateRequest

class CommentController:
    
    @staticmethod
    def get_comments(post_id: int):
        """특정 게시글의 댓글 목록 조회"""
        
        # 1. 게시글이 있는지 먼저 검사
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
            
        # 2. 존재한다면 댓글 목록 가져오기
        comments = CommentModel.get_comments_by_post_id(post_id)
        
        return BaseResponse(
            message="COMMENT_LIST_SUCCESS", 
            data=comments
        )

    @staticmethod
    def create_comment(post_id: int, request: CommentCreateRequest, user: UserInfo, response: Response):
        """댓글 작성"""
        
        # 1. 부모 게시글이 진짜 있는지 확인 (무결성 검사)
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
            
        # 2. 댓글 데이터 조립 (Foreign Key: postId 포함)
        new_comment = {
            "postId": post_id,                # 어떤 글에 달린 댓글인지 연결고리
            "content": request.content,
            "author": user.nickname,          # 작성자
            "profileImage": user.profileImage or "https://image.kr/default.jpg",
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        comment_id = CommentModel.create_comment(new_comment)
        post["commentCount"] += 1        
        
        response.status_code = 201
        return BaseResponse(message="COMMENT_CREATE_SUCCESS", data={"commentId": comment_id})

    @staticmethod
    def update_comment(comment_id: int, request: CommentUpdateRequest, user: UserInfo, response: Response):
        """댓글 수정"""
        
        # 1. [404] 댓글 존재 확인
        comment = CommentModel.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="NOT_FOUND")
            
        # 2. [403] 권한 확인
        if comment["author"] != user.nickname: # 혹은 userId로 비교 추천
            raise HTTPException(status_code=403, detail="FORBIDDEN")
            
        # 3. [Logic] 내용 수정
        CommentModel.update_comment(comment_id, request.content)
        
        # 4. [200] 성공 응답 (204 Spec 대체)
        response.status_code = 200
        return BaseResponse(
            message="COMMENT_UPDATE_SUCCESS", # 요청하신 메시지
            data=None
        )

    @staticmethod
    def delete_comment(comment_id: int, user: UserInfo):
        """댓글 삭제 (본인만 가능)"""
        
        # 1. 댓글 존재 확인
        comment = CommentModel.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="COMMENT_NOT_FOUND")
            
        # 2. 권한 확인
        if comment["author"] != user.nickname:
            raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
            
        # 댓글이 달린 게시글의 commentCount 감소
        target_post = PostModel.get_post_by_id(comment["postId"])
        if target_post:
            target_post["commentCount"] -= 1
            current_count = target_post["commentCount"]

        # 3. 삭제
        CommentModel.delete_comment(comment_id)
        
        return BaseResponse(message="COMMENT_DELETE_SUCCESS", data={"commentCount": current_count})