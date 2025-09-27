# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

손글씨 메모 이미지를 Obsidian Fleet Note로 자동 변환하는 Python 애플리케이션입니다. Google의 Gemini 2.5 Flash-Lite 모델을 사용하여 이미지에서 텍스트를 추출하고 분석하여 구조화된 마크다운 노트를 생성합니다.

## 주요 명령어

### 환경 설정
```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 실행
```bash
# 메인 프로그램 실행
python main.py
```

## 환경 설정

- `.env` 파일에 `GOOGLE_API_KEY` 설정 필요
- `config.py`에서 폴더 경로 커스터마이징 가능

## 아키텍처

### 핵심 컴포넌트

1. **main.py**: 메인 실행 파일 및 워크플로우 조정
   - 설정 검증 및 디렉토리 생성
   - 각 컴포넌트 초기화 및 처리 순서 관리

2. **config.py**: 설정 관리
   - API 키, 모델 설정
   - 폴더 경로 설정 (커스터마이징 가능)
   - Fleet Note 템플릿 정의

3. **ocr_processor.py**: AI 이미지 분석
   - Gemini 2.5 Flash-Lite 모델 통합
   - 재시도 로직 (최대 3회) 및 응답 품질 검증
   - 제목 정제 (macOS/Obsidian 호환성)

4. **note_generator.py**: 마크다운 노트 생성
   - Fleet Note 형식으로 구조화
   - 날짜 파싱 및 태그 생성
   - Obsidian 내부 링크 형식 적용

5. **file_manager.py**: 파일 관리
   - 이미지 파일 처리 및 이동
   - 중복 파일명 처리
   - 처리 통계 제공

### 처리 워크플로우

1. `original_notes/` 폴더에서 이미지 파일 스캔
2. OCR 및 AI 분석으로 텍스트 추출
3. 처리된 이미지를 `linked_notes/` 폴더로 이동
4. 구조화된 마크다운 노트를 `generated_notes/` 폴더에 생성

### 노트 구조

생성되는 Fleet Note는 다음 구조를 따릅니다:
- YAML 프론트매터 (title, created, type: fleet)
- 체크박스 작업 항목
- Notes 섹션 (메모 내용 + 원본 이미지 링크)
- Quotes, Source, Links 섹션
- 해시태그 형식 태그

### 폴더 구조

- `original_notes/`: 처리할 이미지 파일들
- `linked_notes/`: 처리 완료된 이미지들
- `generated_notes/`: 생성된 마크다운 노트들 (기본값, config.py에서 수정 가능)

### AI 모델 설정

- 기본 모델: Gemini 2.5 Flash-Lite (비용 효율적)
- OpenAI 모델도 지원 (config.py에서 LLM_PROVIDER 변경)
- 응답 품질 자동 검증 및 재시도 메커니즘

### 특별 고려사항

- macOS 및 Obsidian 파일명 호환성을 위한 특수문자 정제
- 중복 파일명 자동 처리 (숫자 접미사 추가)
- 날짜 형식: YYMMDD → YYYY-MM-DD 변환
- 이미지 형식: jpg, jpeg, png, bmp, tiff 지원