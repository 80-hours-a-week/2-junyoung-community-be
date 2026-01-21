# 2-junyoung-community-be
AWS AI School 2기 이준영

커뮤니티 서비스 백엔드 프로젝트입니다.
FastAPI를 기반으로 하며, 확장성을 고려한 계층형 아키텍처(Routes-Controllers-Models)로 설계되었습니다.

## Tech Stack
* **Language:** Python 3.13+
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Architecture:** Layered Architecture (Controller, Model, Route, Utils 분리)
* **Security:** Bcrypt Hashing, Session-based Auth

## 📂 Project Structure

```text
2-junyoung-community-be/
├── community/                # 메인 패키지 루트
│   ├── controllers/          # 비즈니스 로직 및 흐름 제어
│   │   ├── auth_controller.py
│   │   ├── comment_controller.py
│   │   ├── like_controller.py
│   │   ├── post_controller.py
│   │   └── user_controller.py
│   ├── models/               # 데이터 접근 로직
│   │   ├── comment_model.py
│   │   ├── like_model.py
│   │   ├── post_model.py
│   │   └── user_model.py
│   ├── routes/               # API 엔드포인트 및 라우팅 설정
│   │   ├── auth_route.py
│   │   ├── comment_route.py
│   │   ├── like_route.py
│   │   ├── post_route.py
│   │   └── user_route.py
│   ├── main.py               # 앱 진입점, 예외 처리, 미들웨어 설정
│   ├── security.py           # 비밀번호 암호화(Hashing) 유틸리티
│   └── utils.py              # 공통 Pydantic 스키마 및 의존성 함수
├── .gitignore                # Git 제외 설정
├── pyproject.toml            # 프로젝트 의존성 관리
└── README.md                 # 프로젝트 문서