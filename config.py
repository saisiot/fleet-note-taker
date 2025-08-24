import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # LLM 설정
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    LLM_MODEL = 'gemini-2.5-flash-lite'
    LLM_PROVIDER = 'gemini'  # 'openai' 또는 'gemini'
    
    # ========================================
    # 폴더 경로 설정 - 여기서 직접 수정하세요!
    # ========================================
    # 기본값: 현재 작업 디렉토리 하위에 생성
    # 원하는 경로로 변경하려면 아래 값을 수정하세요
    
    # 원본 노트 폴더 (처리할 이미지 파일들)
    ORIGINAL_NOTES_DIR = os.path.join(os.getcwd(), 'original_notes')
    
    # 연결된 노트 폴더 (처리 완료된 이미지들)
    # LINKED_NOTES_DIR = os.path.join(os.getcwd(), 'linked_notes')
    
    # 생성된 노트 폴더 (마크다운 파일들)
    # GENERATED_NOTES_DIR = os.path.join(os.getcwd(), 'generated_notes')
    
    # 예시: 절대 경로로 설정하고 싶다면 아래처럼 주석을 해제하고 수정하세요
    # ORIGINAL_NOTES_DIR = '/Users/username/Documents/my_notes/original'
    LINKED_NOTES_DIR = '/Users/saisiot/Desktop/SecondBrain/99 Fleet/linked_notes'
    GENERATED_NOTES_DIR = '/Users/saisiot/Desktop/SecondBrain/99 Fleet'
    
    # ========================================
    
    # 파일 설정
    MAX_TITLE_LENGTH = int(os.getenv('MAX_TITLE_LENGTH', 40))
    SUPPORTED_IMAGE_FORMATS = os.getenv('SUPPORTED_IMAGE_FORMATS', 'jpg,jpeg,png,bmp,tiff').split(',')
    
    # 노트 템플릿
    FLEET_TEMPLATE = """---
title: {title}
created: {created_date}
modification date: {created_date}
source: 
aliases: 
type: fleet
---
- [ ] 작업하기

## Notes
{notes}

## Quotes



## Source
- 


## Links
- 

---
**원본 이미지**: ![[{image_link}]]

{tags}
"""
    
    @classmethod
    def create_directories(cls):
        """필요한 디렉토리 생성"""
        for directory in [cls.ORIGINAL_NOTES_DIR, cls.LINKED_NOTES_DIR, cls.GENERATED_NOTES_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """설정 검증"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
        return True
    
    @classmethod
    def print_directory_info(cls):
        """디렉토리 정보 출력"""
        print("=== 폴더 설정 정보 ===")
        print(f"원본 노트 폴더: {cls.ORIGINAL_NOTES_DIR}")
        print(f"연결된 노트 폴더: {cls.LINKED_NOTES_DIR}")
        print(f"생성된 노트 폴더: {cls.GENERATED_NOTES_DIR}")
        print("=====================")