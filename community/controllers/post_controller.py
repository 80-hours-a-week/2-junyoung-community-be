# controllers/post_controller.py
from datetime import datetime
from fastapi import HTTPException, Response, UploadFile
from models.post_model import PostModel
from models.user_model import UserModel
from models.comment_model import CommentModel
from models.like_model import LikeModel
from utils import BaseResponse, PostCreateRequest, PostDetail, UserInfo, PostUpdateRequest, CommentSimple, AuthorDetail, FileService

BASE_URL = "http://127.0.0.1:8000"

class PostController:
    @staticmethod
    def get_posts(last_post_id: int, size: int, response: Response):
        """전체 게시글 목록을 가져오는 흐름 제어"""
        
        # [방어 코드] 0이나 음수가 들어오면 처음부터 보여주도록 None 처리
        actual_last_id = None if (last_post_id is None or last_post_id <= 0) else last_post_id
        
        # 1. 모델에서 데이터 가져오기
        posts = PostModel.get_all_posts(last_post_id=actual_last_id, size=size)

        if not posts:
            response.status_code = 200
            return BaseResponse(message="NO_MORE_POSTS", data={"posts": [], "nextCursor": None})

        # [핵심 수정] DB의 상대경로를 전체 URL로 변환하여 공급
        for post in posts:
            author_info = post.get("author", {})
            db_path = author_info.get("profileImage")
            
            if db_path and db_path.startswith("http"):
                full_url = db_path
            elif db_path:
                full_url = f"{BASE_URL}{db_path}"
            else:
                full_url = f"{BASE_URL}/public/images/default-profile.png"
            
            # 덮어씌우지 않고, author 객체 내부의 값을 업데이트합니다.
            post["author"]["profileImage"] = full_url
            
        # 3. [핵심] 다음 페이지의 기준점(nextCursor) 계산
        # 가져온 데이터의 마지막 항목 ID를 다음 요청 때 쓰라고 알려줍니다.
        # 만약 요청한 size보다 적게 가져왔다면 '더 이상 글이 없음'을 의미하므로 None을 줍니다.
        next_cursor = posts[-1]["postId"] if len(posts) == size else None

        response.status_code = 200
        return BaseResponse(
            message="POST_RETRIEVAL_SUCCESS",
            data={
                "posts": posts,
                "nextCursor": next_cursor
            }
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
    def get_post_detail(post_id: int, response: Response, user: UserInfo = None) -> BaseResponse:
        """게시글 상세 조회 및 조회수 증가 (댓글은 별도 API에서 처리)"""
    
        # 2. 조회수 증가 (비즈니스 로직)
        PostModel.increase_view_count(post_id)

        # 1. 게시글과 작성자 정보를 한 번에 가져옴 (Model에서 Join 처리됨)
        post = PostModel.get_post_by_id(post_id)
        
        if not post:
            # 특정 글을 찍어서 들어왔는데 없으면 에러(Raise)가 정답!
            raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
        
        # 2. 본문 이미지 경로 조립 (프로필 방식과 동일)
        post_img_path = post.get("image_url") 
        if post_img_path:
            # DB에 경로가 있으면 전체 URL로 변환
            post["image"] = f"{BASE_URL}{post_img_path}"
        else:
            # 이미지가 없으면 null 혹은 빈 값 처리
            post["image"] = None
        
        author_info = post.get("author", {})
        profile_path = author_info.get("profileImage")
        post["isLiked"] = LikeModel.has_liked(user.userId, post_id)
        
        if profile_path and not profile_path.startswith("http"):
            # 상대 경로인 경우 백엔드 주소(8000번)를 붙여줌
            post["author"]["profileImage"] = f"{BASE_URL}{profile_path}"
        elif not profile_path:
            # 이미지가 없는 경우 백엔드의 기본 이미지 경로 전송
            post["author"]["profileImage"] = f"{BASE_URL}/public/images/default-profile.png"

        
        response.status_code = 200
        return BaseResponse(
            message="POST_DETAIL_SUCCESS",
            data=post
        )

    @staticmethod
    def create_post(request: PostCreateRequest, user: UserInfo, response: Response):
        """새 게시글 작성"""

        new_post = {
            "title": request.title,       # 클라이언트가 보낸 제목
            "content": request.content,   # 클라이언트가 보낸 내용
            "image_url": request.image,       # 클라이언트가 보낸 이미지
            "author": user.nickname,   
            "userId": user.userId,   
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
        
        target = post[0] if isinstance(post, list) and len(post) > 0 else post
        
        db_author = None
        author_field = target.get('author')

        # 케이스 1: author 필드가 리스트인 경우 (유저님의 현재 상황)
        if isinstance(author_field, list) and len(author_field) > 0:
            db_author = author_field[0].get('nickname')
        # 케이스 2: author 필드가 딕셔너리인 경우
        elif isinstance(author_field, dict):
            db_author = author_field.get('nickname')
        # 케이스 3: author 필드가 그냥 문자열인 경우
        elif isinstance(author_field, str):
            db_author = author_field
        # 케이스 4: 최상위에 nickname이 있는 경우
        else:
            db_author = target.get('nickname')

        # # [최종 확인 디버깅]
        # print(f"--- [최종 확인] ---")
        # print(f"추출된 작성자 닉네임: [{db_author}]")
        # print(f"현재 로그인 유저 닉네임: [{user.nickname}]")
        # print(f"결과: {db_author == user.nickname}")
        # print(f"------------------")

        # 2. [핵심 보안] 권한 체크 (내 글이 아니면 403 Forbidden)
        if db_author != user.nickname:
            raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
        
        # 3. 업데이트 수행
        update_data = {
            "title": request.title,
            "content": request.content,
            "image_url": request.image
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
        
        # [핵심] 리스트/딕셔너리 구조에서 닉네임만 쏙 뽑아내기
        target = post[0] if isinstance(post, list) and len(post) > 0 else post
        
        author_field = target.get('author')
        if isinstance(author_field, list) and len(author_field) > 0:
            db_author = author_field[0].get('nickname')
        elif isinstance(author_field, dict):
            db_author = author_field.get('nickname')
        else:
            db_author = author_field if isinstance(author_field, str) else target.get('nickname')

        # # [디버깅 로그] 터미널에서 확인용
        # print(f"--- [삭제 권한 확인] ---")
        # print(f"DB 작성자: [{db_author}]")
        # print(f"로그인 유저: [{user.nickname}]")
        # print(f"----------------------")

        # 2. 권한 체크 (내 글이 아니면 403)
        if db_author != user.nickname:
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
    
    @staticmethod
    async def upload_image(image: UploadFile):
        try:
            # 1. 파일을 서버에 저장하고 상대 경로를 받음
            saved_path = await FileService.save_file(image) 
            
            # 2. 성공 응답 반환
            return BaseResponse(
                message="IMAGE_UPLOAD_SUCCESS",
                data={"imagePath": saved_path}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))