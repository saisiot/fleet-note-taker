# Fleet Note Generator v1.0

손글씨 메모 이미지를 Obsidian Fleet Note로 자동 변환하는 Python 프로그램입니다.

**🚀 최신 업데이트: Gemini 2.5 Flash-Lite 모델 적용으로 성능 및 비용 효율성 대폭 향상!**

## ✨ 주요 기능

- **AI 기반 이미지 분석**: Gemini 2.5 Flash-Lite를 사용한 정확한 손글씨 인식
- **자동 노트 생성**: Fleet Note 형식의 마크다운 파일 자동 생성
- **스마트 태그 생성**: 메모 내용 기반 자동 태그 생성
- **파일 관리**: 처리 완료된 이미지 자동 정리
- **macOS/Obsidian 호환**: 모든 특수문자 자동 정제

## 🎯 사용 사례

- 📝 **손글씨 메모 디지털화**: 물리적 메모를 Obsidian 노트로 변환
- 🏥 **의료 기록**: 병원 입원 중 메모 정리
- 💼 **업무 노트**: 회의 메모 및 아이디어 정리
- 📚 **학습 노트**: 공부 메모 및 요약 정리

## 🏗️ 아키텍처

```
fleet_note_taker_2508/
├── original_notes/     # 처리할 이미지 파일들
├── linked_notes/       # 처리 완료된 이미지들
├── main.py             # 메인 실행 파일
├── config.py           # 설정 관리
├── ocr_processor.py    # AI 이미지 분석
├── note_generator.py   # 노트 생성
├── file_manager.py     # 파일 관리
└── requirements.txt    # Python 의존성
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd fleet_note_taker_2508
```

### 2. 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
.\venv\Scripts\activate   # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
`.env` 파일을 생성하고 Google AI API 키를 설정하세요:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 5. 프로그램 실행
```bash
python main.py
```

## 📊 모델 성능 비교

| 모델 | 비용 (1M 토큰) | 성능 | 특징 |
|------|----------------|------|------|
| **Gemini 2.5 Flash-Lite** | $0.10 / $0.40 | ⭐⭐⭐⭐⭐ | **현재 사용 중** - 최고의 비용 효율성 |
| GPT-4o-mini | $0.15 / $0.60 | ⭐⭐⭐⭐ | 이전 모델 - 33% 더 비쌈 |
| GPT-4o | $0.25 / $1.00 | ⭐⭐⭐⭐⭐ | 고성능이지만 비쌈 |

## 💰 비용 계산

### **이미지당 예상 비용 (Gemini 2.5 Flash-Lite)**
- **입력 토큰**: ~3,000 토큰
- **출력 토큰**: ~225 토큰
- **1개 이미지**: 약 **$0.0009** (약 1.2원)
- **100개 이미지**: 약 **$0.09** (약 120원)
- **1000개 이미지**: 약 **$0.90** (약 1,200원)

## 📝 생성되는 노트 형식

```markdown
---
title: 메모_제목
created: 2025-08-15
modification date: 2025-08-15
type: fleet
---
- [ ] 작업하기

## Notes
메모 내용...

## Quotes

## Source

## Links

---
**원본 이미지**: ![메모원본](linked_notes/이미지파일명)

#태그1 #태그2 #태그3
```

## 🔧 설정 옵션

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

```env
GOOGLE_API_KEY=your_api_key
MAX_TITLE_LENGTH=40
SUPPORTED_IMAGE_FORMATS=jpg,jpeg,png,bmp,tiff
```

## 🛠️ 기술 스택

- **Python 3.8+**: 메인 프로그래밍 언어
- **Google Generative AI**: Gemini 2.5 Flash-Lite 모델
- **Pillow**: 이미지 처리
- **python-dotenv**: 환경변수 관리

## 📈 버전 히스토리

### v1.0 (2025-08-24)
- 🎉 **Gemini 2.5 Flash-Lite 모델 적용**
- 🚀 **비용 33% 절약** (GPT-4o-mini 대비)
- ✨ **성능 대폭 향상** - 더 정확한 손글씨 인식
- 🧹 **코드 최적화** - 불필요한 부분 제거
- 🏷️ **태그 시스템 개선** - 해시태그 형태로 변경
- 📅 **날짜 파싱 정확도 향상**
- 🖥️ **macOS/Obsidian 호환성** - 모든 특수문자 자동 정제

### v0.9 (이전)
- OpenAI GPT-4o-mini 모델 사용
- 기본 OCR 및 노트 생성 기능

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**참고**: 이 프로그램은 Google AI API를 사용하므로 사용량에 따른 비용이 발생할 수 있습니다.
