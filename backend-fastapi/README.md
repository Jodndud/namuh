# backend-fastapi

## 🚀 주요 기능

### 1. STT & TTS (Speech-to-Text & Text-to-Speech)
- OpenAI API를 활용한 음성-텍스트 변환
- Base64 인코딩 또는 파일 업로드 방식 지원
- 텍스트 기반 처리 기능

### 2. MQTT 메시징
- MQTT 브로커를 통한 실시간 메시지 발행/구독
- 비동기 메시지 처리
- Topic 기반 메시지 라우팅

### 3. S3 파일 관리
- AWS S3 파일 업로드/삭제
- 썸네일 자동 생성
- 디렉토리 기반 파일 관리

### 4. 인증 & 보안
- JWT 기반 인증 시스템
- Bearer Token 인증
- 경로별 인증 제외 설정 지원

### 5. 헬스 체크
- 애플리케이션 상태 모니터링
- 데이터베이스 연결 상태 확인

## 🛠 기술 스택

### Core Framework
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Python 3.12**: 최신 Python 버전

### 주요 라이브러리
- **dependency-injector**: 의존성 주입 컨테이너
- **Pydantic**: 데이터 검증 및 설정 관리
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **PyJWT**: JWT 토큰 처리
- **OpenAI**: STT/TTS 기능
- **aiomqtt**: 비동기 MQTT 클라이언트
- **boto3**: AWS S3 클라이언트

### 데이터베이스 & 캐시
- **MySQL**: 관계형 데이터베이스
- **Redis**: 캐싱 및 세션 관리

### 서버
- **Uvicorn**: ASGI 서버

## 📁 프로젝트 구조

```
backend-fastapi/
├── app/
│   ├── controllers/          # API 엔드포인트 정의
│   │   ├── health_controller.py
│   │   ├── mqtt_controller.py
│   │   ├── s3_controller.py
│   │   └── stt_tts_controller.py
│   ├── core/                 # 핵심 설정 및 인프라
│   │   ├── base_response.py  # 표준 응답 포맷
│   │   ├── containers.py     # DI 컨테이너
│   │   ├── load_settings.py  # 환경 설정
│   │   ├── mqtt.py           # MQTT 클라이언트
│   │   ├── mysql.py          # MySQL 연결
│   │   ├── redis.py          # Redis 연결
│   │   ├── s3.py             # S3 클라이언트
│   │   └── exceptions/       # 예외 처리
│   ├── middlewares/          # 미들웨어
│   │   ├── cors_config_middleware.py
│   │   ├── jwt_middleware.py
│   │   └── logging_middleware.py
│   ├── models/               # 데이터베이스 모델
│   ├── repositories/         # 데이터 액세스 계층
│   ├── schemas/              # DTO 및 스키마
│   │   ├── mqtt_dto.py
│   │   ├── s3_dto.py
│   │   ├── stt_dto.py
│   │   └── tts_enum.py
│   ├── security/             # 보안 관련
│   │   ├── jwt_provider.py
│   │   └── security_config.py
│   ├── services/             # 비즈니스 로직
│   │   ├── implementation/   # 서비스 구현체
│   │   ├── auth_service.py
│   │   ├── health_service.py
│   │   ├── mqtt_service.py
│   │   ├── s3_service.py
│   │   └── stt_tts_service.py
│   └── utils/                # 유틸리티
│       ├── openai_util.py
│       └── rsp_util.py
├── requirements/             # 의존성 관리
│   ├── base.txt             # 기본 의존성
│   ├── local.txt            # 로컬 개발용
│   └── production.txt       # 프로덕션용
├── Dockerfile.local         # 로컬 개발용 Dockerfile
├── Dockerfile.production    # 프로덕션용 Dockerfile
└── main.py                  # 애플리케이션 진입점
```

## 🚀 실행
#### 로컬 Docker 실행 방법

```bash
docker build -f Dockerfile.local -t backend-fastapi:local .

docker run --env-file ./.env --env-file ./.env.local -p 8081:8081 backend-fastapi:local
```
#### 로컬 FastAPI 실행 방법

```bash
# 가상환경 설정
python -m venv .venv

# Linux / MacOS
source .venv/bin/activate

# Windows
source .venv/Scripts/activate

# 의존성 패키지 설치
pip install --upgrade pip
pip install -r requirements/base.txt -r requirements/local.txt

# 실행
python main.py
```
