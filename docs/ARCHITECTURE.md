# Image Editing And Merging App 설계서

## 1. 프로젝트 개요

### 1.1 프로그램 소개

Image Editing And Merging App은 여러 장의 이미지를 사용자가 원하는 방식으로 편집하고 하나의 이미지로 병합할 수 있는 GUI 기반 응용 프로그램입니다.

### 1.2 주요 기능

- 이미지 파일 관리 (추가/삭제/순서 변경)
- 드래그 앤 드롭 지원
- 이미지 편집 (회전/반전/필터)
- 이미지 병합 (수직/수평)
- 실시간 미리보기
- 설정 저장/불러오기

### 1.3 기술 스택

- 언어: Python 3.12.4
- GUI: tkinter, tkinterdnd2 0.4.2
- 이미지 처리: Pillow (PIL) 10.3.0
- 설정 관리: JSON
- 오류 처리: Python logging

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
project_root/
├── src/
│ ├── main.py # 메인 애플리케이션
│ ├── ui_components.py # UI 컴포넌트
│ ├── image_processor.py # 이미지 처리 로직
│ ├── config_manager.py # 설정 관리
│ ├── error_handler.py # 에러 처리
│ └── constants.py # 상수 정의
│
├── config/
│ └── config.json # 설정 파일
│
└── logs/
└── app.log # 로그 파일
```

### 2.2 모듈별 역할

#### 2.2.1 main.py (ImageMergerApp)

- 애플리케이션의 진입점
- UI 초기화 및 이벤트 처리
- 주요 메서드:

1. 초기화 관련:

   - **init**(self, root): 애플리케이션 초기화
   - setup_window(self): 윈도우 설정
   - setup_shortcuts(self): 단축키 설정
   - create_frames(self): UI 프레임 생성
   - create_left_frame_widgets(self): 좌측 패널 구성
   - create_right_frame_widgets(self): 우측 패널 구성
   - create_file_frame(self): 파일 목록 프레임 생성
   - init_variables(self): 변수 초기화
   - setup_dnd(self): 드래그 앤 드롭 설정

2. 이벤트 핸들러:

   - on_drop(self, event): 파일 드롭 처리
   - on_list_select(self, event): 목록 선택 처리
   - on_align_change(self): 정렬 변경 처리
   - on_zoom(self, value): 확대/축소 처리

3. 파일 관리:

   - add_file(self): 파일 추가
   - remove_files(self): 파일 삭제
   - move_up(self): 선택 항목 위로 이동
   - move_down(self): 선택 항목 아래로 이동

4. 이미지 처리:

   - rotate_image(self, angle): 이미지 회전
   - flip_image(self): 이미지 반전
   - apply_filter(self): 필터 적용
   - reset_current_image_control(self): 현재 이미지 초기화
   - reset_all_image_controls(self): 전체 이미지 초기화

5. 저장 관련:
   - start_merge(self): 병합 시작
   - save_config(self): 설정 저장
   - browse_dest_path(self): 저장 경로 선택

- 단축키 지원:
  - Ctrl + O: 파일 추가
  - Delete: 파일 삭제
  - Ctrl + S: 병합 시작

#### 2.2.2 ui_components.py

##### PreviewFrame

이미지 미리보기 프레임

주요 기능:

1. 선택된 이미지 미리보기 표시
2. 상황별 안내 메시지 표시
3. 고정된 크기로 이미지 표시
4. 이미지 비율 유지

5. 초기화/UI 구성:

   - **init**(self, parent)
   - setup_ui(self)
     - 고정 크기 프레임 생성 (PREVIEW_WIDTH x PREVIEW_HEIGHT)
     - 캔버스 생성 (배경: PREVIEW_BG)
     - 기본 텍스트 표시

6. 이미지 표시:
   - update_preview(self, image=None, file_count=0, selection_count=0)
     - 이미지 또는 상태별 메시지 표시
   - \_show_default_text(self, message)
     - 안내 메시지 중앙 표시

##### ResultPreviewFrame

병합 결과 미리보기 프레임

기능:

1. 병합 결과 이미지 미리보기
2. 이미지 확대/축소 (줌)
3. 스크롤바를 통한 이미지 탐색

4. 초기화/UI 구성:

   - **init**(self, parent)
   - setup_ui(self)
     - 캔버스 생성
     - 스크롤바 설정 (가로/세로)
     - 줌 슬라이더 (0-400%)
   - setup_scrollbars(self)

5. 이미지 표시:
   - update_preview(self, image=None)
   - show_error_message(self)

##### OptionFrame

옵션 설정 프레임

기능:

1. 이미지 너비 설정 (원본유지/1024/800/640)
2. 이미지 간격 설정 (없음/좁게/보통/넓게)
3. 저장 포맷 설정 (PNG/JPG)
4. 정렬 방향 설정 (수직/수평)

5. 초기화/UI 구성:

   - **init**(self, parent, config, on_align_change)
   - setup_ui(self)
     - 너비/간격/포맷/정렬 콤보박스 생성

6. 옵션 관리:

   - get_options(self) -> Dict[str, str]
     - 현재 설정된 모든 옵션값 반환

##### FileListFrame

파일 목록 관리 프레임

기능:

1. 파일 목록 표시 및 관리
2. 드래그 앤 드롭 지원
3. 다중 선택 지원
4. 파일 순서 변경

5. 초기화/UI 구성:

   - **init**(self, parent)
   - setup_ui(self)
     - 리스트박스 생성 (다중 선택 지원)
     - 스크롤바 설정
   - setup_buttons(self)
     - 파일 추가/삭제 버튼
     - 순서 이동 버튼 (↑/↓)

6. 이벤트 처리:

   - on_select(self, event)
   - on_add(self)
   - on_remove(self)
   - on_move_up(self)
   - on_move_down(self)

##### ImageControlFrame

이미지 제어 프레임

기능:

1. 이미지 회전 (좌/우 90도)
2. 이미지 좌우 반전
3. 현재/전체 이미지 초기화

4. 초기화/UI 구성:

   - **init**(self, parent)
   - setup_ui(self)
     - 회전 버튼 (← 90°, 90° →)
     - 좌우반전 버튼
     - 초기화 버튼

5. 이미지 제어:

   - rotate_left(self)
   - rotate_right(self)
   - toggle_flip(self)

6. 상태 관리:

   - set_current_image(self, image_path, selected_count=1)
   - update_reset_count(self)
   - reset_current_image(self)
   - reset_all_images(self)
   - remove_image(self, image_path)

##### ImageFilterFrame

이미지 필터 조절 프레임

기능:

1. 밝기 조절 (0.0-3.0)
2. 대비 조절 (0.0-3.0)
3. 채도 조절 (0.0-3.0)
4. 포스터화 효과 (1.0-3.0)

5. 초기화/UI 구성:

   - **init**(self, parent)
   - create_variables(self)
   - setup_ui(self)
   - create_filter_control(self, name, min_val, max_val, var)

6. 필터 관리:

   - update_filter(self, filter_name, label, value)
   - reset_filter(self, filter_name)
   - reset_current_image(self)
   - reset_all_filters(self)

7. 상태 관리:
   - update_reset_count(self)
   - remove_image(self, image_path)
   - set_current_image(self, image_path, selected_count=1)
   - \_get_var_name(self, name)

#### 2.2.3 image_processor.py

##### ImageProcessor

이미지 처리 클래스

주요 기능:

1. 이미지 크기 조정
2. 이미지 병합 (수직/수평)
3. 이미지 필터 적용
4. 이미지 회전/반전

처리 가능한 이미지 형식: PNG, JPG, JPEG

5. 이미지 처리:

   - process_images(self, images, width, align, progress_callback=None)
     - 이미지 크기 조정 (원본유지/너비/높이)
     - LANCZOS 알고리즘 사용
     - 진행률 콜백 지원

6. 병합 관련:

   - merge_images(self, image_paths, options, progress_callback=None)
     - 이미지 로드 및 전처리 (0-30%)
     - 크기 조정 (30-60%)
     - 병합 처리 (60-100%)
   - merge_images_with_spacing(self, images, spacing, align, progress_callback=None)
     - 간격을 포함한 이미지 병합

7. 필터/변형:

   - apply_filters(self, image, filters)
     - 필터 순차 적용 (밝기/대비/채도/포스터화)
   - \_apply_image_controls(self, img, state)
     - 회전/반전 적용

##### ImageTransformState

이미지 변형(회전/반전) 상태 관리 클래스

관리하는 상태:

1. rotation: 회전 각도 (0-359)
2. flipped: 좌우 반전 여부 (True/False)
3. modified: 상태 변경 여부 (True/False)

4. 상태 관리:

   - set_rotation(self, angle): 회전 각도 설정
   - add_rotation(self, angle): 현재 각도에 추가 회전
   - toggle_flip(self): 좌우 반전 토글
   - reset(self): 상태 초기화
   - is_default(self): 기본 상태 확인
   - get_state(self): 현재 상태 반환

##### ImageFilterState

이미지 필터 상태 관리 클래스

관리하는 필터:

- brightness: 밝기 (0.0-3.0)
- contrast: 대비 (0.0-3.0)
- saturation: 채도 (0.0-3.0)
- posterize: 포스터화 (1.0-3.0)

1. 필터 관리:
   - set_filter(self, filter_name, value): 필터값 설정
   - reset(self): 필터 초기화
   - is_default(self): 기본값 여부 확인
   - get_state(self): 현재 상태 반환

#### 2.2.4 config_manager.py

##### ConfigManager

설정 관리 클래스

주요 기능:

1. 설정 파일 생성/로드/저장
2. 설정값 유효성 검증
3. 기본 설정 관리

설정 항목:

- width: 이미지 너비 ('원본유지' 또는 픽셀값)
- space: 이미지 간격 ('없음', '좁게', '보통', '넓게')
- format: 저장 포맷 ('PNG' 또는 'JPG')
- align: 정렬 방향 ('수직' 또는 '수평')
- last_opened_dir: 마지막으로 열었던 디렉토리
- result_opened_dir: 결과물 저장 디렉토리

4. 초기화/설정:

   - **init**(self): 설정 관리자 초기화
     - 설정 디렉토리 생성
     - 기본 설정값 초기화
   - \_create_default_config(): 기본 설정 파일 생성
     - DEFAULT_CONFIG를 JSON으로 저장

5. 설정 관리:

   - load(): 설정 파일 로드 및 검증
     - 파일 존재 확인
     - JSON 파일 읽기 (UTF-8)
     - 설정값 유효성 검증
   - save(self, new_config): 새로운 설정 검증 및 저장
     - 설정값 유효성 검증
     - JSON 형식으로 저장

6. 유효성 검증:

   - \_validate_config(self, config): 설정값 유효성 검증
     - 필수 키 존재 여부 확인
     - 옵션값 유효성 검증
     - 디렉토리 경로 검증
   - \_validate_directory(self, config, key): 디렉토리 경로 검증
     - 경로 존재 확인
     - 없는 경로는 기본값으로 대체

#### 2.2.5 error_handler.py

##### ErrorHandler

에러 처리 및 로깅 클래스

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

5. 예외 처리:

   - @handle_error: 전역 예외 처리 데코레이터
     - FileNotFoundError: 파일 없음 처리
     - PermissionError: 권한 부족 처리
     - ValueError: 잘못된 입력값 처리
     - UnidentifiedImageError: 미지원 형식 처리
     - MemoryError: 메모리 부족 처리
     - PIL.Image.DecompressionBombError: 이미지 크기 초과 처리

6. 로깅 관리:

   - setup_logging(): 로깅 시스템 초기화
     - 로그 레벨: INFO
     - 출력 포맷: 시간 - 모듈명 - 로그레벨 - 메시지
     - 파일/콘솔 핸들러 설정
   - log_error/warning/info(): 로그 레벨별 기록

7. 사용자 알림:

   - show_error/warning/info(): 메시지박스 표시
     - show_error: 빨간색 X 아이콘
     - show_warning: 노란색 느낌표 아이콘
     - show_info: 파란색 i 아이콘

8. 설정 검증:

   - validate_required_keys(cls, config, required_keys): 필수 키 존재 여부 검증
   - validate_option(cls, value, valid_options, option_name): 설정값 유효성 검증
   - handle_invalid_config(cls): 잘못된 설정 파일 처리

#### 2.2.6 constants.py

##### Constants

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

6. 경로 관련:

   - ROOT_DIR: 프로젝트 루트 디렉토리
   - CONFIG_DIR: 설정 파일 디렉토리
   - LOGS_DIR: 로그 파일 디렉토리
   - CONFIG_FILE: 설정 파일 경로
   - LOG_FILE: 로그 파일 경로
   - DEFAULT_PICTURES_DIR: 기본 사진 디렉토리

7. UI 관련:

   - WINDOW_SIZE: 메인 윈도우 크기 (1500, 900)
   - DEFAULT_PADDING: UI 요소 간 기본 여백 (5px)

8. 이미지 처리:

   - SUPPORTED_FORMATS: 지원하는 이미지 형식 (.png, .jpg, .jpeg)
   - SPACING_OPTIONS: 이미지 간격 옵션
     - "없음": 0px (이미지 간 간격 없음)
     - "좁게": 30px (최소 간격)
     - "보통": 60px (중간 간격)
     - "넓게": 90px (최대 간격)

9. UI 옵션:

   - WIDTH_OPTIONS: 이미지 너비 옵션 ("원본유지", "1024", "800", "640")
   - SPACE_OPTIONS: 간격 옵션 ("없음", "좁게", "보통", "넓게")
   - FORMAT_OPTIONS: 저장 포맷 ("PNG", "JPG")
   - ALIGN_OPTIONS: 정렬 방향 ("수직", "수평")

10. 미리보기:

    - PREVIEW_WIDTH: 미리보기 영역 너비 (400px)
    - PREVIEW_HEIGHT: 미리보기 영역 높이 (300px)
    - PREVIEW_BG: 미리보기 배경색 ('white')
    - PREVIEW_TEXT_NO_FILES: "이미지 파일을 추가하세요" (파일 목록이 비어있을 때)
    - PREVIEW_TEXT_NO_SELECTION: "이미지를 선택하세요" (파일은 있지만 선택되지 않았을 때)
    - PREVIEW_TEXT_MULTI_SELECTION: "하나의 파일만 선택하세요" (여러 파일이 선택되었을 때)

## 3. 핵심 기능 상세

### 3.1 이미지 편집

#### 3.1.1 이미지 변형

- 회전 기능
  - 90도 단위 회전
  - 반전 상태 고려한 방향 조정
- 반전 기능
  - 좌우 반전 토글
  - 상태 저장 및 복원

#### 3.1.2 이미지 필터

- 밝기 조절: 0.0-3.0 (ImageEnhance.Brightness)
- 대비 조절: 0.0-3.0 (ImageEnhance.Contrast)
- 채도 조절: 0.0-3.0 (ImageEnhance.Color)
- 포스터화: 1.0-3.0 (팔레트 변환)

### 3.2 이미지 병합

#### 3.2.1 병합 프로세스

- process_images(self, images, width, align, progress_callback=None)

  - 이미지 크기 조정
  - LANCZOS 알고리즘 사용
  - 진행률 콜백:
    - 각 이미지 처리마다 진행률 계산
    - progress = (i + 1) / total \* 100
    - progress_callback(progress) 호출

- merge_images_with_spacing(self, images, spacing, align, progress_callback=None)
  - 이미지 병합 처리
  - 간격 옵션:
    - "없음": 0px
    - "좁게": 30px
    - "보통": 60px
    - "넓게": 90px
  - 간격 적용 (없음/좁게/보통/넓게)
  - 수직/수평 정렬 지원
  - 수직: 이미지를 세로로 배치
  - 수평: 이미지를 가로로 배치
  - 진행률 콜백 지원

### 3.3 이벤트 처리

#### 3.3.1 이벤트 흐름

1. 파일 관리 이벤트

   - 파일 추가:
     - FileListFrame -> ImageMergerApp.add_file()
     - 지원 형식 검증 (SUPPORTED_FORMATS)
     - 중복 파일 필터링 (이미 목록에 있는 파일은 제외)
     - 파일 목록 업데이트
   - 드래그 앤 드롭:
     - FileListFrame -> ImageMergerApp.on_drop()
     - 드롭된 파일 경로 파싱
     - 지원 형식 및 중복 검증
     - 파일 목록 업데이트
   - 파일 선택:
     - FileListFrame -> ImageMergerApp.on_list_select()
     - 단일/다중 선택 처리
     - 미리보기 업데이트
     - 필터/변형 상태 복원
     - 컨트롤 활성화/비활성화

2. 이미지 편집 이벤트

   - 회전/반전:
     - ImageControlFrame -> ImageMergerApp
     - on_rotate(angle): 회전 상태 업데이트
     - on_flip(): 반전 상태 토글
     - 미리보기 실시간 업데이트
   - 필터 변경:
     - ImageFilterFrame -> ImageMergerApp.apply_filter()
     - 필터 상태 저장
     - 미리보기 실시간 업데이트

3. 옵션 변경 이벤트
   - 정렬 방향:
     - OptionFrame -> ImageMergerApp.on_align_change()
     - 결과 미리보기 업데이트
   - 줌 레벨:
     - ResultPreviewFrame -> ImageMergerApp.on_zoom()
     - 결과 미리보기 크기 조정

## 4. 오류 처리

### 4.1 주요 예외 처리

- 예외 처리 데코레이터 사용:

  ```python
  @ErrorHandler.handle_error
  def function_name(self):
      # 함수 내용
  ```

````

- 처리되는 예외 종류:
  - FileNotFoundError: "파일을 찾을 수 없습니다"
  - PermissionError: "파일 접근 권한이 없습니다"
  - UnidentifiedImageError: "지원하지 않는 이미지 형식입니다"
  - MemoryError: "메모리가 부족합니다"
  - PIL.Image.DecompressionBombError: "이미지가 너무 큽니다"
  - ValueError: 설정값 검증 실패시

### 4.2 로깅 시스템

- 로그 설정 (setup_logging):

  - 로그 레벨: INFO
  - 로그 형식: 시간 - 모듈 - 레벨 - 메시지
  - 파일 핸들러: logs/app.log (UTF-8)
  - 스트림 핸들러: 콘솔 출력

- 로그 메서드:
  ```python
  ErrorHandler.log_error("에러 메시지")
  ErrorHandler.log_warning("경고 메시지")
  ErrorHandler.log_info("정보 메시지")
  ```

## 5. 설정 관리

### 5.1 설정 파일 구조

- 필수 설정 항목:

  - width: 이미지 너비 ("원본유지", "1024", "800", "640")
  - space: 이미지 간격 ("없음", "좁게", "보통", "넓게")
  - format: 저장 포맷 ("PNG", "JPG")
  - align: 정렬 방향 ("수직", "수평")
  - last_opened_dir: 마지막으로 열었던 디렉토리
  - result_opened_dir: 결과물 저장 디렉토리

- 기본값:
  - DEFAULT_CONFIG = {
    "width": "원본유지",
    "space": "없음",
    "format": "PNG",
    "align": "수직",
    "last_opened_dir": DEFAULT_PICTURES_DIR,
    "result_opened_dir": DEFAULT_PICTURES_DIR
    }

## 6. UI 레이아웃

### 6.1 좌측 패널

- OptionFrame (LabelFrame)

  - 너비/간격/포맷/정렬 콤보박스
  - 설정값 관리 및 변경 이벤트 처리
  - 기본값: config.json에서 로드

- ImageFilterFrame (LabelFrame)

  - 필터 슬라이더 (밝기/대비/채도/포스터화)
  - 필터 초기화 버튼 (현재/전체)
  - 필터 상태 관리 (ImageFilterState)
  - 실시간 미리보기 업데이트

- PreviewFrame (LabelFrame)

  - 너비: PREVIEW_WIDTH (400px)
  - 높이: PREVIEW_HEIGHT (300px)
  - 배경: PREVIEW_BG ('white')
  - 상태별 메시지 표시:
    - 파일 없음: PREVIEW_TEXT_NO_FILES
    - 선택 없음: PREVIEW_TEXT_NO_SELECTION
    - 다중 선택: PREVIEW_TEXT_MULTI_SELECTION

- ImageControlFrame (LabelFrame)

  - 회전 버튼 (← 90°, 90° →)
  - 좌우반전 버튼
  - 초기화 버튼 (현재/전체)
  - 변형 상태 관리 (ImageTransformState)

- FileListFrame (LabelFrame)
  - 리스트박스 (다중 선택 지원)
  - 파일 관리 버튼 (추가/삭제)
  - 순서 이동 버튼 (↑/↓)
  - 드래그 앤 드롭 지원

### 6.2 우측 패널 (right_frame)

- ResultPreviewFrame (LabelFrame)

  - 스크롤바 지원 (가로/세로)
  - 확대/축소 기능 (0-400%)
  - 병합 결과 미리보기

- 하단 프레임

  - 저장 경로 입력/선택
  - 진행률 표시바
  - 시작/닫기 버튼

- 저장 옵션
  - 너비 선택 (WIDTH_OPTIONS)
  - 간격 선택 (SPACING_OPTIONS)
  - 포맷 선택 (FORMAT_OPTIONS)
  - 정렬 선택 (ALIGN_OPTIONS)

## 7. 설치 및 실행

### 7.1 요구사항

- Python 3.12.4
- 필수 패키지:
  - tkinter: GUI 구현
  - tkinterdnd2 0.4.2: 드래그 앤 드롭 지원
  - Pillow (PIL) 10.3.0: 이미지 처리

### 7.2 실행 방법

1. 프로젝트 루트 디렉토리로 이동
2. 실행 명령:
   ```bash
   python src/main.py
   ```
````
