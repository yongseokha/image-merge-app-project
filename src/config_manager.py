"""
설정 관리 모듈

주요 기능:
1. 설정 파일 생성/로드/저장
2. 설정값 유효성 검증
3. 기본 설정 관리

설정 파일 형식: JSON
설정 저장 위치: CONFIG_FILE (constants.py에서 정의)

설정 항목:
- width: 이미지 너비 ('원본유지' 또는 픽셀값)
- space: 이미지 간격 ('없음', '좁게', '보통', '넓게')
- format: 저장 포맷 ('PNG' 또는 'JPG')
- align: 정렬 방향 ('수직' 또는 '수평')
- last_opened_dir: 마지막으로 열었던 디렉토리
- result_opened_dir: 결과물 저장 디렉토리
"""

import json
import logging
import os
from typing import Dict, Any

from constants import (
    DEFAULT_CONFIG, 
    WIDTH_OPTIONS, 
    SPACE_OPTIONS, 
    FORMAT_OPTIONS, 
    ALIGN_OPTIONS,
    DEFAULT_PICTURES_DIR,
    CONFIG_FILE,
    CONFIG_DIR
)
from error_handler import ErrorHandler

class ConfigManager:
    """
    설정 관리 클래스
    
    주요 기능:
    1. 설정 파일 생성, 로드, 저장
    2. 설정값 유효성 검증
    3. 기본 설정 관리
    
    설정 검증 규칙:
    1. 필수 키 존재 여부 확인
    2. 옵션값 유효성 검증
       - width: WIDTH_OPTIONS 중 하나
       - space: SPACE_OPTIONS 중 하나
       - format: FORMAT_OPTIONS 중 하나
       - align: ALIGN_OPTIONS 중 하나
    3. 디렉토리 경로 유효성 검증
       - 존재하지 않는 경로는 기본값으로 대체
    """
    
    @ErrorHandler.handle_error
    def __init__(self):
        """
        설정 관리자 초기화
        
        처리 순서:
        1. 설정 디렉토리 존재 확인 및 생성
           - CONFIG_DIR 경로 확인
           - 없으면 새로 생성
        2. 기본 설정값으로 초기화
           - DEFAULT_CONFIG를 복사하여 self.config에 저장
        3. 설정 파일 존재 확인
           - CONFIG_FILE 경로 확인
           - 없으면 기본 설정 파일 생성
        
        속성:
        - config: 현재 설정값을 담은 딕셔너리
            {
                'width': str,      # 이미지 너비
                'space': str,      # 이미지 간격
                'format': str,     # 저장 포맷
                'align': str,      # 정렬 방향
                'last_opened_dir': str,  # 마지막 열기 경로
                'result_opened_dir': str # 마지막 저장 경로
            }
        """
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            
        self.config = DEFAULT_CONFIG.copy()
        
        if not os.path.exists(CONFIG_FILE):
            self._create_default_config()

    @ErrorHandler.handle_error
    def _create_default_config(self):
        """
        기본 설정 파일 생성
        
        처리 순서:
        1. CONFIG_FILE 경로에 파일 생성
        2. DEFAULT_CONFIG를 JSON 형식으로 저장
           - UTF-8 인코딩 사용
           - 한글 문자 그대로 저장 (ensure_ascii=False)
           - 들여쓰기 4칸 적용 (가독성)
        3. 생성 완료 로깅
        
        Note:
            - 파일이 이미 존재하면 덮어씀
            - 디렉토리가 없으면 에러 발생 가능
        """
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        ErrorHandler.log_info("기본 설정 파일이 생성되었습니다.")
        
    @ErrorHandler.handle_error
    def load(self) -> None:
        """
        설정 파일 로드 및 검증
        
        처리 순서:
        1. 설정 파일 존재 확인
           - CONFIG_FILE 경로 확인
        2. 파일이 있는 경우:
           - JSON 파일 읽기 (UTF-8 인코딩)
           - 설정값 유효성 검증
           - 현재 설정 업데이트
           - 로드 성공 로깅
        3. 파일이 없는 경우:
           - 경고 메시지 표시
           - 기본 설정값으로 초기화
        
        검증 내용:
        - 필수 키 존재 여부
        - 옵션값 유효성
        - 디렉토리 경로 유효성
        
        Note:
            - 설정 파일이 없거나 유효하지 않으면 기본 설정 사용
            - 모든 설정 변경 사항은 로그에 기록됨
        """
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            self._validate_config(loaded_config)
            self.config.update(loaded_config)
            ErrorHandler.log_info("설정 파일을 성공적으로 로드했습니다.")
        else:
            self.config = ErrorHandler.handle_invalid_config()

    @ErrorHandler.handle_error
    def save(self, new_config: Dict[str, Any]) -> None:
        """
        새로운 설정을 검증하고 저장
        
        처리 순서:
        1. 새 설정값 유효성 검증
           - 필수 키 존재 여부
           - 옵션값 유효성
           - 디렉토리 경로 유효성
        2. JSON 형식으로 파일 저장
           - UTF-8 인코딩 사용
           - 들여쓰기 적용 (가독성)
        3. 현재 설정 업데이트
        4. 저장 성공 로깅
        
        Args:
            new_config: 저장할 새로운 설정 딕셔너리
                {
                    'width': str,      # 이미지 너비
                    'space': str,      # 이미지 간격
                    'format': str,     # 저장 포맷
                    'align': str,      # 정렬 방향
                    'last_opened_dir': str,  # 마지막 열기 경로
                    'result_opened_dir': str # 마지막 저장 경로
                }
            
        Raises:
            ValueError: 설정값이 유효하지 않은 경우
        """
        self._validate_config(new_config)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=4, ensure_ascii=False)
        self.config = new_config.copy()
        logging.info("설정이 성공적으로 저장되었습니다.")

    @ErrorHandler.handle_error
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        설정값 유효성 검증
        
        검증 항목:
        1. 필수 키 존재 여부
           - width, space, format, align
           - last_opened_dir, result_opened_dir
        2. 옵션값 유효성
           - width: WIDTH_OPTIONS에 포함
           - space: SPACE_OPTIONS에 포함
           - format: FORMAT_OPTIONS에 포함
           - align: ALIGN_OPTIONS에 포함
        3. 디렉토리 경로 유효성
           - 존재하는 경로인지 확인
           - 없는 경로는 기본값으로 대체
        
        Args:
            config: 검증할 설정 딕셔너리
            
        Raises:
            ValueError: 필수 키가 없거나 옵션값이 유효하지 않은 경우
        """
        required_keys = {'width', 'space', 'format', 'align', 
                        'last_opened_dir', 'result_opened_dir'}
        
        # 필수 키 검증
        ErrorHandler.validate_required_keys(config, required_keys)
            
        # 값 유효성 검증
        ErrorHandler.validate_option(config['width'], set(WIDTH_OPTIONS), 'width')
        ErrorHandler.validate_option(config['space'], set(SPACE_OPTIONS), 'space')
        ErrorHandler.validate_option(config['format'], set(FORMAT_OPTIONS), 'format')
        ErrorHandler.validate_option(config['align'], set(ALIGN_OPTIONS), 'align')
            
        # 경로 유효성 검증
        self._validate_directory(config, 'last_opened_dir')
        self._validate_directory(config, 'result_opened_dir')

    @ErrorHandler.handle_error
    def _validate_directory(self, config: Dict[str, str], key: str) -> None:
        """
        디렉토리 경로 유효성 검증
        
        처리 순서:
        1. 설정된 경로 존재 확인
        2. 경로가 없는 경우:
           - 경고 메시지 로깅
           - 기본 경로(DEFAULT_PICTURES_DIR)로 대체
           - 대체 내용 로깅
        3. 경로가 있는 경우:
           - 해당 경로 유지
        
        검증 대상:
        - last_opened_dir: 마지막으로 열었던 디렉토리
        - result_opened_dir: 결과물 저장 디렉토리
        
        실패 시 동작:
        1. 경고 로그 기록
        2. 기본 경로로 자동 대체
        3. 설정 파일 자동 업데이트
        
        Args:
            config: 설정 딕셔너리
            key: 검사할 디렉토리 경로 키
                'last_opened_dir' 또는 'result_opened_dir'
        """
        path = config[key]
        if not os.path.exists(path):
            ErrorHandler.log_warning(f"경로가 존재하지 않습니다 ({key}): {path}")
            ErrorHandler.log_info(f"기본 경로로 대체합니다: {DEFAULT_PICTURES_DIR}")
            config[key] = DEFAULT_PICTURES_DIR
        
    @classmethod
    def validate_option(cls, value: str, valid_options: set[str], option_name: str) -> None:
        """
        설정값 유효성 검증
        
        검증 내용:
        1. 입력값이 허용된 옵션 집합에 포함되는지 확인
        2. 포함되지 않으면 ValueError 발생
        
        Args:
            value: 검증할 값
            valid_options: 허용된 옵션들의 집합
            option_name: 옵션 이름 (에러 메시지용)
            
        Raises:
            ValueError: 값이 허용된 옵션에 없을 때 발생
        """
        if value not in valid_options:
            raise ValueError(f"유효하지 않은 {option_name} 값입니다: {value}")
        