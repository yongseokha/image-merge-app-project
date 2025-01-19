import os
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
from typing import Optional

# 프로그램 상수 및 설정값 임포트
from constants import (
    WINDOW_SIZE,  # 윈도우 크기
    DEFAULT_PADDING,  # 기본 패딩값
    SUPPORTED_FORMATS,  # 지원하는 이미지 포맷
    DEFAULT_PICTURES_DIR, # 기본 사진 디렉토리
    PREVIEW_WIDTH,  # 미리보기 영역 너비 (픽셀)
    PREVIEW_HEIGHT,  # 미리보기 영역 높이 (픽셀)
)

# 커스텀 모듈 임포트
from image_processor import ImageProcessor  # 이미지 처리 클래스
from image_processor import ImageTransformState  # 이미지 변형 상태 클래스
from ui_components import (  # UI 컴포넌트 클래스들
    PreviewFrame,  # 미리보기 프레임
    ResultPreviewFrame,  # 결과 미리보기 프레임
    OptionFrame,  # 옵션 설정 프레임
    FileListFrame,  # 파일 목록 프레임
    ImageControlFrame,  # 이미지 제어 프레임
    ImageFilterFrame,  # 이미지 필터 프레임
)
from error_handler import ErrorHandler  # 에러 처리 클래스
from config_manager import ConfigManager  # 설정 관리 클래스

# 로깅 설정
ErrorHandler.setup_logging()

