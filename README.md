# ck3-mod-manager

```tree
ck3-mod-manager/
├── src/
│   └── ck3_mod_manager/
│       ├── __init__.py
│       ├── cli.py              # Typer CLI 진입점
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py   # SQLite 연결 관리
│       │   └── models.py       # 데이터 모델
│       ├── services/
│       │   ├── __init__.py
│       │   ├── mod_service.py  # 모드 활성화/비활성화 로직
│       │   └── order_service.py # 로드 순서 관리
│       └── utils/
│           ├── __init__.py
│           └── config.py       # 설정 (파일 경로 등)
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   └── test_services.py
├── pyproject.toml
├── README.md
└── .gitignore
```