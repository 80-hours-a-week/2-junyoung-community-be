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

community/
├── main.py           # 애플리케이션 진입점 및 예외 처리기
├── utils.py          # 공통 응답 포장(WrappedAPIRoute) 등 유틸리티
├── routes/           # API 엔드포인트 정의 (Post, Auth)
├── controllers/      # 비즈니스 로직 처리
└── models/           # 데이터 관리 및 스키마 (Memory DB 사용)