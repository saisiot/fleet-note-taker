import base64
from PIL import Image
import io
from config import Config
import google.generativeai as genai

class OCRProcessor:
    def __init__(self):
        if Config.LLM_PROVIDER == 'gemini':
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.LLM_MODEL)
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.GOOGLE_API_KEY)
    
    def encode_image(self, image_path):
        """이미지를 base64로 인코딩"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text_and_analyze(self, image_path):
        """이미지에서 텍스트 추출 및 LLM 분석"""
        try:
            if Config.LLM_PROVIDER == 'gemini':
                # Gemini 모델 사용
                image = Image.open(image_path)
                prompt = self._get_analysis_prompt()
                
                response = self.model.generate_content([prompt, image])
                
                if response.text:
                    return self._parse_llm_response(response.text)
                else:
                    print("Gemini 응답이 비어있습니다.")
                    return None
            else:
                # OpenAI 모델 사용 (기존 코드)
                base64_image = self.encode_image(image_path)
                
                response = self.client.chat.completions.create(
                    model=Config.LLM_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self._get_analysis_prompt()
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_completion_tokens=1000
                )
                
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    return self._parse_llm_response(content)
                else:
                    print("응답에 choices가 없습니다.")
                    return None
            
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            return None
    
    def _get_analysis_prompt(self):
        """LLM에 보낼 프롬프트"""
        return """
이 손글씨 메모 이미지를 분석해주세요. 다음 형식으로 응답해주세요:

제목: [첫 번째 줄 내용을 그대로 사용]

내용: [두 번째 줄부터 모든 내용을 정리 (원본 텍스트 최대한 유지)]

날짜: [메모에서 날짜 정보 추출 (예: 250815, 250818 등). 날짜를 파악할 수 없으면 오늘 날짜(250824)를 사용하세요]

태그: [노트 내용을 바탕으로 한글 태그 5개]

태그 생성 가이드:
- 자기계발 관련: 학습, 성장, 습관, 목표, 동기부여 등
- 방법론 관련: 전략, 기법, 도구, 프로세스, 시스템 등
- 주제별: 업무, 개인, 공부, 회의, 아이디어 등
- 우선순위: 긴급, 중요, 보통 등

한글로 자연스럽게 작성하고, 메모의 핵심 내용을 놓치지 마세요.
"""
    
    def _parse_llm_response(self, response_text):
        """LLM 응답 파싱"""
        try:
            # 빈 응답 체크
            if not response_text.strip():
                return {
                    'title': '메모',
                    'notes': 'GPT 응답 없음',
                    'tags': ['메모']
                }
            
            # 간단한 텍스트 파싱
            lines = response_text.strip().split('\n')
            title = '메모'
            notes = ''
            date = ''
            tags = ['메모']
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith('제목:'):
                    title = line.replace('제목:', '').strip()
                elif line.startswith('내용:'):
                    # 내용은 다음 줄부터 날짜 전까지 모두 포함
                    notes_lines = []
                    i += 1  # 다음 줄부터 시작
                    while i < len(lines) and not lines[i].strip().startswith('날짜:'):
                        if lines[i].strip():  # 빈 줄이 아닌 경우만
                            notes_lines.append(lines[i].strip())
                        i += 1
                    notes = '\n'.join(notes_lines)
                    continue  # 날짜 처리로 넘어감
                elif line.startswith('날짜:'):
                    date = line.replace('날짜:', '').strip()
                elif line.startswith('태그:'):
                    tags_text = line.replace('태그:', '').strip()
                    # 태그에서 대괄호 제거하고 쉼표로 분리
                    tags_text = tags_text.strip('[]')
                    tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                
                i += 1
            
            # 제목이 비어있으면 기본값 설정
            if not title or title == '[첫 번째 줄 내용을 그대로 사용]':
                title = '메모'
            
            # 내용이 비어있으면 기본값 설정
            if not notes or notes == '[두 번째 줄부터 모든 내용을 정리 (원본 텍스트 최대한 유지)]':
                notes = '내용 분석 중...'
            
            # 태그가 비어있거나 기본값이면 기본 태그 설정
            if not tags or tags == ['[노트 내용을 바탕으로 한글 태그 5개]']:
                tags = ['메모', '자기계발', '방법론']
            
            # 제목 정제 (특수문자 제거, 길이 제한)
            title = self._clean_title(title)
            
            return {
                'title': title,
                'notes': notes,
                'date': date,
                'tags': tags
            }
            
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            return {
                'title': '메모',
                'notes': '파싱 오류로 인한 기본 내용',
                'tags': ['메모']
            }
    
    def _clean_title(self, title):
        """제목 정제 (파일명에 사용 불가능한 문자 제거)"""
        import re
        # 연속된 공백을 언더스코어로 변경
        title = re.sub(r'\s+', '_', title)
        # 길이 제한
        if len(title) > Config.MAX_TITLE_LENGTH:
            title = title[:Config.MAX_TITLE_LENGTH]
        
        # macOS/Obsidian 호환성을 위한 문자 정제
        title = self._clean_for_macos_obsidian(title)
        
        return title.strip('_')  # 앞뒤 언더스코어 제거
    
    def _clean_for_macos_obsidian(self, title):
        """macOS와 Obsidian 호환성을 위한 문자 정제"""
        import re
        # macOS에서 문제가 되는 문자들 제거
        # - 쉼표, 세미콜론, 콜론, 느낌표, 물음표
        # - 대괄호, 중괄호, 괄호
        # - 앰퍼샌드, 백슬래시, 슬래시
        # - 따옴표 (작은따옴표, 큰따옴표)
        title = re.sub(r'[,;:!?\[\]{}()&\\/\'"]', '', title)
        
        # 연속된 언더스코어를 하나로 정리
        title = re.sub(r'_+', '_', title)
        
        # 앞뒤 공백 및 특수문자 제거
        title = title.strip(' _-')
        
        return title
    
