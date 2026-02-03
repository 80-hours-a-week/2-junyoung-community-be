# controllers/comment_controller.py
from datetime import datetime
from fastapi import HTTPException, Response
from models.comment_model import CommentModel
from models.user_model import UserModel
from models.post_model import PostModel # 게시글 존재 확인용
from utils import BaseResponse, CommentCreateRequest, UserInfo, CommentUpdateRequest, AuthorDetail, CommentDetailResponse

BASE_URL = "http://127.0.0.1:8000"

class CommentController:
    
    @staticmethod
    def get_comments(post_id: int):
        """특정 게시글의 댓글 목록 조회"""
        
        # 1. 게시글이 있는지 먼저 검사
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
            
        # 2. 댓글 목록 가져오기
        comments = CommentModel.get_comments_by_post_id(post_id)
        
        response_list = []

        for comment in comments:
            # 댓글에 적힌 작성자 닉네임으로 유저 정보를 찾습니다.
            # (만약 DB에 userId로 저장했다면 find_by_id로 찾으면 됩니다)
            author_user = UserModel.find_by_nickname(comment["author"])
            
            # 유저가 탈퇴해서 없을 수도 있으니 방어 로직
            if author_user:

                db_path = author_user.get("profile_url")
                
                # [핵심] BASE_URL과 결합하여 전체 주소 생성
                # 이미지가 없으면 기본 프로필 이미지를 연결합니다.
                full_profile_url = f"{BASE_URL}{db_path}" if db_path else f"{BASE_URL}/public/images/default-profile.png"

                author_data = {
                    "userId" : author_user["id"],
                    "nickname":author_user["nickname"],
                    # DB엔 profileImage지만, 요청하신 응답은 profileImageUrl이므로 이름 변경 매핑
                    "profileImage":full_profile_url 
                }
            else:
                # 탈퇴한 유저 처리 (더미 데이터)
                author_data = {
                    "userId":0,
                    "nickname":"(알수없음)",
                    "profileImage":f"{BASE_URL}/public/images/default-profile.png"
                }

            # 최종 데이터 조립

            raw_date = comment.get("createdAt")
            formatted_date = raw_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(raw_date, datetime) else str(raw_date)

            response_data = {
                "commentId":comment["commentId"],
                "content":comment["content"],
                "postId":post_id,
                "createdAt":formatted_date,
                "author":author_data # 객체 넣기
            }
            response_list.append(response_data)
        
        return BaseResponse(
            message="COMMENT_LIST_SUCCESS", 
            data=response_list
        )

    @staticmethod
    def create_comment(post_id: int, request: CommentCreateRequest, user: UserInfo, response: Response):
        """댓글 작성"""
        
        # 1. 부모 게시글이 진짜 있는지 확인 (무결성 검사)
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
            
        target_post = post[0] if isinstance(post, list) and len(post) > 0 else post

        # 2. 댓글 데이터 조립 (Foreign Key: postId 포함)
        new_comment = {
            "postId": post_id,                # 어떤 글에 달린 댓글인지 연결고리
            "content": request.content,
            "userId": user.userId,          # 작성자
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
            
        db_author_id = comment.get('userId')

        # 2. 권한 확인: DB에 저장된 유저ID와 현재 로그인한 유저ID(숫자)를 비교
        if db_author_id != user.userId:
            # 로그를 찍어보면 확실히 알 수 있습니다.
            print(f"권한 에러 - DB 주인 ID: {db_author_id}, 접속 유저 ID: {user.userId}")
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
        if comment.get("userId") != user.userId:
            raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
            
        # 댓글이 달린 게시글의 commentCount 감소
        target_post = PostModel.get_post_by_id(comment["postId"])
        if target_post:
            target_post["commentCount"] -= 1
            current_count = target_post["commentCount"]

        # 3. 삭제
        CommentModel.delete_comment(comment_id)
        
        return BaseResponse(message="COMMENT_DELETE_SUCCESS", data={"commentCount": current_count})