# GitHub Release 배포 가이드

## 1. GitHub Repository 생성
```bash
cd /Users/kimchan-woo/Desktop/kcw/ck3-modmanager
git init
git add .
git commit -m "Initial commit: CK3 Mod Manager v1.0.0"
```

GitHub에서 새 저장소 생성 후:
```bash
git remote add origin https://github.com/YOUR_USERNAME/ck3-modmanager.git
git branch -M main
git push -u origin main
```

## 2. GitHub Release 생성

1. GitHub 저장소 페이지로 이동
2. 우측 "Releases" → "Create a new release" 클릭
3. 태그 생성: `v1.0.0`
4. Release 제목: `CK3 Mod Manager v1.0.0`
5. 설명: `RELEASE.md` 내용 복사
6. 파일 업로드:
   - `dist/CK3-Mod-Manager-macOS.zip` (약 50-100MB)

## 3. Release Notes 작성

```markdown
# CK3 Mod Manager v1.0.0

Crusader Kings 3용 모드 관리 도구의 첫 번째 공식 릴리즈입니다.

## 📥 다운로드
- [CK3-Mod-Manager-macOS.zip](링크) - macOS용 (Apple Silicon / Intel)

## ✨ 주요 기능
- ✅ Playset 편집 및 드래그 앤 드롭
- ✅ 실시간 모드 충돌 감지
- ✅ Drag & Drop으로 모드 추가
- ✅ 다크 테마 UI
- ✅ Steam 연동 게임 실행

## 📋 설치 방법
1. ZIP 파일 다운로드 및 압축 해제
2. `CK3 Mod Manager.app`을 Applications 폴더로 이동
3. 앱 실행
   - 첫 실행 시: 우클릭 → "열기" → "열기" 클릭

## 💻 시스템 요구사항
- macOS 11.0 이상
- Crusader Kings III 설치 필요

## 🐛 버그 리포트
[Issues](https://github.com/YOUR_USERNAME/ck3-modmanager/issues)에서 버그를 신고해 주세요.
```

## 4. 파일 위치
- 앱 번들: `dist/CK3 Mod Manager.app/`
- 압축 파일: `dist/CK3-Mod-Manager-macOS.zip`
- Release Notes: `RELEASE.md`

## 5. 추가 최적화 (선택사항)

### 코드 서명 (macOS)
```bash
# Apple Developer 계정 필요
codesign --force --deep --sign "Developer ID Application: YOUR_NAME" "dist/CK3 Mod Manager.app"
```

### Notarization (macOS)
Apple에 앱을 공증받으면 Gatekeeper 경고가 나타나지 않습니다.
- 요구사항: Apple Developer Program 가입 ($99/년)
