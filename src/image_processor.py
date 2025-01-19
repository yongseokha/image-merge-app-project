from PIL import Image  # 이미지 처리 라이브러리
from typing import List, Dict, Any, Callable, Tuple  # 타입 힌트를 위한 모듈
import logging  # 로그 기록용 모듈
from constants import SPACING_OPTIONS  # 간격 옵션 상수 가져오기
from error_handler import ErrorHandler  # 에러 핸들링 데코레이터
import os  # 운영 체제 작업 지원 모듈
from PIL import ImageEnhance, ImageFilter  # 이미지 보정 및 필터링 관련 클래스

class ImageProcessor:
    """
    이미지 처리 클래스
    
    주요 기능:
    1. 이미지 크기 조정
    2. 이미지 병합 (수직/수평)
    3. 이미지 필터 적용
    4. 이미지 회전/반전
    
    처리 가능한 이미지 형식: PNG, JPG, JPEG
    """

    def __init__(self):
        """
        이미지 처리기 초기화
        
        속성:
        - app: 메인 애플리케이션 참조
              이미지 상태(회전/반전/필터) 접근에 사용
        """
        pass
    
    @ErrorHandler.handle_error
    def process_images(self, images, width, align, progress_callback=None):
        """
        여러 이미지를 일괄 처리
        
        처리 순서:
        1. 이미지 크기 조정
           - 원본유지(-1): 크기 변경 없음
           - 수직 정렬: 지정된 너비에 맞춤
           - 수평 정렬: 지정된 높이에 맞춤
        
        2. 리사이즈 알고리즘
           - LANCZOS 알고리즘 사용
           - 품질 손실 최소화
           - 비율 유지
        
        3. 진행률 업데이트
           - 각 이미지 처리마다 진행률 계산
           - 콜백 함수 호출
        
        Args:
            images: 처리할 이미지 목록 (PIL.Image 객체들)
            width: 목표 너비/높이 (-1: 원본 크기 유지)
            align: 정렬 방향 ('수직' 또는 '수평')
            progress_callback: 진행률 업데이트 콜백 함수
            
        Returns:
            List[PIL.Image]: 처리된 이미지 목록
        """
        # 처리된 이미지를 저장할 리스트 초기화
        processed = []
        # 총 이미지 개수 계산 (진행률용)
        total = len(images)
        
        for i, image in enumerate(images):
            if width != -1:  # 원본 크기 유지가 아닌 경우
                if align == "수평":
                    # 수평 정렬일 때는 높이 기준으로 크기 조정
                    height = width
                    ratio = height / image.size[1]  # 높이 기준 비율 계산
                    new_width = int(image.size[0] * ratio)  # 비율에 맞춘 너비 계산
                    # LANCZOS 알고리즘으로 이미지 리사이즈 (품질 유지)
                    resized = image.resize((new_width, height), Image.Resampling.LANCZOS)
                else:
                    # 수직 정렬일 때는 너비 기준으로 크기 조정
                    new_width = width
                    ratio = new_width / image.size[0]  # 너비 기준 비율 계산
                    new_height = int(image.size[1] * ratio)  # 비율에 맞춘 높이 계산
                    # LANCZOS 알고리즘으로 이미지 리사이즈 (품질 유지)
                    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                # 원본 크기 유지
                resized = image
            
            # 처리된 이미지를 목록에 추가
            processed.append(resized)
            
            # 진행률 업데이트 (콜백이 있는 경우)
            if progress_callback:
                progress = (i + 1) / total * 100
                progress_callback(progress)
        
        return processed  # 처리된 이미지 리스트 반환
    
    @ErrorHandler.handle_error
    def merge_images(self, image_paths: List[str], options: Dict[str, Any], 
                    progress_callback: Callable = None) -> Tuple[Image.Image, str]:
        """
        이미지 병합 처리
        
        처리 순서:
        1. 이미지 로드 및 전처리 (0-30% 진행)
           - 각 이미지 파일 로드
           - 회전/반전 상태 적용
           - 필터 상태 적용
           - 진행률 업데이트
        
        2. 이미지 크기 조정 (30-60% 진행)
           - 원본유지 또는 지정된 크기로 조정
           - 비율 유지하며 리사이즈
           - 진행률 업데이트
        
        3. 이미지 병합 (60-100% 진행)
           - 간격 설정 적용
           - 수직/수평 정렬에 따라 병합
           - 진행률 업데이트
        
        4. 결과 이미지 후처리
           - JPG 형식인 경우 RGB 모드로 변환
           - 최종 이미지 및 형식 반환
        
        Args:
            image_paths: 병합할 이미지 파일 경로 목록
            options: 병합 옵션 딕셔너리
                {
                    'width': str,    # 이미지 너비 ('원본유지' 또는 픽셀값)
                    'align': str,    # 정렬 방향 ('수직' 또는 '수평')
                    'space': str,    # 간격 설정 ('없음', '좁게', '보통', '넓게')
                    'format': str    # 저장 포맷 ('PNG' 또는 'JPG')
                }
            progress_callback: 진행률 업데이트 콜백 함수
                - 0-100 사이의 진행률 값을 전달받음
                - None인 경우 진행률 업데이트 안 함
        
        Returns:
            Tuple[Image.Image, str]: (병합된 이미지, 저장 포맷)
        """
        images = []
        for i, path in enumerate(image_paths):
            with Image.open(path) as img:
                # 회전/반전 상태 적용
                if path in self.app.image_control_frame.image_states:
                    transform_state = self.app.image_control_frame.image_states[path]
                    if transform_state:
                        img = self._apply_image_controls(img.copy(), transform_state.get_state())
                
                # 필터 상태 적용
                if path in self.app.filter_frame.filter_states:
                    filter_state = self.app.filter_frame.filter_states[path]
                    if filter_state:
                        img = self.apply_filters(img.copy(), filter_state.get_state())
                else:
                    img = img.copy()
                    
                if img:
                    images.append(img)
                
                # 진행률 업데이트 (30%까지)
                if progress_callback:
                    progress_callback(i / len(image_paths) * 30)

        # 이미지 목록 검증
        if not images:
            return None, None

        # 크기 조정 (30-60% 진행)
        width = -1 if options['width'] == '원본유지' else int(options['width'])
        processed = self.process_images(images, width, options['align'], 
            lambda x: progress_callback(30 + x * 0.3) if progress_callback else None)

        # 간격 설정 적용
        spacing = SPACING_OPTIONS[options['space']]

        # 이미지 병합 (60-100% 진행)
        result = self.merge_images_with_spacing(processed, spacing, options['align'],
            lambda x: progress_callback(60 + x * 0.4) if progress_callback else None)

        # JPG 포맷인 경우 RGB 모드로 변환
        img_format = options['format'].lower()
        if img_format == 'jpg':
            result = result.convert('RGB')

        return result, img_format
    
    @ErrorHandler.handle_error
    def apply_filters(self, image: Image.Image, filters: dict) -> Image.Image:
        """
        이미지에 필터 효과를 적용
        
        처리 순서:
        1. 원본 이미지 복사본 생성
        2. 필터 설정값 검증 및 변환
           - ImageFilterState 객체인 경우 딕셔너리로 변환
        3. 필터 순차 적용
           - 밝기 조절 (brightness)
           - 대비 조절 (contrast) 
           - 채도 조절 (saturation)
           - 포스터화 효과 (posterize)
        
        필터 종류 및 범위:
        - brightness: 밝기 조절 (0.0-3.0)
          - 1.0: 원본 밝기
          - >1.0: 밝게
          - <1.0: 어둡게
        - contrast: 대비 조절 (0.0-3.0)
          - 1.0: 원본 대비
          - >1.0: 대비 증가
          - <1.0: 대비 감소
        - saturation: 채도 조절 (0.0-3.0)
          - 1.0: 원본 채도
          - >1.0: 채도 증가
          - <1.0: 채도 감소
        - posterize: 포스터화 효과 (1.0-3.0)
          - 1.0: 효과 없음
          - >1.0: 색상 수 감소 (값이 클수록 강한 효과)
        
        Args:
            image: 필터를 적용할 원본 이미지
            filters: 필터 설정값을 담은 딕셔너리 또는 ImageFilterState 객체
        
        Returns:
            필터가 적용된 이미지
        """
        # 원본 이미지 복사본 생성
        filtered = image.copy()
        
        # ImageFilterState 객체를 딕셔너리로 변환
        if isinstance(filters, ImageFilterState):
            filters = filters.get_state()
        
        # 밝기 조절 필터 적용
        if 'brightness' in filters:
            enhancer = ImageEnhance.Brightness(filtered)
            filtered = enhancer.enhance(filters['brightness'])
        
        # 대비 조절 필터 적용
        if 'contrast' in filters:
            enhancer = ImageEnhance.Contrast(filtered)
            filtered = enhancer.enhance(filters['contrast'])
        
        # 채도 조절 필터 적용
        if 'saturation' in filters:
            enhancer = ImageEnhance.Color(filtered)
            filtered = enhancer.enhance(filters['saturation'])
        
        # 포스터화 효과 적용
        if 'posterize' in filters:
            value = filters['posterize']
            if value > 1.0:
                # 색상 수 계산 (값이 클수록 색상 수 감소)
                colors = int(256 / (1 + (value - 1.0) * 3))
                # 색상 수 범위 제한 (2-256)
                colors = max(2, min(256, colors))
                # 팔레트 모드로 변환하여 포스터화 적용
                filtered = filtered.convert('P', palette=Image.Palette.ADAPTIVE, colors=colors)
                # RGB 모드로 다시 변환
                filtered = filtered.convert('RGB')
        
        return filtered
    
    @ErrorHandler.handle_error
    def merge_images_with_spacing(self, images: List[Image.Image], spacing: int, align: str, progress_callback=None) -> Image.Image:
        """
        여러 이미지를 지정된 간격으로 병합
        
        처리 과정:
        1. 정렬 방향에 따른 최종 크기 계산
           - 수직: 최대 너비, 높이의 합
           - 수평: 너비의 합, 최대 높이
        2. 새 이미지 캔버스 생성 (흰색 배경)
        3. 각 이미지를 순서대로 배치
           - 수직: y 좌표 증가
           - 수평: x 좌표 증가
        4. 진행률 업데이트
        
        Args:
            images: 병합할 이미지 목록
            spacing: 이미지 간 간격 (픽셀)
            align: 정렬 방향 ('수직' 또는 '수평')
            progress_callback: 진행률 업데이트 콜백 함수
            
        Returns:
            병합된 하나의 이미지
            
        Raises:
            ValueError: 병합할 이미지가 없는 경우
        """
        if not images:
            raise ValueError("병합할 이미지가 없습니다.")
        
        if align == "수직":
            # 세로 정렬 시 필요한 크기 계산
            max_width = max(img.size[0] for img in images)  # 가장 큰 너비 찾기
            # 모든 이미지의 높이 합과 간격 계산
            total_height = sum(img.size[1] for img in images) + spacing * (len(images) - 1)
            # 흰색 배경의 새 이미지 생성
            result = Image.new("RGB", (max_width, total_height), "white")
            y_offset = 0  # 세로 위치 초기화
            
            # 각 이미지를 세로로 배치
            for i, img in enumerate(images):
                # 현재 y 위치에 이미지 붙이기
                result.paste(img, (0, y_offset))
                # 다음 이미지의 y 위치 계산 (현재 이미지 높이 + 간격)
                y_offset += img.size[1] + spacing
                
                # 진행률 업데이트
                if progress_callback:
                    progress = (i + 1) / len(images) * 100
                    progress_callback(progress)
        else:  # 수평 정렬
            # 가로 정렬 시 필요한 크기 계산
            total_width = sum(img.size[0] for img in images) + spacing * (len(images) - 1)
            max_height = max(img.size[1] for img in images)  # 가장 큰 높이 찾기
            # 흰색 배경의 새 이미지 생성
            result = Image.new("RGB", (total_width, max_height), "white")
            x_offset = 0  # 가로 위치 초기화
            
            # 각 이미지를 가로로 배치
            for i, img in enumerate(images):
                # 현재 x 위치에 이미지 붙이기
                result.paste(img, (x_offset, 0))
                # 다음 이미지의 x 위치 계산 (현재 이미지 너비 + 간격)
                x_offset += img.size[0] + spacing
                
                # 진행률 업데이트
                if progress_callback:
                    progress = (i + 1) / len(images) * 100
                    progress_callback(progress)
        
        return result
    
    @ErrorHandler.handle_error
    def _apply_image_controls(self, img: Image.Image, state: dict) -> Image.Image:
        """
        이미지에 회전과 반전을 적용
        
        처리 순서:
        1. 회전 적용
           - rotation 값이 있으면 해당 각도로 회전
           - expand=True로 설정하여 이미지 잘림 방지
           - 회전 순서: 반전 전에 회전 적용
        
        2. 반전 적용
           - flipped가 True이면 좌우 반전
           - Image.Transpose.FLIP_LEFT_RIGHT 사용
           - 회전 후 반전 적용
        
        Args:
            img: 원본 이미지 (PIL.Image 객체)
            state: 변형 상태 딕셔너리
                {
                    'rotation': int,  # 회전 각도 (0, 90, 180, 270)
                    'flipped': bool   # 좌우 반전 여부
                }
        
        Returns:
            Image.Image: 변형이 적용된 이미지
        """
        if state.get('rotation'):
            img = img.rotate(state['rotation'], expand=True)
        if state.get('flipped'):
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return img

