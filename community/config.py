# community/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# 모든 컨트롤러와 메인이 참조할 공통 주소
BASE_URL = os.getenv("BACKEND_URL", "http://dlwnsdud.duckdns.org")
