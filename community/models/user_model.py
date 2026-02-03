# models/user_model.py
import uuid # 세션 ID 생성을 위한 라이브러리
from security import SecurityUtils
from sqlalchemy import text
from database import engine, execute_query
from datetime import datetime, timedelta

# 회원 정보를 담을 리스트 (메모리에 저장되므로 서버 재시작 시 초기화됨)
# users_db = [
#     {
#         "userId": 1,
#         "email": "jylee0005@gmail.com",
#         # "password": "$2b$12$cTUCcDU65EhBkjQ5zp1d6evJK5WYr6kDupoT0wwcWIQ04uXU7mEby", #password", 
#         "password": "$2b$12$g1GwgFvaEwhjn8uRO5HWKexCKw3KaLLBO6Wi6E/FV1XtGO47GtHn2", # dlwnsdud
#         "nickname": "관리자",
#         "profileImage": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png",
#         "status": "active"      # 정상 계정
#     },
#     {
#         "userId": 2,
#         "email": "bad@user.com",
#         "password": "password",
#         "nickname": "badguy",
#         "profileImage": None,
#         "status": "suspended"   # [403 테스트용] 정지된 계정
#     }
# ]

# # { "세션ID": "이메일" } 형태로 저장할 세션 창고
# sessions_db = {}