class ImageTransformState:
    """
    이미지 변형(회전/반전) 상태 관리 클래스
    
    관리하는 상태:
    1. rotation: 회전 각도 (0-359)
    2. flipped: 좌우 반전 여부 (True/False)
    3. modified: 상태 변경 여부 (True/False)
    
    주요 메서드:
    - set_rotation(angle): 회전 각도 설정
    - add_rotation(angle): 현재 각도에 추가 회전
    - toggle_flip(): 좌우 반전 토글
    - reset(): 상태 초기화
    """
    
    def __init__(self):
        """
        이미지 변형 상태 초기화
        
        속성:
        - rotation: 회전 각도 (0-359)
        - flipped: 좌우 반전 여부 (True/False)
        - modified: 상태 변경 여부 (True/False)
        
        초기값:
        - rotation = 0 (회전 없음)
        - flipped = False (반전 없음)
        - modified = False (변경 없음)
        """
        self.rotation = 0
        self.flipped = False
        self.modified = False
    
    def set_rotation(self, angle: int) -> None:
        """
        회전 각도 설정
        
        Args:
            angle: 설정할 회전 각도 (0-359)
            
        """
        self.rotation = angle % 360
        self.modified = True
    
    def add_rotation(self, angle: int) -> None:
        """
        현재 회전 각도에 추가 회전
        
        Args:
            angle: 추가할 회전 각도 (양수: 시계방향, 음수: 반시계방향)
        """
        self.rotation = (self.rotation + angle) % 360
        self.modified = True
    
    def toggle_flip(self) -> None:
        """
        좌우 반전 상태 토글
        
        현재 상태의 반대로 설정 (True->False 또는 False->True)
        """
        self.flipped = not self.flipped
        self.modified = True
    
    def reset(self) -> None:
        """
        상태 초기화
        
        초기화 내용:
        - rotation: 0도로 설정
        - flipped: False로 설정
        - modified: False로 설정
        """
        self.rotation = 0
        self.flipped = False
        self.modified = False
    
    def is_default(self) -> bool:
        """
        기본 상태 여부 확인
        
        Returns:
            bool: 회전과 반전이 모두 기본값이면 True
        """
        return self.rotation == 0 and not self.flipped
    
    def get_state(self) -> dict:
        """
        현재 상태 반환
        
        Returns:
            dict: 현재 회전/반전 상태
                {
                    'rotation': int,  # 현재 회전 각도 (0-359)
                    'flipped': bool   # 현재 반전 상태
                }
        """
        return {
            'rotation': self.rotation,
            'flipped': self.flipped
        }

