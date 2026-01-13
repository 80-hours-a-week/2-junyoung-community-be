# models/user_model.py
import uuid # 세션 ID 생성을 위한 라이브러리

# 회원 정보를 담을 리스트 (메모리에 저장되므로 서버 재시작 시 초기화됨)
users_db = []

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
    def save_user(user_data: dict):
        """새로운 사용자를 리스트에 저장하고 발급된 ID를 반환"""
        new_id = len(users_db) + 1
        user_data["user_id"] = new_id
        users_db.append(user_data)
        return new_id
    
    @staticmethod
    def create_session(email: str):
        # 고유한 세션 ID 생성
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