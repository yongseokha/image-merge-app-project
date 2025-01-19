"""
에러 처리 및 로깅 모듈

주요 기능:
1. 로깅 시스템 초기화 및 관리
   - 파일 로깅
   - 콘솔 로깅
   - 로그 레벨 관리
2. 에러/경고/정보 메시지 처리
   - 로그 기록
   - 사용자 알림
3. 전역 예외 처리
   - 데코레이터 제공
   - 주요 예외 타입별 처리
4. 설정 유효성 검증
   - 필수 키 검증
   - 옵션값 검증

사용 예시:
1. 로깅:
   ErrorHandler.log_error("에러 메시지")
   ErrorHandler.log_warning("경고 메시지")
   ErrorHandler.log_info("정보 메시지")

2. 사용자 알림:
   ErrorHandler.show_error("제목", "에러 내용")
   ErrorHandler.show_warning("제목", "경고 내용")
   ErrorHandler.show_info("제목", "알림 내용")

3. 예외 처리:
   @ErrorHandler.handle_error
   def some_function():
       # 함수 내용
"""

from functools import wraps
import logging
import os
import tkinter.messagebox as messagebox
from typing import Callable, Any, Dict
import PIL
from PIL.Image import UnidentifiedImageError
from constants import LOGS_DIR, LOG_FILE, DEFAULT_CONFIG