class ImageFilterState:
    """
    이미지 필터 상태 관리 클래스
    
    관리하는 필터:
    - brightness: 밝기
    - contrast: 대비
    - saturation: 채도
    - posterize: 포스터화
    """
    
    def __init__(self):
        """
        이미지 필터 상태 초기화
        
        속성:
        - filters: 필터 설정값을 담은 딕셔너리
            {
                'brightness': float,  # 밝기 (기본값: 1.0)
                'contrast': float,    # 대비 (기본값: 1.0)
                'saturation': float,  # 채도 (기본값: 1.0)
                'posterize': float    # 포스터화 (기본값: 1.0)
            }
        - modified: 상태 변경 여부 (True/False)
        
        Note:
            - 모든 필터값의 기본값은 1.0 (원본 상태)
            - 0.0 ~ 3.0 사이의 값을 가질 수 있음
            - modified는 필터값이 변경될 때 True로 설정됨
        """
        self.filters = {
            'brightness': 1.0,
            'contrast': 1.0,
            'saturation': 1.0,
            'posterize': 1.0
        }
        self.modified = False
    
    def set_filter(self, filter_name: str, value: float) -> None:
        """
        필터 값 설정
        
        Args:
            filter_name: 필터 이름 (brightness/contrast/saturation/posterize)
            value: 필터 값 (0.0 ~ 3.0)
        """
        if filter_name in self.filters:
            self.filters[filter_name] = value
            self.modified = True
    
    def reset(self) -> None:
        """
        필터 초기화
        
        초기화 내용:
        - 모든 필터값을 1.0(기본값)으로 설정
        - modified 플래그를 False로 설정
        
        필터 목록:
        - brightness: 밝기
        - contrast: 대비
        - saturation: 채도
        - posterize: 포스터화
        """
        self.filters = {
            'brightness': 1.0,
            'contrast': 1.0,
            'saturation': 1.0,
            'posterize': 1.0
        }
        self.modified = False
    
    def is_default(self) -> bool:
        """
        기본 상태 여부 확인
        
        Returns:
            bool: 모든 필터가 기본값(1.0)이면 True
        """
        return all(abs(v - 1.0) < 0.01 for v in self.filters.values())
    
    def get_state(self) -> dict:
        """
        현재 필터 상태 반환
        
        Returns:
            dict: 현재 필터 설정값
                {
                    'brightness': float,  # 밝기 (0.0-3.0)
                    'contrast': float,    # 대비 (0.0-3.0)
                    'saturation': float,  # 채도 (0.0-3.0)
                    'posterize': float    # 포스터화 (1.0-3.0)
                }
        """
        return {
            'brightness': self.filters['brightness'],
            'contrast': self.filters['contrast'],
            'saturation': self.filters['saturation'],
            'posterize': self.filters['posterize']
        }