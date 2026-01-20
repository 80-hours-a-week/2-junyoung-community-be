# models/user_model.py
import uuid # 세션 ID 생성을 위한 라이브러리
from security import SecurityUtils

# 회원 정보를 담을 리스트 (메모리에 저장되므로 서버 재시작 시 초기화됨)
users_db = [
    {
        "userId": 1,
        "email": "test@startupcode.kr",
        "password": "$2b$12$cTUCcDU65EhBkjQ5zp1d6evJK5WYr6kDupoT0wwcWIQ04uXU7mEby", #password", 
        "nickname": "startup",
        "profileImage": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png",
        "status": "active"      # 정상 계정
    },
    {
        "userId": 2,
        "email": "bad@user.com",
        "password": "password",
        "nickname": "badguy",
        "profileImage": None,
        "status": "suspended"   # [403 테스트용] 정지된 계정
    }
]

# { "세션ID": "이메일" } 형태로 저장할 세션 창고
sessions_db = {}

class UserModel:
    @staticmethod
    def find_by_email(email: str):
        """이메일로 기존 사용자가 있는지 검색 (중복 체크용)"""
        return next((user for user in users_db if user["email"] == email), None)

    @staticmethod
    def find_by_nickname(nickname: str):
        """닉네임으로 기존 사용자가 있는지 검색 (중복 체크용)"""
        return next((user for user in users_db if user["nickname"] == nickname), None)

    @staticmethod
    def find_by_id(userId: int):
        """userId로 사용자 검색"""
        return next((user for user in users_db if user["userId"] == userId), None)

    @staticmethod
    def save_user(user_data: dict):
        """회원가입: 사용자 정보를 리스트에 저장"""
        # 1. 새로운 ID 생성 (현재 개수 + 1)
        new_id = len(users_db) + 1
        
        # 2. 데이터 보정 (userId, status 추가)
        user_data["userId"] = new_id
        user_data["status"] = "active" # 기본 상태는 '활동 중'
        
        # 비밀번호 해싱
        user_data["password"] = SecurityUtils.get_password_hash(user_data["password"])

        # 3. DB(리스트)에 저장
        users_db.append(user_data)
        
        return new_id

    @staticmethod
    def update_user(userId: int, update_data: dict):
        '''회원 정보 수정'''
        user = UserModel.find_by_id(userId)
        if user:
            user.update(update_data)
            return True
        return False

    @staticmethod
    def update_password(userId: int, new_password: str):
        '''비밀번호 변경'''
        user = UserModel.find_by_id(userId)
        if user:
            user["password"] = SecurityUtils.get_password_hash(new_password)
            return True
        return False
    
    @staticmethod
    def delete_session(session_id: str):
        """세션 ID에 해당하는 세션을 삭제합니다."""
        if session_id in sessions_db:
            del sessions_db[session_id]

    @staticmethod
    def delete_user(userId: int):
        '''회원 탈퇴'''
        global users_db, sessions_db
        
        user = UserModel.find_by_id(userId)
        if user:
            users_db.remove(user)
        
            # 관련된 세션도 모두 삭제 (강제 로그아웃)
            for session_id, email in list(sessions_db.items()):
                if email == user["email"]:
                    del sessions_db[session_id]
            return True
        return False

    @staticmethod
    def create_session(email: str):
        """새로운 세션 ID를 생성하고 저장합니다."""
        session_id = str(uuid.uuid4())
        sessions_db[session_id] = email
        return session_id
    
    @staticmethod
    def get_user_by_session(session_id: str):
        """세션 ID로 사용자 정보를 조회합니다."""
        # 1. 세션 창고(sessions_db)에서 이메일을 찾습니다.
        email = sessions_db.get(session_id)
        if not email:
            return None
        
        # 2. 찾은 이메일로 사용자 상세 정보(users_db)를 반환합니다.
        return UserModel.find_by_email(email)
    
    @staticmethod
    def is_already_logged_in(email: str):
        """[409 체크용] 이메일이 세션 저장소에 이미 있는지 확인"""
        # 딕셔너리의 값(email) 중에 찾는 email이 있는지 확인
        return email in sessions_db.values()
    