class ErrorHandler:
    """
    에러 처리 및 로깅 관리 클래스
    
    주요 기능:
    1. 로깅 시스템 관리
       - 파일 로깅
       - 콘솔 로깅
       - 로그 레벨 관리
    2. 예외 처리
       - 전역 예외 처리 데코레이터 제공
       - 주요 예외 타입별 처리
    3. 사용자 알림
       - 에러/경고/정보 메시지 표시
       - 로그 기록과 연동
    
    클래스 변수:
    - logger: 로깅 인스턴스 (None으로 초기화)
    """
    
    logger = None

    @staticmethod
    def handle_error(func: Callable) -> Callable:
        """
        전역 예외 처리 데코레이터
        
        처리하는 예외:
        1. FileNotFoundError
           - 파일 또는 디렉토리 없음
           - 사용자에게 파일 경로 확인 요청
        2. PermissionError
           - 파일 접근 권한 부족
           - 관리자 권한 실행 또는 권한 수정 필요
        3. ValueError
           - 잘못된 입력값 또는 설정값
           - 유효한 값 범위 안내
        4. UnidentifiedImageError
           - 지원하지 않는 이미지 형식
           - 지원 형식 목록 안내
        5. MemoryError
           - 이미지 처리 중 메모리 부족
           - 더 작은 이미지 사용 권장
        6. PIL.Image.DecompressionBombError
           - 너무 큰 이미지 파일
           - 크기 제한 안내
        7. 기타 예외
           - 예상치 못한 오류
           - 상세 오류 메시지 기록
        
        동작 방식:
        1. 원본 함수 실행 시도
        2. 예외 발생 시 해당 타입에 맞는 처리
        3. 오류 메시지 표시 및 로깅
        
        Args:
            func: 데코레이트할 함수
            
        Returns:
            wrapper: 예외 처리가 추가된 함수
        """
        @wraps(func)  # 원본 함수의 메타데이터 보존
        def wrapper(*args, **kwargs) -> Any:
            """
            예외 처리가 추가된 래퍼 함수
            
            처리 순서:
            1. 원본 함수 실행 시도
            2. 예외 발생 시 타입별 처리:
               - FileNotFoundError: 파일 관련 오류
               - PermissionError: 권한 관련 오류
               - ValueError: 값 검증 오류
               - UnidentifiedImageError: 이미지 형식 오류
               - MemoryError: 메모리 부족 오류
               - DecompressionBombError: 이미지 크기 초과
               - 기타 예외: 예상치 못한 오류
            3. 오류 발생 시 None 반환
            
            Args:
                *args: 원본 함수에 전달할 위치 인자
                **kwargs: 원본 함수에 전달할 키워드 인자
                
            Returns:
                Any: 원본 함수의 반환값 또는 오류 시 None
            """
            try:
                return func(*args, **kwargs)  # 원본 함수 실행
            except FileNotFoundError as e:  # 파일 없음 에러
                ErrorHandler.show_error("파일 오류", f"파일을 찾을 수 없습니다: {str(e)}")
            except PermissionError as e:  # 권한 부족 에러
                ErrorHandler.show_error("권한 오류", f"파일 접근 권한이 없습니다: {str(e)}")
            except ValueError as e:  # 잘못된 값 에러
                ErrorHandler.show_error("입력 오류", f"잘못된 값이 입력되었습니다: {str(e)}")
            except UnidentifiedImageError as e:  # 이미지 형식 에러
                ErrorHandler.show_error("이미지 오류", f"지원하지 않는 이미지 형식입니다: {str(e)}")
            except MemoryError as e:  # 메모리 부족 에러
                ErrorHandler.show_error("메모리 오류", "메모리가 부족합니다. 더 작은 이미지로 시도해주세요.")
            except PIL.Image.DecompressionBombError as e:  # 이미지 크기 초과 에러
                ErrorHandler.show_error("이미지 오류", "이미지가 너무 큽니다. 더 작은 이미지를 사용해주세요.")
            except Exception as e:  # 기타 예상치 못한 에러
                ErrorHandler.show_error("오류", f"예상치 못한 오류가 발생했습니다: {str(e)}")
            return None  # 에러 발생 시 None 반환
        return wrapper  # 래퍼 함수 반환

    # 1. 로깅 관련 메서드
    @classmethod
    def setup_logging(cls):
        """
        로깅 시스템 초기화
        
        처리 순서:
        1. 로그 디렉토리 생성
           - LOGS_DIR 경로 확인
           - 없으면 새로 생성
        
        2. 로깅 설정
           - 로그 레벨: INFO
           - 출력 포맷: 시간 - 모듈명 - 로그레벨 - 메시지
           - 인코딩: UTF-8
        
        3. 핸들러 설정
           - 파일 핸들러: 로그를 파일에 저장
           - 스트림 핸들러: 콘솔에 출력
        
        로그 파일 위치:
        - {LOGS_DIR}/app.log
        
        로그 포맷:
        - 예시: "2024-01-01 12:00:00 - error_handler - INFO - 로그 메시지"
           - 클래스 변수 logger에 저장
        """
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)

    @classmethod
    def _ensure_logger(cls):
        """
        로거 초기화 상태 확인
        
        처리 순서:
        1. 클래스 로거 존재 여부 확인
        2. 로거가 None이면 setup_logging() 호출
        """
        if not cls.logger:
            cls.setup_logging()

    @classmethod
    def log_error(cls, message: str) -> None:
        """
        에러 수준 로그 기록
        
        처리 순서:
        1. 로거 초기화 확인
        2. ERROR 레벨로 메시지 기록
           - 파일에 저장
           - 콘솔에 출력
        
        Args:
            message: 로깅할 에러 메시지
        """
        cls._ensure_logger()
        cls.logger.error(message)
        
    @classmethod
    def log_warning(cls, message: str) -> None:
        """
        경고 수준 로그 기록
        
        처리 순서:
        1. 로거 초기화 확인
        2. WARNING 레벨로 메시지 기록
           - 파일에 저장
           - 콘솔에 출력
        
        Args:
            message: 로깅할 경고 메시지
        """
        cls._ensure_logger()
        cls.logger.warning(message)
        
    @classmethod
    def log_info(cls, message: str) -> None:
        """
        정보 수준 로그 기록
        
        처리 순서:
        1. 로거 초기화 확인
        2. INFO 레벨로 메시지 기록
           - 파일에 저장
           - 콘솔에 출력
        
        Args:
            message: 로깅할 정보 메시지
        """
        cls._ensure_logger()
        cls.logger.info(message)

    # 2. 사용자 알림 메서드
    @classmethod
    def show_error(cls, title: str, message: str) -> None:
        """
        에러 메시지 표시 및 로깅
        
        처리 순서:
        1. 에러 메시지 로깅 (ERROR 레벨)
        2. 에러 메시지 박스 표시
           - 아이콘: 빨간색 X
           - 제목: title 매개변수
           - 내용: message 매개변수
        
        Args:
            title: 메시지 박스의 제목
            message: 표시할 에러 메시지
        """
        cls.log_error(message)
        messagebox.showerror(title, message)

    @classmethod
    def show_warning(cls, title: str, message: str) -> None:
        """
        경고 메시지 표시 및 로깅
        
        처리 순서:
        1. 경고 메시지 로깅 (WARNING 레벨)
        2. 경고 메시지 박스 표시
           - 아이콘: 노란색 느낌표
           - 제목: title 매개변수
           - 내용: message 매개변수
        
        Args:
            title: 메시지 박스의 제목
            message: 표시할 경고 메시지
        """
        cls.log_warning(message)
        messagebox.showwarning(title, message)

    @classmethod
    def show_info(cls, title: str, message: str) -> None:
        """
        정보 메시지 표시 및 로깅
        
        처리 순서:
        1. 정보 메시지 로깅 (INFO 레벨)
        2. 정보 메시지 박스 표시
           - 아이콘: 파란색 i
           - 제목: title 매개변수
           - 내용: message 매개변수
        
        Args:
            title: 메시지 박스의 제목
            message: 표시할 정보 메시지
        """
        cls.log_info(message)
        messagebox.showinfo(title, message)

    # 설정 검증 관련 메서드
    @classmethod
    def validate_required_keys(cls, config: Dict[str, Any], required_keys: set) -> None:
        """
        필수 키 존재 여부 검증
        
        처리 순서:
        1. 설정 딕셔너리의 키 집합 생성
        2. 필수 키 집합과 비교하여 누락된 키 확인
        3. 누락된 키가 있으면 ValueError 발생
        
        Args:
            config: 검증할 설정 딕셔너리
            required_keys: 필수 키 집합
        
        Raises:
            ValueError: 필수 키가 누락된 경우
                메시지: "필수 설정이 누락되었습니다: {누락된 키 목록}"
        """
        missing_keys = required_keys - set(config.keys())
        if missing_keys:
            raise ValueError(f"필수 설정이 누락되었습니다: {missing_keys}")

    @classmethod
    def validate_option(cls, value: str, valid_options: set[str], option_name: str) -> None:
        """
        설정값 유효성 검증
        
        처리 순서:
        1. 주어진 값이 유효한 옵션 집합에 포함되는지 확인
        2. 포함되지 않으면 ValueError 발생
        
        검증 대상:
        1. width: WIDTH_OPTIONS 중 하나
           - "원본유지", "1024", "800", "640"
        2. space: SPACE_OPTIONS 중 하나
           - "없음", "좁게", "보통", "넓게"
        3. format: FORMAT_OPTIONS 중 하나
           - "PNG", "JPG"
        4. align: ALIGN_OPTIONS 중 하나
           - "수직", "수평"
        
        Args:
            value: 검증할 값
            valid_options: 허용된 옵션들의 집합
            option_name: 옵션 이름 (에러 메시지용)
        
        Raises:
            ValueError: 값이 허용된 옵션에 없을 때 발생
                메시지 형식: "잘못된 {option_name} 값: {value}"
        """
        if value not in valid_options:
            raise ValueError(f"잘못된 {option_name} 값: {value}")

    @classmethod
    def handle_invalid_config(cls) -> dict:
        """
        잘못된 설정 파일 처리
        
        처리 순서:
        1. 경고 메시지 로깅
           - 로그 레벨: WARNING
           - 메시지: "설정 파일이 잘못되었습니다"
        2. 사용자에게 경고 메시지 표시
           - 제목: "설정 오류"
           - 내용: "설정 파일이 잘못되었습니다. 기본 설정을 사용합니다."
        3. 기본 설정값 복사 및 반환
        
        Returns:
            dict: 기본 설정값
                DEFAULT_CONFIG의 복사본
        """
        cls.show_warning(
            "설정 오류",
            "설정 파일이 잘못되었습니다. 기본 설정을 사용합니다."
        )
        
        return DEFAULT_CONFIG.copy()
