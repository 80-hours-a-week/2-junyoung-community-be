# 2-junyoung-community-be
AWS AI School 2기 이준영

커뮤니티 서비스 백엔드 프로젝트입니다.
FastAPI를 기반으로 하며, 확장성을 고려한 계층형 아키텍처(Routes-Controllers-Models)로 설계되었습니다.

## Tech Stack
* **Language:** Python 3.13+
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Architecture:** Layered Architecture (Controller, Model, Route, Utils 분리)

## 📂 Project Structure

```text
2-junyoung-community-be/
├── community/                # 메인 패키지 루트
│   ├── controllers/          # 비즈니스 로직 및 흐름 제어
│   │   ├── auth_controller.py
│   │   └── post_controller.py
│   ├── models/               # 데이터 스토어 및 데이터 접근 로직
│   │   ├── post_model.py
│   │   └── user_model.py
│   ├── routes/               # API 엔드포인트 및 라우팅 설정
│   │   ├── auth_route.py
│   │   └── post_route.py
│   ├── main.py               # 애플리케이션 진입점 및 전역 설정
│   └── utils.py              # 공통 유틸리티 및 응답 래퍼
├── .gitignore                # Git 제외 설정
├── pyproject.toml            # 프로젝트 의존성 관리
└── README.md                 # 프로젝트 문서