class ImageMergerApp:
    """
    이미지 병합 프로그램의 메인 애플리케이션 클래스
    
    주요 기능:
    1. 이미지 파일 관리
       - 파일 추가/삭제
       - 순서 변경
       - 드래그 앤 드롭 지원
    2. 이미지 편집
       - 회전/반전 기능
       - 필터 적용 (밝기/대비/채도)
       - 포스터화 효과
    3. 이미지 병합
       - 수직/수평 정렬
       - 간격 조절
       - 크기 조정
    4. 결과물 관리
       - 미리보기 제공
       - JPG/PNG 형식 저장
       - 확대/축소 기능
    
    구성 요소:
    - 좌측 패널: 이미지 목록 및 편집 도구
    - 우측 패널: 결과 미리보기 및 저장 옵션
    """
    
    # === 초기화 관련 메서드 ===
    @ErrorHandler.handle_error
    def __init__(self, root: TkinterDnD.Tk):
        """
        애플리케이션 초기화
        
        처리 순서:
        1. 루트 윈도우 설정
           - 윈도우 제목 및 크기 설정
           - 단축키 바인딩
           - 드래그 앤 드롭 설정
        2. 설정 관리
           - ConfigManager 초기화
           - 설정 파일 로드
           - 기본값 설정
        3. UI 프레임 생성
           - 좌측 프레임 (파일 목록/편집 도구)
           - 우측 프레임 (미리보기/저장)
           - 각 컴포넌트 초기화
        4. 상태 관리 초기화
           - 이미지 처리기 설정
           - 미리보기 상태 초기화
           - 경로 설정 초기화
        
        Args:
            root: TkinterDnD 루트 윈도우 객체
                드래그 앤 드롭을 지원하는 Tk 인스턴스
        """
        self.root = root
        self.setup_window()
        
        # config 경로 설정 및 로드
        self.config_manager = ConfigManager()
        self.config_manager.load()
        self.config = self.config_manager.config
        
        self.create_frames()
        self.init_variables()
        self.setup_dnd()
        
        # 이미지 제어 프레임 콜백 설정
        self.image_control_frame.on_flip = self.flip_image
        self.image_control_frame.on_rotate = self.rotate_image
        
    @ErrorHandler.handle_error
    def setup_window(self):
        """
        메인 윈도우 기본 설정
        
        처리 순서:
        1. 윈도우 제목 설정
           - "이미지 병합 프로그램"
        2. 윈도우 크기 설정
           - WINDOW_SIZE 상수 사용
        3. 단축키 설정
           - Ctrl + O: 파일 추가
           - Delete: 파일 삭제
           - Ctrl + S: 병합 시작
        """
        self.root.title("이미지 병합 프로그램")
        self.root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.setup_shortcuts()
        
    def setup_shortcuts(self):
        """
        단축키 설정
        
        처리 순서:
        1. 파일 관리 단축키 설정
           - Ctrl + O: 파일 추가
           - Delete: 파일 삭제
        2. 병합 관련 단축키 설정
           - Ctrl + S: 병합 시작
        
        단축키 목록:
        - Ctrl + O: add_file 메서드 호출
        - Delete: remove_files 메서드 호출
        - Ctrl + S: start_merge 메서드 호출
        """
        self.root.bind('<Control-o>', lambda e: self.add_file())  # Ctrl + O
        self.root.bind('<Delete>', lambda e: self.remove_files())  # Delete
        self.root.bind('<Control-s>', lambda e: self.start_merge())  # Ctrl + S

    @ErrorHandler.handle_error
    def create_frames(self):
        """
        UI 프레임 생성 및 배치
        
        처리 순서:
        1. 메인 프레임 분할
           - 좌측 프레임: 전체 너비의 1/2
           - 우측 프레임: 전체 너비의 1/2
        2. 좌측 프레임 구성
           - 옵션 프레임
           - 이미지 필터 프레임
           - 미리보기 프레임
           - 이미지 제어 프레임
           - 파일 목록 프레임
        3. 우측 프레임 구성
           - 결과 미리보기 프레임
           - 저장 경로 프레임
           - 진행 상황 프레임
        """
        # 메인 프레임 분할
        self.left_frame = Frame(self.root, width=WINDOW_SIZE[0]/2)
        self.right_frame = Frame(self.root, width=WINDOW_SIZE[0]/2)
        
        self.left_frame.pack(side="left", fill="both", expand=True)
        self.right_frame.pack(side="left", fill="both", expand=True)
        
        # 프레임 크기 고정
        self.left_frame.pack_propagate(False)
        self.right_frame.pack_propagate(False)
        
        # 좌측 프레임 구성
        self.create_left_frame_widgets()
        # 우측 프레임 구성
        self.create_right_frame_widgets()
        
    @ErrorHandler.handle_error
    def create_left_frame_widgets(self):
        """
        좌측 프레임 위젯 생성 및 배치
        
        처리 순서:
        1. 옵션 프레임 생성
           - 병합 옵션 설정 UI
           - 정렬 변경 콜백 연결
        2. 이미지 필터 프레임 생성
           - 필터 조절 UI
           - 필터 변경 콜백 연결
        3. 미리보기 프레임 생성
           - 선택 이미지 표시 영역
        4. 이미지 제어 프레임 생성
           - 회전/반전 버튼
           - 초기화 버튼
        5. 파일 리스트 프레임 생성
           - 파일 목록 관리 UI
        
        각 프레임은 콜백 함수와 연결되어 이벤트 처리
        """
        self.option_frame = OptionFrame(
            self.left_frame,
            self.config,
            self.on_align_change
        )
        self.option_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # 이미지 필터 프레임
        self.filter_frame = ImageFilterFrame(self.left_frame)
        self.filter_frame.app = self  # app 참조 설정
        self.filter_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        self.filter_frame.on_filter_change = self.apply_filter  # 콜백 함수 연결
        
        # 미리보기 프레임
        self.preview_frame = PreviewFrame(self.left_frame)
        self.preview_frame.pack(fill="both", expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # 이미지 제어 프레임
        self.image_control_frame = ImageControlFrame(self.left_frame)
        self.image_control_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # 콜백 함수 설정
        self.image_control_frame.on_rotate = self.rotate_image
        self.image_control_frame.on_flip = self.flip_image
        self.image_control_frame.on_reset_current = self.reset_current_image_control
        self.image_control_frame.on_reset_all = self.reset_all_image_controls
        
        # 파일 리스트 프레임
        self.create_file_frame()
    
    @ErrorHandler.handle_error
    def create_right_frame_widgets(self):
        """
        우측 프레임 위젯 생성 및 배치
        
        처리 순서:
        1. 결과 미리보기 프레임 생성
           - 병합 결과 표시 영역
           - 확대/축소 기능
           - 스크롤 지원
        2. 하단 프레임 생성
           - 저장 경로 입력/선택 UI
           - 진행률 표시 UI
           - 시작/닫기 버튼
        """
        # 결과 미리보기
        self.result_preview = ResultPreviewFrame(self.right_frame)
        self.result_preview.pack(fill="both", expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        self.result_preview.scale_preview.config(command=self.on_zoom)  # 줌 이벤트 연결
        
        # 하단 프레임 (저장 경로 + 진행률)
        bottom_frame = ttk.Frame(self.right_frame)
        bottom_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # 저장 경로 프레임
        path_frame = ttk.LabelFrame(bottom_frame, text="저장 경로")
        path_frame.pack(fill="x", pady=(0, DEFAULT_PADDING))
        
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        ttk.Button(path_frame, text="찾아보기", command=self.browse_dest_path).pack(
            side="right", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING
        )
        
        # 진행률 표시 프레임
        progress_frame = ttk.LabelFrame(bottom_frame, text="진행률")
        progress_frame.pack(fill="x")
        
        self.progress_var = DoubleVar()
        self.progress = ttk.Progressbar(
            progress_frame,
            maximum=100,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress.pack(fill="x", padx=DEFAULT_PADDING, pady=(DEFAULT_PADDING, 0))
        
        # 진행률 텍스트와 시작/닫기 버튼을 담을 프레임
        control_frame = ttk.Frame(progress_frame)
        control_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        self.progress_label = ttk.Label(control_frame, text="대기중...")
        self.progress_label.pack(side="left")
        
        ttk.Button(control_frame, text="닫기", command=self.root.quit).pack(side="right", padx=5)
        ttk.Button(control_frame, text="시작", command=self.start_merge).pack(side="right", padx=5)

    @ErrorHandler.handle_error
    def create_file_frame(self):
        """
        파일 목록 관리 프레임 생성
        
        처리 순서:
        1. 컨테이너 프레임 생성
           - 스크롤 가능한 프레임 구성
        2. 파일 리스트 프레임 생성
           - FileListFrame 인스턴스 생성
        3. 이벤트 핸들러 연결
           - 파일 추가: add_file
           - 파일 삭제: remove_files
           - 위로 이동: move_up
           - 아래로 이동: move_down
        4. 리스트박스 선택 이벤트 연결
           - <<ListboxSelect>> 이벤트를 on_list_select에 바인딩
        """
        # 파일 리스트 프레임을 스크롤 가능한 프레임으로 변경
        list_container = ttk.Frame(self.left_frame)
        list_container.pack(fill="both", expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        self.file_frame = FileListFrame(list_container)
        self.file_frame.pack(fill="both", expand=True)
        
        # 파일 리스트 이벤트 연결
        self.file_frame.on_add = self.add_file
        self.file_frame.on_remove = self.remove_files
        self.file_frame.on_move_up = self.move_up
        self.file_frame.on_move_down = self.move_down
        
        # 리스트박스 직접 접근을 위한 참조
        self.list_file = self.file_frame.listbox
        self.list_file.bind("<<ListboxSelect>>", self.on_list_select)

        
    @ErrorHandler.handle_error
    def init_variables(self):
        """
        변수 초기화
        
        처리 순서:
        1. 이미지 처리기 초기화
           - ImageProcessor 인스턴스 생성
           - app 참조 설정
        2. 이미지 관련 변수 초기화
           - 미리보기 이미지
           - 결과 이미지
        3. 디렉토리 경로 초기화
           - 마지막으로 열었던 디렉토리
           - 결과물 저장 디렉토리
        4. 저장 경로 UI 업데이트
           - 결과물 저장 경로를 path_entry에 표시
        """
        self.image_processor = ImageProcessor()
        self.image_processor.app = self  # ImageProcessor에 app 참조 추가
        
        self.preview_image = None
        self.result_image = None
        
        self.last_opened_dir = self.config.get("last_opened_dir", DEFAULT_PICTURES_DIR)
        self.result_opened_dir = self.config.get("result_opened_dir", DEFAULT_PICTURES_DIR)
        
        # 초기 저장 경로 설정
        if self.result_opened_dir:
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, self.result_opened_dir)
        
    
    def setup_dnd(self):
        """
        드래그 앤 드롭 기능 설정
        
        처리 순서:
        1. 드롭 타겟 등록
           - DND_FILES 타입 등록
        2. 드롭 이벤트 바인딩
           - <<Drop>> 이벤트를 on_drop 메서드에 연결
        """
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    @ErrorHandler.handle_error
    def on_drop(self, event):
        """
        드래그 앤 드롭으로 파일 추가 처리
        
        처리 순서:
        1. 드롭된 파일 목록 파싱
           - tk.splitlist로 파일 경로 분리
        2. 각 파일별 처리
           - 지원 형식 확인 (SUPPORTED_FORMATS)
           - 중복 파일 검사
           - 유효한 파일만 목록에 추가
        3. 미리보기 업데이트
           - 추가된 파일이 있으면 미리보기 갱신
        
        Args:
            event: 드롭 이벤트 객체
                data 속성에 드롭된 파일 경로 포함
        """
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                existing_index = self._find_existing_file(file)
                if existing_index is not None:
                    self._handle_duplicate_file(file, existing_index)
                else:
                    self.list_file.insert(END, file)
        self.update_preview()

    @ErrorHandler.handle_error
    def on_list_select(self, event):
        """
        리스트박스 선택 이벤트 처리
        
        처리 순서:
        1. 현재 선택된 항목 확인
        2. 선택된 이미지 경로 가져오기
        3. 선택된 항목 개수 확인
        4. UI 상태 업데이트
           - 이미지 제어 프레임 상태
           - 필터 프레임 상태
        5. 미리보기 업데이트
           - 단일 선택: 이미지 처리 및 표시
           - 다중 선택/선택 없음: 미리보기 초기화
        
        Args:
            event: 리스트박스 선택 이벤트 객체
        """
        selected = self.list_file.curselection()
        if not selected:
            self.preview_frame.update_preview(None, self.list_file.size(), 0)
            return

        image_path = self.list_file.get(selected[0])
        selected_count = len(selected)

        # 이미지 제어 프레임과 필터 프레임 상태 업데이트
        self.image_control_frame.set_current_image(image_path, selected_count)
        self.filter_frame.set_current_image(image_path, selected_count)

        # 이미지 미리보기 업데이트
        if selected_count == 1:
            self._process_single_image(image_path)
        else:
            self.preview_frame.update_preview(None, self.list_file.size(), selected_count)

    def on_align_change(self, *args):
        """
        이미지 정렬 방향 변경 처리
        
        처리 순서:
        1. 현재 정렬 방향 확인
           - 수평/수직 옵션 확인
        2. 너비 레이블 텍스트 업데이트
           - 수평 정렬: "세로넓이"
           - 수직 정렬: "가로넓이"
        3. UI 상태 업데이트
           - 레이블 텍스트 변경
           - 미리보기 이미지 재배치
        
        Args:
            *args: 이벤트 관련 추가 인자
        """
        align = self.option_frame.option_vars["align"].get()
        width_label = self.option_frame.winfo_children()[0]  # 첫 번째 라벨
        width_label.config(text="세로넓이" if align == "수평" else "가로넓이")

    @ErrorHandler.handle_error
    def on_zoom(self, value):
        """
        결과 이미지 확대/축소 처리
        
        처리 순서:
        1. 이미지 존재 여부 확인
        2. 이미지 크기 조정
           - 줌 값에 따른 비율 계산
           - 새 크기로 이미지 리사이즈
        3. 캔버스 업데이트
           - 리사이즈된 이미지 표시
           - 스크롤 영역 조정
        
        Args:
            value: 확대/축소 비율 (0-200)
        """
        if not hasattr(self, "img") or not self.img:
            return

        resized_image = self._resize_image_for_zoom(value)
        self._update_canvas_with_image(resized_image)

    def _resize_image_for_zoom(self, value):
        """
        줌 값에 따라 이미지 크기 조정
        
        처리 순서:
        1. 확대/축소 비율 계산
           - value를 백분율로 변환 (100 = 원본 크기)
        2. 새로운 크기 계산
           - 원본 크기에 비율 적용
        3. 이미지 리사이즈
           - LANCZOS 알고리즘 사용
        4. PhotoImage 객체 생성
           - 결과 이미지 저장
        
        Args:
            value: 확대/축소 비율 값 (0-400)
            
        Returns:
            tuple[int, int]: 조정된 이미지 크기 (width, height)
        """
        scale = float(value) / 100
        width = int(self.img.width * scale)
        height = int(self.img.height * scale)
        
        resized = self.img.resize((width, height), Image.Resampling.LANCZOS)
        self.result_image = ImageTk.PhotoImage(resized)
        return (width, height)

    def _update_canvas_with_image(self, size: tuple[int, int]) -> None:
        """
        캔버스 크기 및 이미지 업데이트
        
        처리 순서:
        1. 캔버스 크기 조정
           - 이미지 크기에 맞게 설정
        2. 스크롤 영역 설정
           - 이미지 크기만큼 스크롤 가능하도록 설정
        3. 이미지 표시
           - 캔버스 중앙에 이미지 배치
        
        Args:
            size: 이미지 크기 (width, height)
                width: 이미지 너비
                height: 이미지 높이
        """
        width, height = size
        canvas = self.result_preview.canvas
        
        # 캔버스 중심점 계산
        canvas_width = max(canvas.winfo_width(), width)
        canvas_height = max(canvas.winfo_height(), height)
        x_center = canvas_width // 2
        y_center = canvas_height // 2

        # 이미지 업데이트
        canvas.delete("all")
        canvas.create_image(x_center, y_center, image=self.result_image, anchor="center")
        canvas.configure(scrollregion=(0, 0, width, height))

    @ErrorHandler.handle_error
    def move_up(self):
        """
        선택된 파일을 위로 이동
        
        처리 순서:
        1. 현재 선택된 항목 확인
        2. 각 선택 항목 처리
           - 맨 위가 아닌 경우에만 이동
           - 이전 위치로 항목 이동
           - 이동된 항목 선택 상태 유지
        3. 미리보기 업데이트
           - 변경된 순서 반영
        """
        selected = self.list_file.curselection()
        for i in selected:
            if i > 0:
                text = self.list_file.get(i)
                self.list_file.delete(i)
                self.list_file.insert(i - 1, text)
                self.list_file.selection_set(i - 1)
        self.update_preview()

    @ErrorHandler.handle_error
    def move_down(self):
        """
        선택된 파일을 아래로 이동
        
        처리 순서:
        1. 현재 선택된 항목 확인
        2. 각 선택 항목 처리
           - 맨 아래가 아닌 경우에만 이동
           - 다음 위치로 항목 이동
           - 이동된 항목 선택 상태 유지
        3. 미리보기 업데이트
           - 변경된 순서 반영
        """
        selected = self.list_file.curselection()
        for i in reversed(selected):
            if i < self.list_file.size() - 1:
                text = self.list_file.get(i)
                self.list_file.delete(i)
                self.list_file.insert(i + 1, text)
                self.list_file.selection_set(i + 1)
        self.update_preview()

    def browse_save_path(self):
        """
        저장 경로 선택 다이얼로그 표시
        
        처리 순서:
        1. 저장 경로 선택 다이얼로그 표시
           - 초기 경로: 마지막 저장 경로
           - 제목: "저장 폴더를 선택하세요"
        2. 선택된 경로 처리
           - 경로 입력창 업데이트
           - 설정 파일 업데이트
           - 마지막 저장 경로 업데이트
        """
        folder_selected = filedialog.askdirectory(
            title="저장 폴더를 선택하세요",
            initialdir=self.result_opened_dir
        )
        
        if folder_selected:  # 폴더를 선택했을 경우
            self.result_opened_dir = folder_selected
            self.config["result_opened_dir"] = folder_selected
            
            # 엔트리 위젯 업데이트
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, folder_selected)

    @ErrorHandler.handle_error
    def update_preview(self):
        """
        미리보기 이미지 업데이트
        
        처리 순서:
        1. 선택된 이미지 확인
           - 단일 선택: 이미지 처리 및 표시
           - 다중 선택/선택 없음: 미리보기 초기화
        2. 결과 미리보기 업데이트
           - 병합 결과 표시
           - 스크롤 영역 조정
        """
        selected = self.list_file.curselection()
        file_count = self.list_file.size()
        
        if not selected:
            # 선택된 항목이 없음
            self.preview_frame.update_preview(
                file_count=file_count,
                selection_count=0
            )
            return
        
        if len(selected) > 1:
            # 다중 선택됨
            self.preview_frame.update_preview(
                file_count=file_count,
                selection_count=len(selected)
            )
            return
        
        # 단일 선택: 이미지 처리 및 표시
        image_path = self.list_file.get(selected[0])
        with Image.open(image_path) as img:
            processed = self._apply_image_transformations(img, image_path)
            self._update_preview_image(processed)

    @ErrorHandler.handle_error
    def _update_preview_image(self, processed_image: Image.Image) -> None:
        """
        처리된 이미지로 미리보기 업데이트
        
        처리 순서:
        1. 이미지 크기 조정
           - PREVIEW_WIDTH, PREVIEW_HEIGHT에 맞게 조정
        2. PhotoImage 객체 생성
           - 조정된 이미지로 PhotoImage 생성
        3. 미리보기 프레임 업데이트
           - PhotoImage와 상태 정보 전달
        
        Args:
            processed_image: 처리가 완료된 이미지
        """
        # 미리보기 크기에 맞게 이미지 조정
        width_ratio = PREVIEW_WIDTH / processed_image.width
        height_ratio = PREVIEW_HEIGHT / processed_image.height
        scale_ratio = min(width_ratio, height_ratio)
        
        new_width = int(processed_image.width * scale_ratio)
        new_height = int(processed_image.height * scale_ratio)
        
        resized = processed_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        
        # PhotoImage 생성 및 참조 유지
        self.preview_image = ImageTk.PhotoImage(resized)
        
        # 미리보기 업데이트 (PhotoImage 객체 전달)
        self.preview_frame.update_preview(
            image=self.preview_image,
            file_count=self.list_file.size(),
            selection_count=len(self.list_file.curselection())
        )

    @ErrorHandler.handle_error
    def save_config(self):
        """
        현재 설정 저장
        
        처리 순서:
        1. 옵션 프레임의 현재 설정 가져오기
           - 병합 옵션 (정렬/간격/형식)
           - 이미지 크기 설정
        2. 디렉토리 경로 설정 추가
           - 마지막 열기 경로
           - 결과물 저장 경로
        3. 설정 파일에 저장
           - ConfigManager를 통해 저장
        """
        config = self.option_frame.get_options()
        config.update({
            "last_opened_dir": self.last_opened_dir,
            "result_opened_dir": self.result_opened_dir
        })
        self.config_manager.save(config)

    @ErrorHandler.handle_error
    def start_merge(self):
        """
        이미지 병합 프로세스 시작
        
        처리 순서:
        1. 입력값 유효성 검증
           - 이미지 파일 존재 여부
           - 저장 경로 설정 여부
        2. 병합 옵션 설정
           - 정렬 방향 (수직/수평)
           - 이미지 간격
           - 저장 형식
        3. 이미지 병합 실행
           - 진행률 업데이트
           - 결과 이미지 생성
        4. 결과 이미지 저장
           - 저장 다이얼로그 표시
           - 완료 메시지 표시
        """
        if not self.validate_inputs():
            return
            
        self.save_config()
        
        # 현재 설정 가져오기
        options = {
            'width': self.option_frame.option_vars['width'].get(),
            'align': self.option_frame.option_vars['align'].get(),
            'space': self.option_frame.option_vars['space'].get(),
            'format': self.option_frame.option_vars['format'].get()
        }
        
        # 이미지 경로 리스트 생성
        image_paths = [self.list_file.get(i) for i in range(self.list_file.size())]
        
        # 이미지 병합 처리
        result_image, img_format = self.image_processor.merge_images(
            image_paths, 
            options,
            progress_callback=self.update_progress
        )
        
        # 저장 다이얼로그 표시 및 저장 처리
        self._save_result_image(result_image, img_format)

    @ErrorHandler.handle_error
    def _save_result_image(self, result_image: Image.Image, img_format: str):
        """
        결과 이미지 저장 처리
        
        처리 순서:
        1. 파일 형식에 따른 저장 옵션 설정
           - JPG/PNG 파일 형식 설정
           - 파일 확장자 필터 설정
        2. 저장 경로 선택 다이얼로그 표시
           - 초기 경로: 현재 설정된 저장 경로
        3. 저장 진행 중 대화상자 표시
           - 모달 다이얼로그로 표시
        4. 이미지 저장 및 미리보기 업데이트
           - 선택된 경로에 이미지 저장
           - 결과 미리보기 업데이트
        5. 완료 메시지 표시
           - 성공/실패 메시지 표시
        
        Args:
            result_image: 저장할 이미지 객체
            img_format: 저장할 이미지 형식 ('jpg' 또는 'png')
        """
        filetypes = []
        if img_format == "jpg":
            filetypes = [
                ("JPG 파일", "*.jpg"),
                ("PNG 파일", "*.png"),
                ("모든 파일", "*.*")
            ]
        else:
            filetypes = [
                ("PNG 파일", "*.png"),
                ("JPG 파일", "*.jpg"),
                ("모든 파일", "*.*")
            ]
            
        save_path = filedialog.asksaveasfilename(
            initialdir=self.path_entry.get(),
            defaultextension=f".{img_format}",
            filetypes=filetypes
        )

        if save_path:
            loading_window = self._show_saving_dialog()
            try:
                result_image.save(save_path)
                self.result_image_original = result_image
                self.result_preview.scale_preview.set(100)
                self.update_result_preview()
                ErrorHandler.show_info("완료", "이미지 병합이 완료되었습니다!")
                self.progress_var.set(100)
                self.progress_label.config(text="완료!")
            finally:
                loading_window.destroy()
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="대기중...")

    @ErrorHandler.handle_error
    def _show_saving_dialog(self):
        """
        저장 진행 중 다이얼로그 표시
        
        처리 내용:
        - 모달 다이얼로그 생성
        - 저장 중 메시지 표시
        - 부모 윈도우 비활성화
        
        Returns:
            생성된 다이얼로그 윈도우
        """
        loading_window = Toplevel(self.root)
        loading_window.title("저장중...")
        Label(loading_window, text="저장 중입니다. 잠시만 기다려주세요...").pack(padx=20, pady=20)
        loading_window.transient(self.root)
        loading_window.grab_set()
        loading_window.update()
        return loading_window

    @ErrorHandler.handle_error
    def validate_inputs(self) -> bool:
        """
        병합 시작 전 입력값 검증
        
        처리 순서:
        1. 이미지 파일 존재 여부 확인
           - 파일 없으면 경고 메시지 표시
        2. 저장 경로 설정 여부 확인
           - 경로 미설정 시 경고 메시지 표시
        
        Returns:
            bool: 검증 결과
                True: 모든 검증 통과
                False: 검증 실패
        """
        if self.list_file.size() == 0:
            ErrorHandler.show_warning("경고", "이미지 파일을 추가하세요")
            return False
            
        if not self.path_entry.get():
            ErrorHandler.show_warning("경고", "저장 경로를 선택하세요")
            return False
            
        return True
    
    @ErrorHandler.handle_error
    def update_progress(self, value: float):
        """
        진행률 업데이트
        
        처리 내용:
        1. 진행률 값 설정
        2. 진행률 텍스트 업데이트
        3. UI 강제 업데이트
        
        Args:
            value: 진행률 값 (0.0 ~ 100.0)
        """
        self.progress_var.set(value)
        self.progress_label.config(text=f"처리중... {int(value)}%")
        self.root.update()
    
    @ErrorHandler.handle_error
    def update_result_preview(self):
        """
        결과 미리보기 업데이트
        
        처리 순서:
        1. 캔버스 크기 가져오기
        2. 원본 이미지 복사
        3. 캔버스 크기에 맞게 이미지 크기 조정
        4. 미리보기 업데이트
        """
        # 캔버스 크기에 맞게 이미지 크기 조정
        canvas_width = self.result_preview.canvas.winfo_width()
        canvas_height = self.result_preview.canvas.winfo_height()
        
        self.img = self.result_image_original.copy()
        self.img.thumbnail((canvas_width, canvas_height))        
        self.result_image = ImageTk.PhotoImage(self.img)
        self.result_preview.update_preview(self.result_image)

    @ErrorHandler.handle_error
    def add_file(self):
        """
        파일 추가 다이얼로그 표시
        
        처리 순서:
        1. 파일 선택 다이얼로그 표시
        2. 선택된 파일 처리
        3. 마지막 디렉토리 업데이트
        4. 미리보기 업데이트
        """
        files = self._show_file_dialog()
        if files:
            self._update_last_directory(files[0])
            self._process_selected_files(files)
            self.update_preview()

    @ErrorHandler.handle_error
    def _show_file_dialog(self):
        """
        파일 선택 다이얼로그 표시
        
        Returns:
            선택된 파일 경로들의 튜플 또는 빈 튜플
        """
        return filedialog.askopenfilenames(
            title="이미지 파일을 선택하세요",
            filetypes=[
                ("이미지 파일", " ".join(f"*{fmt}" for fmt in SUPPORTED_FORMATS)),
                ("모든 파일", "*.*")
            ],
            initialdir=self.last_opened_dir
        )

    @ErrorHandler.handle_error
    def _update_last_directory(self, first_file):
        """
        마지막 작업 디렉토리 업데이트
        
        처리 내용:
        1. 선택된 파일의 디렉토리 경로 추출
        2. 마지막 작업 디렉토리 설정 업데이트
        3. 설정 파일에 저장
        
        Args:
            first_file: 선택된 첫 번째 파일의 경로
        """
        self.last_opened_dir = os.path.dirname(first_file)
        self.config["last_opened_dir"] = self.last_opened_dir

    @ErrorHandler.handle_error
    def _process_selected_files(self, files):
        """선택된 파일들 처리"""
        for file in files:
            existing_index = self._find_existing_file(file)
            if existing_index is not None:
                self._handle_duplicate_file(file, existing_index)
            else:
                self.list_file.insert(END, file)

    @ErrorHandler.handle_error
    def _find_existing_file(self, file):
        """
        파일 목록에서 중복 파일 검색
        
        Args:
            file: 검색할 파일
            
        Returns:
            중복된 파일의 인덱스 또는 None
        """
        for i in range(self.list_file.size()):
            if self.list_file.get(i) == file:
                return i
        return None

    @ErrorHandler.handle_error
    def _handle_duplicate_file(self, file, existing_index):
        """
        중복 파일 처리
        
        처리 순서:
        1. 덮어쓰기 확인 대화상자 표시
        2. 확인 시 이미지 상태 초기화
        3. 파일 목록 업데이트
        
        Args:
            file: 중복된 파일 경로
            existing_index: 기존 파일의 인덱스
        """
        if self._confirm_overwrite(file):
            self._reset_image_states(file)
            self._update_file_list(file, existing_index)

    @ErrorHandler.handle_error
    def _confirm_overwrite(self, file: str) -> bool:
        """
        파일 덮어쓰기 확인
        
        처리 순서:
        1. 덮어쓰기 확인 대화상자 표시
           - 파일명 표시
           - 경고 메시지 표시
        2. 사용자 선택 결과 반환
        
        Args:
            file: 덮어쓸 파일 경로
            
        Returns:
            bool: 덮어쓰기 여부
                True: 덮어쓰기 확인
                False: 덮어쓰기 취소
        """
        return messagebox.askyesno(
            "파일 중복",
            f"'{os.path.basename(file)}' 파일이 이미 목록에 있습니다.\n"
            "기존 파일을 덮어쓰시겠습니까?\n\n"
            "※ 덮어쓰기 시 해당 이미지의 필터와 회전 상태가 초기화됩니다."
        )

    @ErrorHandler.handle_error
    def _reset_image_states(self, file: str) -> None:
        """
        이미지 상태 초기화
        
        처리 순서:
        1. 필터 상태 초기화
           - 필터 프레임에서 이미지 상태 제거
        2. 이미지 변형 상태 초기화
           - 이미지 제어 프레임에서 이미지 상태 제거
        
        Args:
            file: 초기화할 이미지 파일 경로
        """
        if hasattr(self.filter_frame, 'remove_image'):
            self.filter_frame.remove_image(file)
        if hasattr(self.image_control_frame, 'remove_image'):
            self.image_control_frame.remove_image(file)

    @ErrorHandler.handle_error
    def _update_file_list(self, file, index):
        """
        파일 목록 업데이트
        
        처리 순서:
        1. 기존 항목 삭제
        2. 새 파일 삽입
        
        Args:
            file: 업데이트할 파일 경로
            index: 업데이트할 위치의 인덱스
        """
        self.list_file.delete(index)
        self.list_file.insert(index, file)

    @ErrorHandler.handle_error
    def remove_files(self):
        """
        선택된 파일 삭제
        
        처리 순서:
        1. 선택된 파일 목록 가져오기
        2. 각 파일별 상태 초기화
           - 필터 상태 초기화
           - 이미지 제어 상태 초기화
        3. 파일 목록에서 제거
           - 역순으로 삭제하여 인덱스 유지
        4. UI 상태 업데이트
           - 이미지 제어 프레임 초기화
           - 필터 프레임 초기화
        5. 미리보기 업데이트
           - 선택 해제 상태 반영
        """
        selected = self.list_file.curselection()
        
        # 선택된 이미지들의 필터 상태와 처리 상태 초기화
        for index in selected:
            image_path = self.list_file.get(index)
            # 필터 상태 초기화
            if hasattr(self.filter_frame, 'remove_image'):
                self.filter_frame.remove_image(image_path)
            # 이미지 제어 상태 초기화
            if hasattr(self.image_control_frame, 'remove_image'):
                self.image_control_frame.remove_image(image_path)
        
        # 리스트에서 선택된 항목 삭제
        for index in reversed(selected):
            self.list_file.delete(index)
        
        # 선택 삭제 후 선택 상태가 해제되므로 이미지 제어 버튼 비활성화
        self.image_control_frame.set_current_image(None)
        self.filter_frame.set_current_image(None)  # 필터 UI도 초기화
        self.update_preview()

    @ErrorHandler.handle_error
    def _process_single_image(self, image_path: str) -> None:
        """
        단일 이미지 처리 및 미리보기 업데이트
        
        처리 순서:
        1. 이미지 상태 가져오기
           - 회전/반전 상태 확인
           - 필터 상태 확인
        2. 이미지 변형 적용
           - 회전 적용
           - 반전 적용
        3. 이미지 필터 적용
           - 밝기/대비/채도 조정
           - 포스터화 효과 적용
        4. 미리보기 업데이트
           - 처리된 이미지로 미리보기 갱신
        
        Args:
            image_path: 처리할 이미지 파일 경로
        """
        with Image.open(image_path) as image:
            processed = self._apply_image_transformations(image, image_path)
            self._update_preview_image(processed)

    @ErrorHandler.handle_error
    def rotate_image(self, angle: int):
        """
        이미지 회전 처리
        
        처리 순서:
        1. 선택된 이미지 확인
        2. 회전 상태 업데이트
        3. 이미지 처리 및 미리보기 업데이트
        4. 리셋 카운트 업데이트
        
        Args:
            angle: 회전 각도 (양수: 시계방향, 음수: 반시계방향)
        """
        image_path = self._get_selected_image_path()
        if not image_path:
            return
        
        transform_state = self._ensure_transform_state(image_path)
        
        # 좌우 반전 상태에 따라 회전 각도 조정
        if transform_state.flipped:
            angle = -angle  # 반전 상태에서는 회전 방향을 반대로
        
        transform_state.add_rotation(angle)
        self._process_single_image(image_path)
        self.image_control_frame.update_reset_count()

    @ErrorHandler.handle_error
    def flip_image(self):
        """
        선택된 이미지 좌우 반전
        
        처리 순서:
        1. 현재 선택된 이미지 확인
        2. 이미지 상태 업데이트
           - 반전 상태 토글
           - 상태 변경 플래그 설정
        3. 미리보기 업데이트
           - 반전된 이미지 표시
        """
        image_path = self._get_selected_image_path()
        if not image_path:
            return
        
        transform_state = self._ensure_transform_state(image_path)
        transform_state.toggle_flip()
        
        self._process_single_image(image_path)
        self.image_control_frame.update_reset_count()

    @ErrorHandler.handle_error
    def apply_filter(self):
        """
        선택된 이미지에 필터 적용
        
        처리 순서:
        1. 현재 선택된 이미지 확인
        2. 필터 상태 업데이트
           - 밝기/대비/채도/포스터화 적용
        3. 이미지 처리 및 미리보기
           - 필터가 적용된 이미지 생성
           - 미리보기 업데이트
        """
        image_path = self._get_selected_image_path()
        if not image_path:
            return
        
        self._process_single_image(image_path)

    def browse_dest_path(self):
        """        저장 경로 선택 다이얼로그 표시
        
        처리 순서:
        1. 저장 경로 선택 다이얼로그 표시
           - 초기 경로: 마지막 저장 경로
        2. 선택된 경로 처리
           - 경로 입력창 업데이트
           - 설정 파일 업데이트
        """
        folder_selected = filedialog.askdirectory(
            title="저장 폴더를 선택하세요",
            initialdir=self.result_opened_dir
        )
        
        if folder_selected:  # 폴더를 선택했을 경우
            self.result_opened_dir = folder_selected
            self.config["result_opened_dir"] = folder_selected
            
            # 엔트리 위젯 업데이트
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, folder_selected)

    @ErrorHandler.handle_error
    def reset_current_image_control(self):
        """
        현재 선택된 이미지의 회전/반전 상태 초기화
        
        처리 순서:
        1. 선택된 이미지 확인
           - 단일 선택 여부 확인
           - 이미지 경로 가져오기
        2. 변형 상태 초기화
           - 회전 각도 초기화
           - 반전 상태 초기화
        3. 이미지 처리 및 미리보기
           - 초기화된 상태로 이미지 처리
           - 미리보기 업데이트
        4. UI 상태 업데이트
           - 리셋 카운트 업데이트
        """
        image_path = self._get_selected_image_path()
        if not image_path:
            return
        
        transform_state = self._ensure_transform_state(image_path)
        transform_state.reset()
        self._process_single_image(image_path)
        self.image_control_frame.update_reset_count()
    
    def reset_all_image_controls(self):
        """
        모든 이미지의 회전/반전 상태 초기화
        
        처리 순서:
        1. 이미지 상태 존재 여부 확인
           - 초기화할 상태가 있는지 확인
        2. 모든 이미지의 변형 상태 초기화
           - 각 이미지의 회전/반전 상태 초기화
        3. 현재 선택된 이미지 처리
           - 선택된 이미지 확인
           - 미리보기 업데이트
        4. UI 상태 업데이트
           - 리셋 카운트 업데이트
        """
        if not self.image_control_frame.image_states:
            return
        
        for state in self.image_control_frame.image_states.values():
            state.reset()
        
        # 현재 선택된 이미지가 있다면 미리보기 업데이트
        image_path = self._get_selected_image_path()
        if image_path:
            self._process_single_image(image_path)
        
        self.image_control_frame.update_reset_count()

    def _apply_image_transformations(self, image: Image.Image, image_path: str) -> Image.Image:
        """
        이미지에 회전/반전/필터 적용
        
        처리 순서:
        1. 이미지 복사본 생성
        2. 회전/반전 상태 적용
           - 회전 각도 적용 (expand=True)
           - 좌우 반전 적용
        3. 필터 상태 적용
           - 밝기/대비/채도/포스터화 적용
        
        Args:
            image: 원본 이미지
            image_path: 이미지 파일 경로
            
        Returns:
            Image.Image: 모든 변형이 적용된 이미지
        """
        processed = image.copy()
        
        # 회전 및 반전 상태 적용
        transform_state = self._ensure_transform_state(image_path)
        if transform_state.rotation:
            processed = processed.rotate(transform_state.rotation, expand=True)
        if transform_state.flipped:
            processed = processed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        
        # 필터 적용
        if image_path in self.filter_frame.filter_states:
            filter_state = self.filter_frame.filter_states[image_path]
            processed = self.image_processor.apply_filters(processed, filter_state)
        
        return processed

    def _ensure_transform_state(self, image_path: str) -> ImageTransformState:
        """
        이미지의 변형 상태 객체 반환 (없으면 생로 생성)
        
        처리 순서:
        1. 이미지 경로로 상태 객체 검색
           - image_states 딕셔너리에서 검색
        2. 상태 객체가 없으면 새로 생성
           - ImageTransformState 인스턴스 생성
        3. 상태 객체 반환
           - 기존 또는 새로 생성된 객체
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            ImageTransformState: 이미지의 변형 상태 객체
                회전/반전 상태 정보를 포함
        """
        if image_path not in self.image_control_frame.image_states:
            self.image_control_frame.image_states[image_path] = ImageTransformState()
        return self.image_control_frame.image_states[image_path]

    def _get_selected_image_path(self) -> Optional[str]:
        """
        현재 선택된 이미지 경로 반환
        
        처리 순서:
        1. 리스트박스 선택 항목 확인
           - 선택된 항목 수 확인
        2. 선택 상태 검증
           - 단일 선택: 해당 경로 반환
           - 선택 없음/다중 선택: None 반환
        
        Returns:
            str | None: 선택된 이미지 경로 또는 None
                - 단일 선택: 해당 이미지 경로
                - 선택 없음: None
                - 다중 선택: None
        """
        selected = self.list_file.curselection()
        if len(selected) == 1:  # 단일 선택인 경우만 처리
            return self.list_file.get(selected[0])
        return None

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # 드래그 앤 드롭 지원 Tk 인스턴스 생성
    app = ImageMergerApp(root)  # 애플리케이션 인스턴스 생성
    root.mainloop()  # 메인 이벤트 루프 시작



