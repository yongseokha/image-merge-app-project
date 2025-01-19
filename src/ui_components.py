import tkinter as tk
from tkinter import ttk, Frame, LabelFrame, Scale, Canvas, Scrollbar, Listbox, END, Button, StringVar, DoubleVar
from typing import Any, Callable, Dict, Optional
from PIL import ImageTk
from constants import (
    DEFAULT_PADDING, WIDTH_OPTIONS, SPACE_OPTIONS,
    FORMAT_OPTIONS, ALIGN_OPTIONS,
    PREVIEW_WIDTH, PREVIEW_HEIGHT, PREVIEW_BG,
    PREVIEW_TEXT_NO_FILES, PREVIEW_TEXT_NO_SELECTION, PREVIEW_TEXT_MULTI_SELECTION
)
from error_handler import ErrorHandler
from image_processor import ImageTransformState, ImageFilterState


class PreviewFrame(LabelFrame):
    """
    이미지 미리보기 프레임
    
    주요 기능:
    1. 선택된 이미지 미리보기 표시
    2. 상황별 안내 메시지 표시
       - 파일 없음: "이미지 파일을 추가하세요"
       - 선택 없음: "이미지를 선택하세요"
       - 다중 선택: "하나의 파일만 선택하세요"
    3. 고정된 크기로 이미지 표시
    4. 이미지 비율 유지
    
    속성:
    - canvas: 이미지 표시용 캔버스
    - _image: 현재 표시 중인 이미지 객체 참조
    """
    
    def __init__(self, parent: Any, **kwargs):
        """
        미리보기 프레임 초기화
        
        Args:
            parent: 부모 위젯
            **kwargs: 추가 설정값
        """
        super().__init__(parent, text="미리보기", **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """
        미리보기 UI 구성
        
        구성 요소:
        1. 고정 크기 프레임
           - 너비: PREVIEW_WIDTH
           - 높이: PREVIEW_HEIGHT
           - 패딩: DEFAULT_PADDING
        2. 캔버스
           - 프레임과 동일한 크기
           - 배경색: PREVIEW_BG
           - 테두리 없음
        3. 기본 텍스트 표시
           - 중앙 정렬
           - 기본 폰트 사용
        """
        # 고정 크기 프레임 생성
        self.frame = ttk.Frame(self)
        self.frame.pack(padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # 캔버스 생성 및 설정
        self.canvas = tk.Canvas(
            self.frame,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            bg=PREVIEW_BG,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # 기본 텍스트 표시
        self._show_default_text(PREVIEW_TEXT_NO_FILES)
        
        # 프레임을 중앙에 배치
        self.frame.pack_configure(expand=True)

    def _show_default_text(self, message: str):
        """
        안내 메시지 표시
        
        처리 순서:
        1. 캔버스 초기화
        2. 메시지 중앙 배치
           - 가로 위치: PREVIEW_WIDTH // 2
           - 세로 위치: PREVIEW_HEIGHT // 2
           - 앵커: center
        3. 텍스트 스타일 적용
           - 폰트: Arial 12pt
           - 정렬: 중앙
        
        Args:
            message: 표시할 안내 메시지
        """
        self.canvas.delete("all")
        self.canvas.create_text(
            PREVIEW_WIDTH // 2,
            PREVIEW_HEIGHT // 2,
            text=message,
            anchor="center",
            font=("Arial", 12)
        )

    @ErrorHandler.handle_error
    def update_preview(self, image: Optional[ImageTk.PhotoImage] = None, 
                      file_count: int = 0, selection_count: int = 0):
        """
        미리보기 이미지 업데이트
        
        처리 순서:
        1. 상태 확인 및 메시지 표시
           - file_count == 0: 파일 없음 → "이미지 파일을 추가하세요"
           - selection_count == 0: 선택 없음 → "이미지를 선택하세요"
           - selection_count > 1: 다중 선택 → "하나의 파일만 선택하세요"
        2. 이미지 표시 (단일 선택된 경우)
           - 캔버스 초기화
           - 이미지 중앙 배치
           - 이미지 객체 참조 유지
        
        Args:
            image: 표시할 이미지 (PhotoImage 객체)
            file_count: 리스트의 전체 파일 수
            selection_count: 현재 선택된 파일 수
        """
        if image:
            self.canvas.delete("all")
            x = PREVIEW_WIDTH // 2
            y = PREVIEW_HEIGHT // 2
            self.canvas.create_image(x, y, image=image, anchor="center")
            self._image = image
        else:
            if file_count == 0:
                self._show_default_text(PREVIEW_TEXT_NO_FILES)
            elif selection_count == 0:
                self._show_default_text(PREVIEW_TEXT_NO_SELECTION)
            elif selection_count > 1:
                self._show_default_text(PREVIEW_TEXT_MULTI_SELECTION)


class ResultPreviewFrame(LabelFrame):
    """
    결과 미리보기 프레임
    
    기능:
    1. 병합 결과 이미지 미리보기
    2. 이미지 확대/축소 (줌)
    3. 스크롤바를 통한 이미지 탐색
    
    구성 요소:
    - 캔버스 (이미지 표시 영역)
    - 스크롤바 (가로/세로)
    - 줌 컨트롤
    
    Args:
        parent: 부모 위젯
        **kwargs: 추가 설정값
    """
    def __init__(self, parent: Any, **kwargs):
        """
        결과 미리보기 프레임 초기화
        
        구성 요소:
        1. 캔버스 (이미지 표시)
        2. 스크롤바 (가로/세로)
        3. 줌 컨트롤
        
        Args:
            parent: 부모 위젯
            **kwargs: 추가 설정값
        """
        super().__init__(parent, text="저장 결과 화면", bg="lightgray", **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """
        결과 미리보기 UI 구성
        
        구성 요소:
        1. 캔버스 (이미지 표시 영역)
           - 배경색: 흰색
           - 스크롤 가능
        2. 스크롤바
           - 가로/세로 스크롤바
           - 캔버스와 연동
        3. 줌 컨트롤
           - 범위: 0~400%
           - 기본값: 100%
        """
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        # 스크롤바 추가
        self.setup_scrollbars()
        
        # 줌 슬라이더 초기화
        self.scale_preview = Scale(
            self,
            from_=0,  # 슬라이더 최소값
            to=400,  # 슬라이더 최대값
            orient="horizontal",  # 슬라이더 방향
            label="Zoom (%)"  # 라벨 텍스트
        )
        self.scale_preview.set(100)  # 기본값 100%
        self.scale_preview.pack(side="top", fill="x", padx=5, pady=5)  # 상단에 배치

    def setup_scrollbars(self):
        """
        스크롤바 설정 및 캔버스 연결
        
        구성:
        1. 가로 스크롤바
           - 하단 배치
           - 캔버스 xview 연결
        2. 세로 스크롤바
           - 우측 배치
           - 캔버스 yview 연결
        """
        self.x_scroll = ttk.Scrollbar(
            self.canvas,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.x_scroll.pack(side="bottom", fill="x")

        self.y_scroll = ttk.Scrollbar(
            self.canvas,
            orient="vertical",
            command=self.canvas.yview
        )
        self.y_scroll.pack(side="right", fill="y")

        self.canvas.configure(
            xscrollcommand=self.x_scroll.set,
            yscrollcommand=self.y_scroll.set
        )

    @ErrorHandler.handle_error
    def update_preview(self, image: ImageTk.PhotoImage = None):
        """
        결과 미리보기 업데이트
        
        처리 내용:
        1. 캔버스 초기화
        2. 이미지가 있는 경우:
           - 캔버스 중앙에 이미지 배치
           - 이미지 객체 참조 유지
        3. 이미지가 없는 경우:
           - 에러 메시지 표시
        
        Args:
            image: 표시할 이미지 (None인 경우 에러 메시지 표시)
        """
        self.canvas.delete("all")
        if image:
            x_center = self.canvas.winfo_width() // 2
            y_center = self.canvas.winfo_height() // 2
            self.canvas.create_image(x_center, y_center, image=image, anchor="center")
            self._image = image
        else:
            self.show_error_message()

    def show_error_message(self):
        """
        에러 메시지 표시
        
        처리 내용:
        1. 캔버스 중앙에 에러 메시지 표시
        2. 텍스트 스타일 설정
           - 색상: 빨간색
           - 폰트: Arial 16pt
           - 정렬: 중앙
        
        표시 메시지:
        - "이미지를 불러올 수 없습니다."
        """
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,  # 캔버스 가로 중심
            self.canvas.winfo_height() // 2,  # 캔버스 세로 중심
            text="이미지를 불러올 수 없습니다.",  # 에러 메시지
            fill="red",  # 텍스트 색상
            font=("Arial", 16),  # 텍스트 폰트
            anchor="center"  # 중심 정렬
        )

class OptionFrame(LabelFrame):
    """
    옵션 설정 프레임
    
    제공 옵션:
    1. 이미지 너비 (원본유지/1024/800/640)
    2. 이미지 간격 (없음/좁게/보통/넓게)
    3. 저장 포맷 (PNG/JPG)
    4. 정렬 방향 (수직/수평)
    
    특징:
    - 콤보박스를 통한 옵션 선택
    - 설정값 저장/로드 지원
    - 기본값 제공
    """
    def __init__(self, parent: Any, config: Dict[str, str], 
                 on_align_change: Callable, **kwargs):
        """
        옵션 프레임 초기화
        
        구성 요소:
        1. 너비 설정 콤보박스
        2. 간격 설정 콤보박스
        3. 포맷 설정 콤보박스
        4. 정렬 설정 콤보박스
        
        Args:
            parent: 부모 위젯
            config: 초기 설정값 딕셔너리
            on_align_change: 정렬 변경 시 호출될 콜백 함수
            **kwargs: 추가 설정값
        """
        super().__init__(parent, text="옵션", **kwargs)
        self.config = config
        self.on_align_change = on_align_change
        self.setup_ui()

    def setup_ui(self):
        """
        옵션 UI 구성 및 초기화
        
        구성 요소:
        1. 가로넓이 설정
           - 라벨과 콤보박스
           - 옵션: 원본유지/1024/800/640
        2. 간격 설정
           - 라벨과 콤보박스
           - 옵션: 없음/좁게/보통/넓게
        3. 포맷 설정
           - 라벨과 콤보박스
           - 옵션: PNG/JPG
        4. 정렬 설정
           - 라벨과 콤보박스
           - 옵션: 수직/수평
           - 정렬 변경 시 콜백 호출
        """
        self.option_vars = {}  # 옵션 변수 저장을 위한 딕셔너리 초기화
        
        # 가로넓이 라벨과 콤보박스
        self.label_width = ttk.Label(self, text="가로넓이", width=10)
        self.label_width.pack(side="left", padx=5, pady=5)
        
        # 가로넓이 설정용 StringVar와 콤보박스
        width_var = tk.StringVar(value=self.config.get("width", WIDTH_OPTIONS[0]))  # 기본값 설정
        width_combo = ttk.Combobox(  # 콤보박스 생성
            self,
            textvariable=width_var,  # 값 저장 변수
            values=WIDTH_OPTIONS,  # 선택 가능한 옵션 리스트
            state="readonly",  # 읽기 전용으로 설정
            width=10
        )
        width_combo.pack(side="left", padx=5, pady=5)  # 좌측에 배치
        self.option_vars["width"] = width_var  # 옵션 변수 딕셔너리에 추가

        # 간격 라벨과 콤보박스
        ttk.Label(self, text="간격", width=10).pack(side="left", padx=5, pady=5)  # 간격 라벨 생성 및 배치
        space_var = tk.StringVar(value=self.config.get("space", SPACE_OPTIONS[0]))  # 기본값 설정
        space_combo = ttk.Combobox(
            self,
            textvariable=space_var,  # 값 저장 변수
            values=SPACE_OPTIONS,  # 선택 가능한 옵션 리스트
            state="readonly",
            width=10
        )
        space_combo.pack(side="left", padx=5, pady=5)  # 좌측에 배치
        self.option_vars["space"] = space_var  # 옵션 변수 딕셔너리에 추가

        # 포맷 라벨과 콤보박스
        ttk.Label(self, text="포맷", width=10).pack(side="left", padx=5, pady=5)  # 포맷 라벨 생성 및 배치
        format_var = tk.StringVar(value=self.config.get("format", FORMAT_OPTIONS[0]))  # 기본값 설정
        format_combo = ttk.Combobox(
            self,
            textvariable=format_var,  # 값 저장 변수
            values=FORMAT_OPTIONS,  # 선택 가능한 옵션 리스트
            state="readonly",
            width=10
        )
        format_combo.pack(side="left", padx=5, pady=5)  # 좌측에 배치
        self.option_vars["format"] = format_var  # 옵션 변수 딕셔너리에 추가

        # 정렬 라벨과 콤보박스
        ttk.Label(self, text="정렬", width=10).pack(side="left", padx=5, pady=5)  # 정렬 라벨 생성 및 배치
        align_var = tk.StringVar(value=self.config.get("align", ALIGN_OPTIONS[0]))  # 기본값 설정
        align_combo = ttk.Combobox(
            self,
            textvariable=align_var,  # 값 저장 변수
            values=ALIGN_OPTIONS,  # 선택 가능한 옵션 리스트
            state="readonly",
            width=10
        )
        align_combo.pack(side="left", padx=5, pady=5)  # 좌측에 배치
        self.option_vars["align"] = align_var  # 옵션 변수 딕셔너리에 추가
        
        # 정렬 변경 이벤트만 바인딩하고, 다른 콤보박스는 이벤트 바인딩하지 않음
        align_var.trace_add("write", lambda *args: self.on_align_change())  # 값 변경 시 콜백 호출

        # 정렬 값에 따라 초기 라벨 텍스트 설정
        if align_var.get() == "수평":  # 정렬 값이 '수평'인 경우
            self.label_width.config(text="세로넓이")  # 라벨 텍스트 변경

    def get_options(self) -> Dict[str, str]:
        """
        현재 옵션값 반환
        
        Returns:
            Dict[str, str]: 현재 설정된 모든 옵션값
            {
                'width': 선택된 너비 값,
                'space': 선택된 간격 값,
                'format': 선택된 포맷 값,
                'align': 선택된 정렬 값
            }
        """
        return {key: var.get() for key, var in self.option_vars.items()}


class FileListFrame(LabelFrame):
    """
    파일 목록 관리 프레임
    
    기능:
    1. 파일 목록 표시 및 관리
       - 파일 추가/삭제
       - 파일 순서 변경 (위/아래)
       - 다중 선택 지원
    2. 드래그 앤 드롭 지원
    3. 스크롤바 지원
    
    상태 관리:
    - listbox: 파일 목록을 표시하는 리스트박스
    - scrollbar: 세로 스크롤바
    
    콜백 함수:
    - on_add: 파일 추가
    - on_remove: 파일 삭제
    - on_move_up: 위로 이동
    - on_move_down: 아래로 이동
    - on_select_callback: 선택 변경
    """
    def __init__(self, parent, **kwargs):
        """
        파일 목록 프레임 초기화
        
        Args:
            parent: 부모 위젯
            **kwargs: 추가 설정값
            
        초기화 내용:
        - 콜백 함수 초기화 (파일 추가/삭제/이동)
        - UI 구성 요소 생성
        """
        super().__init__(parent, text="파일 리스트", **kwargs)
        # 콜백 함수 초기화
        self.on_add = None  # 파일 추가 콜백 함수
        self.on_remove = None  # 파일 제거 콜백 함수
        self.on_move_up = None  # 파일 위로 이동 콜백 함수
        self.on_move_down = None  # 파일 아래로 이동 콜백 함수
        self.setup_ui()  # UI 구성 함수 호출
        
    def setup_ui(self):
        """
        파일 목록 UI 구성 및 초기화
        
        구성 요소:
        1. 리스트박스 프레임
           - 파일 목록 표시 영역
           - 세로 스크롤바
           - 다중 선택 지원
        
        2. 버튼 프레임
           - 파일 추가/삭제 버튼
           - 순서 이동 버튼 (↑/↓)
           - 버튼 간격: DEFAULT_PADDING
        
        레이아웃:
        - 리스트박스: 좌측 배치, 확장 가능
        - 버튼들: 우측 배치, 세로 정렬
        
        이벤트 바인딩:
        - <<ListboxSelect>>: 선택 변경 이벤트
        - 버튼 클릭: 각 기능 실행
        """
        self.list_frame = Frame(self)  # 파일 목록을 표시할 프레임 생성
        self.list_frame.pack(side="left", fill="both", expand=True, padx=DEFAULT_PADDING)  # 좌측에 배치
        
        # 스크롤바
        self.scrollbar = Scrollbar(self.list_frame)  # 세로 스크롤바 생성
        self.scrollbar.pack(side="right", fill="y")  # 우측에 배치
        
        # 리스트박스
        self.listbox = Listbox(
            self.list_frame,  # 리스트박스가 들어갈 프레임
            selectmode="extended",  # 여러 개 선택 가능
            height=10,  # 리스트박스 높이
            yscrollcommand=self.scrollbar.set,  # 스크롤바 연결
            exportselection=0  # 다른 위젯에서 선택 유지 방지
        )
        self.listbox.pack(side="left", fill="both", expand=True)  # 좌측에 배치
        self.scrollbar.config(command=self.listbox.yview)  # 스크롤 동작 연결
        
        # 선택 이벤트만 바인딩
        self.listbox.bind('<<ListboxSelect>>', lambda e: self.on_select(e))
        
        # 버튼 프레임
        self.setup_buttons()
        
    def setup_buttons(self):
        """
        버튼 프레임 설정
        
        구성 버튼:
        1. 파일 추가 버튼
        2. 선택 삭제 버튼
        3. 위로 이동 버튼
        4. 아래로 이동 버튼
        
        처리 내용:
        - 각 버튼에 콜백 함수 연결
        - 버튼 레이아웃 설정
        """
        btn_frame = Frame(self)  # 버튼 배치를 위한 프레임 생성
        btn_frame.pack(side="right", fill="y", padx=DEFAULT_PADDING)  # 우측에 배치

        # 버튼 생성
        Button(btn_frame, text="파일 추가", 
               command=lambda: self.on_add() if self.on_add else None).pack(fill="x", pady=2)  # 추가 버튼
        Button(btn_frame, text="선택 삭제", 
               command=lambda: self.on_remove() if self.on_remove else None).pack(fill="x", pady=2)  # 삭제 버튼
        Button(btn_frame, text="↑", 
               command=lambda: self.on_move_up() if self.on_move_up else None, 
               width=3).pack(pady=(20,2))  # 위로 이동 버튼
        Button(btn_frame, text="↓", 
               command=lambda: self.on_move_down() if self.on_move_down else None, 
               width=3).pack(pady=2)  # 아래로 이동 버튼
        
    def on_add(self):
        """
        파일 추가 버튼 이벤트
        
        처리 내용:
        - 콜백 함수가 설정된 경우 호출
        
        콜백:
        - on_add: 메인 앱의 add_file 메서드 호출
        """
        # 이벤트 콜백을 위한 더미 메서드
        pass
        
    def on_remove(self):
        """
        파일 삭제 버튼 이벤트
        
        처리 내용:
        - 콜백 함수가 설정된 경우 호출
        
        콜백:
        - on_remove: 메인 앱의 remove_files 메서드 호출
        """
        # 이벤트 콜백을 위한 더미 메서드
        pass
        
    def on_move_up(self):
        """
        위로 이동 버튼 이벤트
        
        처리 내용:
        - 콜백 함수가 설정된 경우 호출
        
        콜백:
        - on_move_up: 메인 앱의 move_up 메서드 호출
        """
        # 이벤트 콜백을 위한 더미 메서드
        pass
        
    def on_move_down(self):
        """
        아래로 이동 버튼 이벤트
        
        처리 내용:
        - 콜백 함수가 설정된 경우 호출
        
        콜백:
        - on_move_down: 메인 앱의 move_down 메서드 호출
        """
        # 이벤트 콜백을 위한 더미 메서드
        pass
        
    def on_select(self, event):
        """
        리스트박스 선택 이벤트
        
        처리 내용:
        - 콜백 함수가 설정된 경우 이벤트 객체와 함께 호출
        
        Args:
            event: 리스트박스 선택 이벤트 객체
            
        콜백:
        - on_select_callback: 메인 앱의 on_list_select 메서드 호출
        """
        if hasattr(self, 'on_select_callback'):
            self.on_select_callback(event)

class ImageControlFrame(LabelFrame):
    """
    이미지 제어 프레임
    
    기능:
    1. 이미지 회전 (좌/우 90도)
    2. 이미지 좌우 반전
    3. 현재/전체 이미지 초기화
    
    상태 관리:
    - image_states: Dict[str, ImageTransformState] 
      각 이미지 경로별 회전/반전 상태 저장
    
    콜백 함수:
    - on_rotate: 회전 이벤트 처리
    - on_flip: 반전 이벤트 처리
    - on_reset_current: 현재 이미지 초기화
    - on_reset_all: 전체 이미지 초기화
    """
    def __init__(self, parent: Any):
        """
        이미지 제어 프레임 초기화
        
        구성 요소:
        1. 회전 버튼 (좌/우)
        2. 좌우 반전 버튼
        3. 초기화 버튼 (현재/전체)
        
        상태 관리:
        - image_states: 이미지별 회전/반전 상태 저장
        - current_image: 현재 선택된 이미지 경로
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent, text="이미지 제어")
        self.image_states = {}  # 이미지별 상태 저장
        self.setup_ui()

    def setup_ui(self):
        """
        이미지 제어 프레임 UI 설정
        
        구성 요소:
        1. 좌측 프레임
           - 회전 버튼 프레임 (← 90°, 90° →)
           - 좌우반전 버튼
        2. 우측 프레임
           - 현재 초기화 버튼
           -  버튼 (초기화 가능 개수 표시)
        
        레이아웃:
        - 회전/반전 버튼은 좌측에 배치
        - 초기화 버튼은 우측에 배치
        - 모든 버튼은 초기에 비활성화 상태
        """
        # 좌측 버튼 프레임
        left_frame = ttk.Frame(self)  # 좌측 버튼을 포함하는 프레임 생성
        left_frame.pack(side="left", fill="x", expand=True)  # 프레임을 좌측 정렬 및 확장

        # 회전 버튼들
        rotate_frame = ttk.Frame(left_frame)  # 회전 버튼 전용 하위 프레임
        rotate_frame.pack(side="left", padx=5)  # 좌측으로 배치

        # 왼쪽으로 회전 버튼 (머리가 왼쪽으로)
        self.rotate_left_btn = ttk.Button(
            rotate_frame,
            text="← 90°",  # 버튼 텍스트
            width=8,  # 버튼 폭
            command=self.rotate_left,  # 회전 메서드 연결
            state="disabled"  # 초기에는 비활성화 상태
        )
        self.rotate_left_btn.pack(side="left", padx=2)  # 버튼 배치
        
        # 오른쪽으로 회전 버튼
        self.rotate_right_btn = ttk.Button(
            rotate_frame,
            text="90° →",  # 버튼 텍스트
            width=8,  # 버튼 폭
            command=self.rotate_right,  # 회전 메서드 연결
            state="disabled"  # 초기에는 비활성화 상태
        )
        self.rotate_right_btn.pack(side="left", padx=2)  # 버튼 배치   
        # 반전 버튼
        self.flip_btn = ttk.Button(
            left_frame,
            text="좌우반전",  # 버튼 텍스트
            width=8,  # 버튼 폭
            command=self.toggle_flip,  # 반전 토글 메서드 연결
            state="disabled"  # 초기에는 비활성화 상태
        )
        self.flip_btn.pack(side="left", padx=5)  # 버튼 배치

        # 우측 초기화 버튼
        right_frame = ttk.Frame(self)  # 우측 초기화 버튼 프레임 생성
        right_frame.pack(side="right", padx=5)  # 우측 정렬

        # 전체 초기화 버튼 (가장 오른쪽)
        self.reset_all_btn = ttk.Button(
            right_frame,
            text="전체 초기화 (0)",  # 초기 상태는 0개 초기화 가능
            width=15,  # 버튼 폭
            command=self.reset_all_images,  # 모든 이미지 초기화 메서드 연결
            state="disabled"  # 초기에는 비활성화 상태
        )
        self.reset_all_btn.pack(side="right", padx=2)  # 버튼 배치
        # 현재 이미지 초기화 버튼 (전체 초기화 왼쪽)
        self.reset_current_btn = ttk.Button(
            right_frame,
            text="현재 초기화",  # 버튼 텍스트
            width=12,  # 버튼 폭
            command=self.reset_current_image,  # 현재 이미지 초기화 메서드 연결
            state="disabled"  # 초기에는 비활성화 상태
        )
        self.reset_current_btn.pack(side="right", padx=2)  # 버튼 배치
    
    def set_current_image(self, image_path, selected_count=1):
        """
        현재 이미지 설정 및 UI 상태 업데이트
        
        처리 순서:
        1. 현재 이미지 정보 설정
           - 이미지 경로 저장
           - 선택된 이미지 수 저장
        
        2. 이미지 상태 초기화 (필요한 경우)
           - 새 이미지인 경우 상태 객체 생성
           - ImageTransformState 인스턴스로 초기화
        
        3. 버튼 상태 업데이트
           - 회전 버튼 (← 90°, 90° →)
           - 좌우반전 버튼
           - 현재 초기화 버튼
           - 전체 초기화 버튼
        
        4. 초기화 카운트 업데이트
           - 변형된 이미지 수 계산
           - 전체 초기화 버튼 텍스트 업데이트
        
        버튼 활성화 조건:
        - 단일 선택(selected_count == 1)이고 유효한 이미지 경로인 경우
        - 그 외의 경우 모든 버튼 비활성화
        
        Args:
            image_path: 선택된 이미지 경로
            selected_count: 선택된 이미지 개수
        """
        self.current_image = image_path
        self.selected_count = selected_count

        if image_path and image_path not in self.image_states:
            self.image_states[image_path] = ImageTransformState()

        # 버튼 상태 설정
        state = "normal" if image_path and selected_count == 1 else "disabled"
        self.rotate_left_btn.configure(state=state)
        self.rotate_right_btn.configure(state=state)
        self.flip_btn.configure(state=state)
        self.reset_current_btn.configure(state=state)

        self.update_reset_count()

    def toggle_flip(self):
        """
        좌우반전 토글
        
        처리 순서:
        1. 현재 이미지 존재 확인
        2. 콜백 함수 존재 확인 및 호출
        
        콜백:
        - on_flip: 메인 앱의 flip_image 메서드 호출
        """
        if self.current_image:
            if self.on_flip:
                self.on_flip()

    def update_reset_count(self):
        """
        초기화 가능한 이미지 수 업데이트
        
        처리 순서:
        1. 기본 상태가 아닌 이미지 개수 계산
        2. 전체 초기화 버튼 텍스트 업데이트
           - 형식: "전체 초기화 (개수)"
        3. 버튼 활성화/비활성화 상태 설정
           - 초기화 가능한 이미지가 있으면 활성화
           - 없으면 비활성화
        """
        count = sum(1 for state in self.image_states.values() if not state.is_default())
        self.reset_all_btn.config(
            text=f"전체 초기화 ({count})",
            state="normal" if count > 0 else "disabled"
        )

    def reset_current_image(self):
        """
        현재 이미지의 회전/반전 상태 초기화
        
        처리 순서:
        1. 현재 이미지 상태 존재 확인
        2. 회전/반전 상태 초기화
        3. 초기화 카운트 업데이트
        4. 콜백 함수 호출
        
        콜백:
        - on_reset_current: 메인 앱의 reset_current_image_control 메서드 호출
        """
        if self.current_image and self.current_image in self.image_states:
            self.image_states[self.current_image].reset()
            self.update_reset_count()
            if self.on_reset_current:
                self.on_reset_current()

    def reset_all_images(self):
        """
        모든 이미지 초기화
        
        처리 내용:
        1. 모든 이미지 상태 초기화
        2. 초기화 카운트 업데이트
        3. 콜백 함수 호출
        
        콜백:
        - on_reset_all: 메인 앱의 reset_all_image_controls 메서드 호출
        """
        for state in self.image_states.values():
            state.reset()
        self.update_reset_count()
        if self.on_reset_all:
            self.on_reset_all()

    def remove_image(self, image_path):
        """
        이미지 삭제 및 상태 정리
        
        처리 내용:
        1. 이미지 상태 존재 확인
        2. 상태 딕셔너리에서 제거
        3. 초기화 카운트 업데이트
        
        Args:
            image_path: 삭제할 이미지 경로
        """
        if image_path in self.image_states:
            del self.image_states[image_path]
            self.update_reset_count()

    def rotate_left(self):
        """
        왼쪽으로 90도 회전
        
        처리 내용:
        1. 콜백 함수 존재 확인
        2. 90도 회전 값으로 콜백 호출
        
        콜백:
        - on_rotate: 메인 앱의 rotate_image 메서드 호출 (각도: 90)
        """
        if hasattr(self, 'on_rotate') and self.on_rotate:
            self.on_rotate(90)

    def rotate_right(self):
        """
        오른쪽으로 90도 회전
        
        처리 내용:
        1. 콜백 함수 존재 확인
        2. -90도 회전 값으로 콜백 호출
        
        콜백:
        - on_rotate: 메인 앱의 rotate_image 메서드 호출 (각도: -90)
        """
        if hasattr(self, 'on_rotate') and self.on_rotate:
            self.on_rotate(-90)


class ImageFilterFrame(LabelFrame):
    """
    이미지 필터 조절 프레임
    
    제공 필터:
    - 밝기 (Brightness)
    - 대비 (Contrast)
    - 채도 (Saturation)
    - 선명도 (Sharpness)
    
    특징:
    - 실시간 미리보기 지원
    - 필터값 초기화 기능
    - 개별/전체 이미지 적용
    """
    
    def __init__(self, parent):
        """
        이미지 필터 조절 프레임 초기화
        
        구성 요소:
        1. 필터 슬라이더 (밝기/대비/채도/선명도)
        2. 초기화 버튼 (개별/전체)
        3. 필터값 표시 레이블
        
        상태 관리:
        - filter_states: 이미지별 필터 상태 저장
        - current_image: 현재 선택된 이미지 경로
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent, text="이미지 필터")
        self.filter_states = {}  # {image_path: ImageFilterState()}
        self.current_image = None
        self.on_filter_change = None
        self.controls = []
        self.create_variables()
        self.setup_ui()
        self.set_current_image(None)

    def create_variables(self):
        """
        필터 조절을 위한 변수 생성
        
        생성되는 변수:
        1. brightness_var: 밝기 조절 (0.0 ~ 3.0)
        2. contrast_var: 대비 조절 (0.0 ~ 3.0)
        3. saturation_var: 채도 조절 (0.0 ~ 3.0)
        4. posterize_var: 포스터화 효과 (0.0 ~ 3.0)
        
        모든 변수의 기본값: 1.0 (원본 상태)
        """
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.saturation_var = tk.DoubleVar(value=1.0)
        self.posterize_var = tk.DoubleVar(value=1.0)

    def setup_ui(self):
        """
        필터 UI 구성 및 초기화
        
        구성 요소:
        1. 필터 컨트롤 프레임들
           - 밝기 조절 (0.0 ~ 3.0)
           - 대비 조절 (0.0 ~ 3.0)
           - 채도 조절 (0.0 ~ 3.0)
           - 포스터화 효과 (0.0 ~ 3.0)
        2. 하단 버튼 프레임
           - 현재 이미지 초기화 버튼
           - 전체 초기화 버튼
        
        레이아웃:
        - 각 필터 컨트롤은 세로로 배치
        - 초기화 버튼들은 하단에 배치
        - 현재 초기화는 중앙, 전체 초기화는 우측에 배치
        """
        main_frame = ttk.Frame(self)  # 필터 컨트롤들을 담을 메인 프레임 생성
        main_frame.pack(fill="x", padx=5, pady=1)

        # 밝기 조절 컨트롤 생성 및 추가
        brightness_frame = self.create_filter_control("밝기", 0.0, 3.0, self.brightness_var)
        brightness_frame.pack(fill="x", padx=5, pady=1)

        # 대비 조절 컨트롤 생성 및 추가
        contrast_frame = self.create_filter_control("대비", 0.0, 3.0, self.contrast_var)
        contrast_frame.pack(fill="x", padx=5, pady=1)

        # 채도 조절 컨트롤 생성 및 추가
        saturation_frame = self.create_filter_control("채도", 0.0, 3.0, self.saturation_var)
        saturation_frame.pack(fill="x", padx=5, pady=1)

        # 포스터화 효과 조절 컨트롤 생성 및 추가
        posterize_frame = self.create_filter_control("포스터화", 0.0, 3.0, self.posterize_var)
        posterize_frame.pack(fill="x", padx=5, pady=1)

        # 하단 프레임 생성 (초기화 버튼용)
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=5, pady=(5, 3))

        # 중앙에 현재 이미지 초기화 버튼 배치
        center_frame = ttk.Frame(bottom_frame)
        center_frame.pack(fill="x")
        ttk.Frame(center_frame).pack(side="left", expand=True)  # 왼쪽 여백
        self.reset_current_btn = ttk.Button(
            center_frame,
            text="현재 초기화",
            width=12,
            command=self.reset_current_image,  # 현재 이미지 필터 초기화 메서드 연결
            state="disabled"  # 초기 상태 비활성화
        )
        self.reset_current_btn.pack(side="left")
        ttk.Frame(center_frame).pack(side="left", expand=True)  # 오른쪽 여백

        # 우측에 전체 초기화 버튼 배치
        reset_all_frame = ttk.Frame(bottom_frame)
        reset_all_frame.pack(side="right", pady=(3, 0))
        self.reset_all_btn = ttk.Button(
            reset_all_frame,
            text="전체 초기화 (0)",  # 초기화 가능한 이미지 수를 표시
            width=15,
            command=self.reset_all_filters,  # 모든 이미지 초기화 메서드 연결
            state="disabled"  # 초기 상태 비활성화
        )
        self.reset_all_btn.pack(side="right")

    def create_filter_control(self, name, min_val, max_val, var):
        """
        필터 조절 컨트롤 생성
        
        구성 요소:
        1. 필터 이름 레이블
        2. 현재값 표시 레이블
        3. 초기화 버튼
        4. 슬라이더 컨트롤
        
        Args:
            name: 필터 이름
            min_val: 슬라이더 최소값
            max_val: 슬라이더 최대값
            var: 연결할 변수 (DoubleVar)
            
        Returns:
            생성된 필터 컨트롤 프레임
        """
        frame = ttk.Frame(self)  # 개별 필터 컨트롤용 프레임 생성

        # 상단 프레임 생성 (레이블, 값 표시, 초기화 버튼 포함)
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="x")

        label = ttk.Label(top_frame, text=name)  # 필터 이름 레이블
        label.pack(side="left")

        value_label = ttk.Label(top_frame, text=f"{var.get():.1f}", width=4)  # 현재 값 표시 레이블
        value_label.pack(side="right")
        setattr(self, f"{self._get_var_name(name)}_label", value_label)  # 값 레이블 속성으로 저장

        reset_btn = ttk.Button(
            top_frame,
            text="초기화",
            width=5,
            command=lambda n=name: self.reset_filter(self._get_var_name(n))  # 필터 초기화 메서드 연결
        )
        reset_btn.pack(side="right", padx=(0, 2))  # 초기화 버튼 추가

        scale = ttk.Scale(
            frame,
            from_=min_val,  # 최소값
            to=max_val,  # 최대값
            variable=var,  # 필터 변수
            orient="horizontal",  # 가로 방향 슬라이더
            command=lambda v: self.update_filter(self._get_var_name(name), value_label, v)  # 값 변경 시 메서드 호출
        )
        scale.pack(fill="x", pady=(0, 2))  # 슬라이더 추가

        self.controls.extend([label, value_label, reset_btn, scale])  # 컨트롤 저장
        return frame  # 생성된 프레임 반환

    def _get_var_name(self, name):
        """
        필터 이름을 변수 이름으로 변환
        
        변환 규칙:
        - 밝기 -> brightness
        - 대비 -> contrast
        - 채도 -> saturation
        - 포스터화 -> posterize
        
        Args:
            name: 한글 필터 이름
            
        Returns:
            str: 영문 변수명
        """
        name_map = {
            "밝기": "brightness",
            "대비": "contrast",
            "채도": "saturation",
            "포스터화": "posterize"
        }
        return name_map.get(name, name.lower())

    @ErrorHandler.handle_error
    def update_filter(self, filter_name, label, value):
        """
        필터 값 업데이트
        
        처리 순서:
        1. 레이블 텍스트 업데이트
        2. 현재 이미지의 필터 상태 업데이트
           - 필터 상태 없으면 새로 생성
           - 필터값 설정
        3. 초기화 카운트 업데이트
        4. 필터 변경 콜백 호출
        
        Args:
            filter_name: 업데이트할 필터 이름
            label: 값 표시 레이블 위젯
            value: 새로운 필터 값
        """
        label.config(text=f"{float(value):.1f}")

        if self.current_image:
            if self.current_image not in self.filter_states:
                self.filter_states[self.current_image] = ImageFilterState()
            self.filter_states[self.current_image].set_filter(filter_name, float(value))
            self.update_reset_count()

        if self.on_filter_change:
            self.on_filter_change()

    def reset_filter(self, filter_name):
        """
        개별 필터 초기화
        
        처리 내용:
        1. 필터 변수와 레이블 초기화 (1.0)
        2. 현재 이미지의 필터 상태 업데이트
        3. 필터 상태가 기본값이면 초기화 카운트 업데이트
        4. 필터 변경 콜백 호출
        
        Args:
            filter_name: 초기화할 필터 이름
        """
        var = getattr(self, f"{filter_name}_var")
        label = getattr(self, f"{filter_name}_label")
        var.set(1.0)
        label.config(text="1.0")

        if self.current_image and self.current_image in self.filter_states:
            self.filter_states[self.current_image].set_filter(filter_name, 1.0)
            if self.filter_states[self.current_image].is_default():
                self.update_reset_count()
            
        if self.on_filter_change:
            self.on_filter_change()

    def reset_current_image(self):
        """
        현재 이미지의 회전/반전 상태 초기화
        
        처리 순서:
        1. 현재 이미지 상태 존재 확인
        2. 회전/반전 상태 초기화
        3. 초기화 카운트 업데이트
        4. 콜백 함수 호출
        
        콜백:
        - on_reset_current: 메인 앱의 reset_current_image_control 메서드 호출
        """
        if self.current_image:
            if self.current_image in self.filter_states:
                self.filter_states[self.current_image].reset()
            
            # UI 업데이트
            for filter_name in ['brightness', 'contrast', 'saturation', 'posterize']:
                var = getattr(self, f"{filter_name}_var")
                label = getattr(self, f"{filter_name}_label")
                var.set(1.0)
                label.config(text="1.0")

            self.update_reset_count()

            if self.on_filter_change:
                self.on_filter_change()

    def update_reset_count(self):
        """
        초기화 가능한 이미지 수 업데이트
        
        처리 순서:
        1. 기본 상태가 아닌 이미지 개수 계산
        2. 전체 초기화 버튼 텍스트 업데이트
           - 형식: "전체 초기화 (개수)"
        3. 버튼 활성화/비활성화 상태 설정
           - 초기화 가능한 이미지가 있으면 활성화
           - 없으면 비활성화
        """
        count = sum(1 for state in self.filter_states.values() if not state.is_default())
        self.reset_all_btn.config(
            text=f"전체 초기화 ({count})",
            state="normal" if count > 0 else "disabled"
        )

    def remove_image(self, image_path):
        """
        이미지 삭제 및 상태 정리
        
        처리 내용:
        1. 이미지 필터 상태 존재 확인
        2. 필터 상태 딕셔너리에서 제거
        3. 초기화 카운트 업데이트
        
        Args:
            image_path: 삭제할 이미지 경로
        """
        if image_path in self.filter_states:
            del self.filter_states[image_path]
            self.update_reset_count()

    @ErrorHandler.handle_error
    def set_current_image(self, image_path, selected_count=1):
        """
        현재 이미지 설정 및 UI 상태 업데이트
        
        처리 순서:
        1. 현재 이미지 정보 설정
           - 이미지 경로 저장
           - 선택된 이미지 수 저장
        
        2. 이미지 상태 초기화 (필요한 경우)
           - 새 이미지인 경우 상태 객체 생성
           - ImageTransformState 인스턴스로 초기화
        
        3. 버튼 상태 업데이트
           - 회전 버튼 (← 90°, 90° →)
           - 좌우반전 버튼
           - 현재 초기화 버튼
           - 전체 초기화 버튼
        
        4. 초기화 카운트 업데이트
           - 변형된 이미지 수 계산
           - 전체 초기화 버튼 텍스트 업데이트
        
        버튼 활성화 조건:
        - 단일 선택(selected_count == 1)이고 유효한 이미지 경로인 경우
        - 그 외의 경우 모든 버튼 비활성화
        
        Args:
            image_path: 선택된 이미지 경로 (None이면 초기화)
            selected_count: 선택된 이미지 개수 (기본값: 1)
        """
        self.current_image = image_path

        # 이미지가 하나만 선택된 경우에만 컨트롤을 활성화
        state = "normal" if image_path and selected_count == 1 else "disabled"

        # 모든 필터 컨트롤 상태 설정
        for control in self.controls:
            control.configure(state=state)

        # 초기화 버튼들의 상태 설정
        bottom_frame = self.winfo_children()[-1]
        for widget in bottom_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, ttk.Button):
                        btn.configure(state=state)

        if image_path:
            if image_path not in self.filter_states:
                self.filter_states[image_path] = ImageFilterState()

            # 필터 상태 복원
            state = self.filter_states[image_path]
            filters = state.get_state()
            for filter_name in ['brightness', 'contrast', 'saturation', 'posterize']:
                var = getattr(self, f"{filter_name}_var")
                label = getattr(self, f"{filter_name}_label")
                value = filters[filter_name]
                var.set(value)
                label.config(text=f"{value:.1f}")
        else:
            # UI를 기본값으로 초기화
            for filter_name in ['brightness', 'contrast', 'saturation', 'posterize']:
                var = getattr(self, f"{filter_name}_var")
                label = getattr(self, f"{filter_name}_label")
                var.set(1.0)
                label.config(text="1.0")

        # 초기화 가능한 이미지 수 업데이트
        self.update_reset_count()

    def reset_all_filters(self):
        """
        모든 이미지의 필터 초기화
        
        처리 순서:
        1. 모든 이미지의 필터 상태 초기화
        2. 모든 필터 UI 컨트롤 초기화 (1.0)
        3. 초기화 카운트 업데이트
        4. 필터 변경 콜백 호출
        
        콜백:
        - on_filter_change: 메인 앱의 apply_filter 메서드 호출
        """
        for state in self.filter_states.values():
            state.reset()

        # UI 업데이트
        for filter_name in ['brightness', 'contrast', 'saturation', 'posterize']:
            var = getattr(self, f"{filter_name}_var")
            label = getattr(self, f"{filter_name}_label")
            var.set(1.0)
            label.config(text="1.0")

        self.update_reset_count()

        if self.on_filter_change:
            self.on_filter_change()
