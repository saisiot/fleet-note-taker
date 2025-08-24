# Fleet Note Generator

손글씨 메모 이미지를 Obsidian Fleet Note로 자동 변환하는 Python 프로그램입니다.

## 🚀 주요 기능

- **자동 이미지 감지**: `original_notes/` 폴더의 이미지를 자동으로 감지
- **AI 기반 텍스트 추출**: OpenAI GPT-4o-mini를 사용한 정확한 OCR 처리
- **스마트 분석**: 메모 내용을 바탕으로 제목, 태그, 내용을 자동 생성
- **Obsidian 호환**: Fleet Note 형식의 마크다운 파일 자동 생성
- **파일 관리**: 처리 완료된 이미지를 자동으로 정리

## 📋 요구사항

- Python 3.8 이상
- OpenAI API 키
- 인터넷 연결

## 🛠️ 설치 방법

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd fleet_note_taker_2508
   ```

**💡 빠른 시작 (macOS/Linux)**
```bash
# 가상환경 자동 활성화 및 상태 확인
./activate.sh
```

2. **의존성 설치**
   ```bash
   # 가상환경 생성
   python -m venv venv
   
   # 가상환경 활성화
   source venv/bin/activate  # macOS/Linux
   # 또는
   .\venv\Scripts\activate   # Windows
   
   # 패키지 설치
   pip install -r requirements.txt
   ```

3. **환경변수 설정**
   프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키를 설정하세요:
   ```bash
   # .env 파일 생성
   touch .env
   
   # .env 파일 편집 (텍스트 에디터 사용)
   # 또는 다음 내용을 복사하여 .env 파일에 붙여넣기
   ```
   
   `.env` 파일 내용:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **⚠️ 중요**: `your_openai_api_key_here` 부분을 실제 OpenAI API 키로 교체하세요!

## 📁 폴더 구조

```
fleet_note_taker_2508/
├── original_notes/     # 처리할 이미지 파일들
├── linked_notes/       # 처리 완료된 이미지들
├── venv/               # Python 가상환경
├── main.py             # 메인 실행 파일
├── config.py           # 설정 관리
├── ocr_processor.py    # OCR 및 AI 분석
├── note_generator.py   # 노트 생성
├── file_manager.py     # 파일 관리
├── activate.sh         # 가상환경 활성화 스크립트
├── requirements.txt    # Python 의존성
└── README.md           # 프로젝트 문서
```

## 🎯 사용 방법

1. **이미지 준비**
   - `original_notes/` 폴더에 처리할 이미지 파일을 넣으세요
   - 지원 형식: JPG, JPEG, PNG, BMP, TIFF

2. **프로그램 실행**
   ```bash
   # 가상환경 활성화 (아직 활성화하지 않았다면)
   source venv/bin/activate  # macOS/Linux
   # 또는
   .\venv\Scripts\activate   # Windows
   
   # 프로그램 실행
   python main.py
   ```

3. **결과 확인**
   - 생성된 마크다운 노트는 프로젝트 루트에 저장됩니다
   - 처리 완료된 이미지는 `linked_notes/` 폴더로 이동됩니다

## 📝 생성되는 노트 형식

```markdown
---
title: 메모_제목
created: 2024-01-15
modification date: 2024-01-15
source: 
aliases: 
tags: [태그1, 태그2, 태그3]
type: fleet
---
- [ ] 작업하기

## Notes
메모 내용...

## Quotes

## Source
- 

## Links
- 

---
**원본 이미지**: ![메모원본](linked_notes/이미지파일명)
```

## ⚙️ 설정 옵션

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

```env
OPENAI_API_KEY=your_api_key
MAX_TITLE_LENGTH=40
SUPPORTED_IMAGE_FORMATS=jpg,jpeg,png,bmp,tiff
OCR_LANGUAGE=kor+eng
```

## 🔧 문제 해결

### 일반적인 오류

1. **API 키 오류**
   - `.env` 파일에 올바른 OpenAI API 키가 설정되어 있는지 확인
   - API 키가 유효한지 확인

2. **이미지 처리 실패**
   - 지원되는 이미지 형식인지 확인
   - 이미지 파일이 손상되지 않았는지 확인

3. **권한 오류**
   - 폴더에 쓰기 권한이 있는지 확인

## 📊 처리 통계

프로그램 실행 시 다음 정보를 확인할 수 있습니다:
- 처리 대기 중인 이미지 수
- 처리 완료된 이미지 수
- 각 이미지별 처리 진행 상황
- 최종 성공/실패 통계

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**참고**: 이 프로그램은 OpenAI API를 사용하므로 사용량에 따른 비용이 발생할 수 있습니다.

## 🚀 **첫 실행 가이드**

1. **OpenAI API 키 준비**
   - [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키 발급
   - API 키는 `sk-...`로 시작하는 문자열입니다

2. **환경 설정**
   ```bash
   # .env 파일 생성 및 편집
   echo "OPENAI_API_KEY=your_actual_api_key" > .env
   ```

3. **프로그램 실행**
   ```bash
   python main.py
   ```

4. **이미지 준비**
   - `original_notes/` 폴더에 처리할 이미지 파일을 넣으세요
   - 지원 형식: JPG, JPEG, PNG, BMP, TIFF
