"""
프로그램 전역 상수 정의 모듈

주요 구성:
1. 경로 관련 상수
   - 프로그램 실행에 필요한 기본 디렉토리 경로
   - 설정 및 로그 파일 경로
2. UI 관련 상수
   - 윈도우 크기, 여백 등 UI 기본값
3. 이미지 처리 관련 상수
   - 지원하는 이미지 형식
   - 이미지 간격 옵션
4. 기본 설정값
   - 프로그램 초기 실행시 사용되는 설정
5. UI 옵션값
   - 콤보박스 등에서 사용되는 선택 옵션
"""

import os

# === 경로 관련 상수 ===
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # 프로젝트 루트 디렉토리
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')         # 설정 파일 디렉토리
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')            # 로그 파일 디렉토리
DEFAULT_PICTURES_DIR = os.path.expanduser("~/Pictures")  # 기본 사진 디렉토리

# === 파일 경로 상수 ===
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')  # 설정 파일 경로
LOG_FILE = os.path.join(LOGS_DIR, 'app.log')          # 로그 파일 경로

# === UI 관련 상수 ===
WINDOW_SIZE = (1500, 900)  # 메인 윈도우 크기 (너비, 높이)
DEFAULT_PADDING = 5        # UI 요소 간 기본 여백 (픽셀)

# === 이미지 처리 관련 상수 ===
# 지원하는 이미지 파일 확장자
SUPPORTED_FORMATS = (
    '.png',   # PNG 형식 (투명도 지원)
    '.jpg',   # JPG 형식 (높은 압축률)
    '.jpeg'   # JPEG 형식 (JPG와 동일)
)

# 이미지 간격 옵션 (픽셀 단위)
SPACING_OPTIONS = {
    "없음": 0,    # 이미지 간 간격 없음
    "좁게": 30,   # 최소 간격 (30px)
    "보통": 60,   # 중간 간격 (60px)
    "넓게": 90    # 최대 간격 (90px)
}

# === 기본 설정값 ===
DEFAULT_CONFIG = {
    "width": "원본유지",    # 이미지 너비 설정 (원본 크기 유지)
    "space": "없음",       # 이미지 간격 설정 (간격 없음)
    "format": "PNG",      # 저장 포맷 (PNG 형식)
    "align": "수직",       # 이미지 정렬 방향 (세로 방향)
    "last_opened_dir": DEFAULT_PICTURES_DIR,    # 마지막으로 열었던 디렉토리
    "result_opened_dir": DEFAULT_PICTURES_DIR   # 결과물 저장 디렉토리
}

# === UI 콤보박스 옵션 ===
# 이미지 너비 옵션 (픽셀 단위, "원본유지"는 크기 변경 없음)
WIDTH_OPTIONS = [
    "원본유지",  # 원본 크기 유지
    "1024",    # 너비 1024px
    "800",     # 너비 800px
    "640"      # 너비 640px
]

# 이미지 간격 옵션 (SPACING_OPTIONS의 키값들)
SPACE_OPTIONS = ["없음", "좁게", "보통", "넓게"]

# 저장 포맷 옵션
FORMAT_OPTIONS = [
    "PNG",     # PNG 형식 (무손실, 투명도 지원)
    "JPG"      # JPG 형식 (손실 압축, 작은 파일 크기)
]

# 이미지 정렬 방향 옵션
ALIGN_OPTIONS = [
    "수직",     # 세로 방향 정렬
    "수평"      # 가로 방향 정렬
]

# === 미리보기 관련 상수 ===
PREVIEW_WIDTH = 400    # 미리보기 영역 너비 (픽셀)
PREVIEW_HEIGHT = 300   # 미리보기 영역 높이 (픽셀)
PREVIEW_BG = 'white'   # 미리보기 배경색

# 미리보기 상태 메시지 - 상황별 안내 텍스트
PREVIEW_TEXT_NO_FILES = "이미지 파일을 추가하세요"     # 파일 목록이 비어있을 때
PREVIEW_TEXT_NO_SELECTION = "이미지를 선택하세요"      # 파일은 있지만 선택되지 않았을 때
PREVIEW_TEXT_MULTI_SELECTION = "하나의 파일만 선택하세요"  # 여러 파일이 선택되었을 때