class UserModel:
    @staticmethod
    def find_by_email(email: str):
        """이메일로 기존 사용자가 있는지 검색 (중복 체크용)"""
        with engine.connect() as conn:
            query = text("""
                SELECT id, email, nickname, password, profile_url, account_status, suspension_start_at 
                FROM users 
                WHERE email = :email AND deleted_at IS NULL
            """)
            result = conn.execute(query, {"email": email}).fetchone()
            
            if result:
                # 딕셔너리 형태로 변환해서 리턴
                return {
                    "userId": result.id,
                    "email": result.email,
                    "nickname": result.nickname,
                    "password": result.password, # 패스워드 체크를 위해 필요!
                    "status": result.account_status,
                    "suspensionStart": result.suspension_start_at
                }
        return None

    @staticmethod
    def find_by_nickname(nickname: str):
        """닉네임으로 기존 사용자가 있는지 검색 (중복 체크용)"""
        query = "SELECT * FROM users WHERE nickname = :nickname"
        result = execute_query(query, {"nickname": nickname})
        return result[0] if result else None
    
    @staticmethod
    def find_by_id(user_id: int):
        """userId로 사용자 검색"""
        with engine.connect() as conn:
            query = text("""
                SELECT id, email, nickname, password, profile_url, account_status, suspension_start_at 
                FROM users 
                WHERE id = :user_id AND deleted_at IS NULL
            """)
            
            result = conn.execute(query, {"user_id": user_id}).fetchone()  

            # 2. 결과값을 백엔드에서 쓰기 편한 '딕셔너리' 형태로 직접 매핑해줘
            if result:
                return {
                    "userId": result.id,
                    "email": result.email,
                    "nickname": result.nickname,
                    "password": result.password,
                    "profileImage": result.profile_url,
                    "status": result.account_status,
                }
            return None

    @staticmethod
    def save_user(user_data: dict):
        """회원가입: 사용자 정보를 리스트에 저장"""
        # 비밀번호 해싱 처리
        hashed_password = SecurityUtils.get_password_hash(user_data["password"])
        
        # 2. DB 연결 및 쿼리 실행
        with engine.connect() as conn:
            # text()를 이용해 Raw SQL 작성
            query = text("""
                INSERT INTO users (email, password, nickname, profile_url, account_status)
                VALUES (:email, :password, :nickname, :profile_url, 'active')
            """)
            
            params = {
                "email": user_data["email"],
                "password": hashed_password,
                "nickname": user_data["nickname"],
                "profile_url": user_data.get("profile_url")
            }
            
            # 3. 쿼리 실행 및 커밋
            conn.execute(query, params)
            conn.commit()  # 데이터 변경 작업이므로 반드시 커밋이 필요합니다.
            
        return True

    @staticmethod
    def update_user(user_id: int, update_data: dict):
        '''회원 정보 수정'''
        with engine.connect() as conn:
            # 1. SQL 문을 text()로 감쌉니다.
            query = text("""
                UPDATE users 
                SET nickname = :nickname, 
                    profile_url = :profile_url 
                WHERE Id = :user_id
            """)
            
            # 2. 파라미터 준비
            params = {
                "nickname": update_data.get("nickname"),
                "profile_url": update_data.get("profile_url"),
                "user_id": user_id
            }
            
            # 3. 쿼리 실행
            result = conn.execute(query, params)
            
            # 4. 데이터 변경 사항을 확정(Commit)합니다.
            conn.commit()
            
            # rowcount를 사용하여 실제 수정된 행이 있는지 확인 (성공 시 True 리턴)
            return result.rowcount > 0

    @staticmethod
    def update_password(user_id: int, new_password: str):
        '''비밀번호 변경'''
        # 1. 새 비밀번호 해싱
        hashed_pw = SecurityUtils.get_password_hash(new_password)
        
        # 2. DB 연결 및 실행
        with engine.connect() as conn:
            query = text("UPDATE users SET password = :password WHERE id = :user_id")
            params = {"password": hashed_pw, "user_id": user_id}
            
            result = conn.execute(query, params)
            conn.commit()  # 변경 사항 확정
            
            # 영향을 받은 행이 1개 이상이면 성공(True)
            return result.rowcount > 0
    
    @staticmethod
    def delete_session(session_id: str):
        """세션 ID에 해당하는 세션을 삭제합니다."""
        with engine.connect() as conn:
            # SQL 문 작성
            query = text("DELETE FROM sessions WHERE session_id = :session_id")
            
            # 쿼리 실행
            conn.execute(query, {"session_id": session_id})
            
            # 삭제 작업이므로 반드시 커밋
            conn.commit()

    @staticmethod
    def delete_user(user_id: int):
        '''회원 탈퇴'''
        with engine.connect() as conn:
            # 1. 실제 삭제 대신 deleted_at 컬럼에 현재 시간을 기록합니다.

            # 1. 유저 계정 소프트 딜리트
            query_user = text("UPDATE users SET deleted_at = NOW() WHERE id = :user_id")
            conn.execute(query_user, {"user_id": user_id})
            
            # 2. 작성한 게시글 처리 (선택: 삭제하거나 '알 수 없음'으로 변경)
            # 여기서는 게시글도 소프트 딜리트 처리합니다.
            query_posts = text("UPDATE posts SET deleted_at = NOW() WHERE user_id = :user_id")
            conn.execute(query_posts, {"user_id": user_id})
            
            # 3. 작성한 댓글 처리
            query_comments = text("UPDATE comments SET deleted_at = NOW() WHERE user_id = :user_id")
            conn.execute(query_comments, {"user_id": user_id})
            
            # 4. 좋아요 처리 (좋아요는 보통 즉시 삭제합니다)
            query_likes = text("DELETE FROM likes WHERE user_id = :user_id")
            conn.execute(query_likes, {"user_id": user_id})

            conn.commit()

    @staticmethod
    def create_session(user_id: str):
        """새로운 세션 ID를 생성하고 저장합니다."""
        session_id = str(uuid.uuid4())
        expire_time = datetime.now() + timedelta(hours=1)
    
        with engine.connect() as conn:
            query = text("""
                INSERT INTO sessions (user_id, session_id, expired_at) 
                VALUES (:user_id, :session_id, :expired_at)
            """)
            
            conn.execute(query, {
                "user_id": user_id, 
                "session_id": session_id,
                "expired_at": expire_time # 만료 시간 추가
            })
            conn.commit()
            
        return session_id
    
    @staticmethod
    def get_user_by_session(session_id: str):
        """세션 ID로 사용자 정보를 조회합니다."""
        with engine.connect() as conn:
        # 1. SQL 작성 (users와 sessions 테이블을 email로 조인)
            query = text("""
            SELECT u.* FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.session_id = :session_id
            """)
            
            # 2. 실행 및 한 줄 가져오기
            result = conn.execute(query, {"session_id": session_id}).fetchone()
            
            # 3. 결과가 있으면 매핑하여 반환
            if result:
                row = result._mapping
                # DB 컬럼명에 맞춰 결과 반환 (필요한 것 위주로)
                return {
                    "userId": row["id"],
                    "email": row["email"],
                    "nickname": row["nickname"],
                    "profileImage": row.get("profile_url") or row.get("profileImage"),
                    "status": row.get("account_status", "active")
                }
        return None
    
    @staticmethod
    def delete_session(session_id: str):
        with engine.connect() as conn:
            # 1. SQL 작성
            query = text("DELETE FROM sessions WHERE session_id = :session_id")
            
            # 2. 실행
            conn.execute(query, {"session_id": session_id})
            
            # 3. 삭제 작업 확정 (커밋)
            conn.commit()

    @staticmethod
    def is_already_logged_in(email: str):
        """[409 체크용] 이메일이 세션 저장소에 이미 있는지 확인"""
        with engine.connect() as conn:
            # 2. 이제 이 안에서는 'conn'을 사용할 수 있습니다.
            # (sessions 테이블의 컬럼명에 맞춰 query를 작성하세요)
            query = text("SELECT user_id FROM sessions WHERE user_id = (SELECT id FROM users WHERE email = :email) AND expired_at > NOW()")
            result = conn.execute(query, {"email": email}).fetchone()
            
            return True if result else False