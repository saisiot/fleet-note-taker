import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # LLM 설정
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    LLM_MODEL = 'gemini-2.5-flash-lite'
    LLM_PROVIDER = 'gemini'  # 'openai' 또는 'gemini'
    
    # 파일 경로 설정
    CURRENT_DIR = os.getcwd()
    ORIGINAL_NOTES_DIR = os.path.join(CURRENT_DIR, 'original_notes')
    LINKED_NOTES_DIR = os.path.join(CURRENT_DIR, 'linked_notes')
    
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
**원본 이미지**: ![메모원본]({image_link})

{tags}
"""
    
    @classmethod
    def create_directories(cls):
        """필요한 디렉토리 생성"""
        for directory in [cls.ORIGINAL_NOTES_DIR, cls.LINKED_NOTES_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """설정 검증"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
        return True