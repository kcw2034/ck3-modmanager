# CK3 Mod Manager - Release Notes

## 버전 1.0.0

### 주요 기능

#### 모드 관리
- ✅ Playset 편집 및 로드 순서 조정 (Drag & Drop)
- ✅ 모드 활성화/비활성화
- ✅ Mod Library에서 Playset으로 Drag & Drop 추가
- ✅ 모드 제거 (버튼 클릭 또는 Delete 키)
- ✅ 검색 기능

#### 충돌 감지
- ✅ 실시간 파일 충돌 감지
- ✅ 시각적 경고 아이콘 (⚠️)
- ✅ 충돌 모드 툴팁
- ✅ 파일 스캔 캐싱으로 성능 최적화

#### UI/UX
- ✅ Side-by-Side 레이아웃 (Active Playset + Mod Library)
- ✅ 컴팩트한 디자인
- ✅ 다크 테마
- ✅ Launch Game 버튼 (Steam 연동)

### 설치 방법

1. `CK3-Mod-Manager-macOS.zip` 다운로드
2. 압축 해제
3. `CK3 Mod Manager.app`을 Applications 폴더로 이동 (선택사항)
4. 앱 실행
   - 처음 실행 시 "확인되지 않은 개발자" 경고가 뜰 수 있습니다
   - **해결 방법**: 우클릭 → 열기 → 열기 클릭

### 시스템 요구사항
- macOS 11.0 이상
- Apple Silicon (M1/M2/M3) 또는 Intel
- Crusader Kings III 설치 필요

### 알려진 이슈
- 첫 실행 시 macOS 보안 경고 (Gatekeeper)
  - 앱을 우클릭 → "열기"로 실행하면 해결됩니다

### 기술 스택
- Python 3.11
- PySide6 (Qt)
- PyInstaller

---

**다운로드**: [Releases](https://github.com/YOUR_USERNAME/ck3-modmanager/releases)
