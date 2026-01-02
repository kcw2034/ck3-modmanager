from pathlib import Path
import os

# 프로젝트 루트 디렉토리 (절대 경로)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# 데이터베이스 경로 (환경변수 DB_PATH가 있으면 사용, 없으면 프로젝트 루트의 ck3_mods.db 사용)
DB_PATH = Path(os.path.expanduser("~/Documents/Paradox Interactive/Crusader Kings III/launcher-v2.sqlite.backup"))