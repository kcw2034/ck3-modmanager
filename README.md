# CK3 Mod Manager

Crusader Kings 3용 GUI 기반 모드 관리 도구입니다. Paradox Launcher의 데이터베이스를 직접 읽고 수정하여 모드를 관리할 수 있습니다.

## 주요 기능

### 모드 관리
- **Playset 편집**: 드래그 앤 드롭으로 모드 로드 순서 조정
- **모드 활성화/비활성화**: 체크박스로 간편하게 관리
- **모드 추가**: Drag & Drop으로 라이브러리에서 Playset으로 즉시 추가
- **모드 제거**: 선택 후 버튼 클릭 또는 `Delete` 키로 Playset에서 제거
- **검색 기능**: Mod Library에서 모드명으로 빠른 검색

### 충돌 감지
- **실시간 파일 충돌 감지**: 활성화된 모드 간 파일 충돌을 자동으로 감지
- **시각적 경고**: 충돌이 있는 모드에 ⚠️ 아이콘 표시
- **툴팁**: 마우스를 올리면 충돌 대상 모드 목록 확인 가능
- **캐싱**: 성능 최적화를 위해 파일 목록을 메모리에 캐싱

### UI & UX
- **Side-by-Side 레이아웃**: 좌측 Active Playset, 우측 Mod Library를 동시에 표시
- **컴팩트 디자인**: 여백을 최소화한 실속 있는 인터페이스
- **다크 테마**: Fusion 스타일 기반의 세련된 다크 UI
- **게임 실행**: Launch Game 버튼으로 Steam을 통해 CK3 즉시 실행

### Mac App
- **독립 실행형 앱**: PyInstaller로 빌드된 `.app` 번들 (`dist/CK3 Mod Manager.app`)
- **터미널 불필요**: Finder에서 더블 클릭으로 실행 가능

## 프로젝트 구조

```tree
ck3-mod-manager/
├── src/
│   └── ck3_mod_manager/
│       ├── main.py              # 진입점
│       ├── analyzer.py          # 모드 파일 분석 및 충돌 감지
│       ├── database/
│       │   └── launcher_db.py   # Launcher DB 연동
│       └── gui/
│           └── main_window.py   # PySide6 GUI
├── dist/
│   └── CK3 Mod Manager.app     # 빌드된 Mac 앱
├── scripts/
│   └── inspect_db.py           # DB 스키마 검사 도구
├── tests/
├── pyproject.toml
├── README.md
└── .gitignore
```

## 설치 및 실행

### 개발 모드
```bash
# UV 사용 (권장)
uv run src/ck3_mod_manager/main.py

# 또는 직접 실행
python src/ck3_mod_manager/main.py
```

### Mac App 실행
```bash
# Finder에서 더블 클릭 또는
open "dist/CK3 Mod Manager.app"
```

## 기술 스택
- **Python 3.11+**
- **PySide6**: Qt 기반 GUI
- **SQLite3**: Paradox Launcher 데이터베이스 연동
- **PyInstaller**: Mac App 패키징
- **UV**: 패키지 관리

## 라이선스
MIT