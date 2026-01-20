# controllers/post_controller.py
from datetime import datetime
from fastapi import HTTPException, Response
from models.post_model import PostModel
from models.user_model import UserModel
from models.comment_model import CommentModel
from models.like_model import LikeModel
from utils import BaseResponse, PostCreateRequest, PostDetail, UserInfo, PostUpdateRequest, CommentSimple, AuthorDetail

class PostController:
    @staticmethod
    def get_posts(offset: int, size: int, response: Response):
        """전체 게시글 목록을 가져오는 흐름 제어"""
        
        # 데이터 필터링 (Model에서 데이터 획득)
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
        PostModel.increase_view_count(post_id)
        
        # 3. [NEW] 작성자 상세 정보 찾기 (Join)
        # 게시글의 author(닉네임)로 유저 DB 검색
        post_author = UserModel.find_by_nickname(post["author"])
        
        # 유저 정보를 찾아서 AuthorDetail 객체 생성
        if post_author:
            author_data = AuthorDetail(
                userId=post_author["userId"],
                nickname=post_author["nickname"],
                profileImageUrl=post_author.get("profileImage")
            )
        else:
            # 탈퇴한 회원이거나 정보가 없을 경우 방어 코드
            author_data = AuthorDetail(
                userId=0, 
                nickname=post["author"], 
                profileImageUrl=None
            )

        # 4. 댓글 목록 가져오기 (기존 로직 유지)
        raw_comments = CommentModel.get_comments_by_post_id(post_id)
        comment_list = []
        for c in raw_comments:
            comment_list.append(CommentSimple(
                author=c["author"],  # 닉네임
                content=c["content"], # 내용
                createdAt=c.get("createdAt", "") # 작성일
            )) 

        # 5. 최종 응답 생성
        response_data = PostDetail(
            postId=post["postId"],
            title=post["title"],
            author=author_data,
            content=post["content"],
            createdAt=post["createdAt"],
            likeCount=post["likeCount"],
            commentCount=len(comment_list),
            viewCount=post["viewCount"],
            comments=comment_list # (아까 만든 댓글 리스트 변수)
        )
        
        return BaseResponse(
            message="POST_DETAIL_GET_SUCCESS",
            data=response_data
        )

    @staticmethod
    def create_post(request: PostCreateRequest, user: UserInfo, response: Response):
        """새 게시글 작성"""

        new_post = {
            "title": request.title,       # 클라이언트가 보낸 제목
            "content": request.content,   # 클라이언트가 보낸 내용
            "image": request.image,       # 클라이언트가 보낸 이미지
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
    
    @staticmethod
    def update_post(post_id: int, request: PostUpdateRequest, user: UserInfo, response: Response):
        """게시글 수정: 작성자 본인만 가능"""
        
        # 1. 게시글 존재 확인
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
        
        # 2. [핵심 보안] 권한 체크 (내 글이 아니면 403 Forbidden)
        if post["author"] != user.nickname:
            raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
        
        # 3. 업데이트 수행
        update_data = {
            "title": request.title,
            "content": request.content
        }
        PostModel.update_post(post_id, update_data)
        
        # 4. 응답
        return BaseResponse(
            message="POST_UPDATE_SUCCESS",
            data={"postId": post_id}
        )
    
    @staticmethod
    def delete_post(post_id: int, user: UserInfo, response: Response):
        """게시글 삭제: 작성자 본인만 가능"""
        
        # 1. 게시글 존재 확인
        post = PostModel.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
        
        # 2. 권한 체크 (내 글이 아니면 403)
        if post["author"] != user.nickname:
            raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
        
        # 3. 삭제 수행 (댓글, 좋아요도 함께 삭제)
        CommentModel.delete_comments_by_post_id(post_id)
        LikeModel.delete_likes_by_post_id(post_id)
        PostModel.delete_post(post_id)
        
        # 4. 응답
        return BaseResponse(
            message="POST_DELETE_SUCCESS",
            data=None
        )