import os
from datetime import datetime
from config import Config

class NoteGenerator:
    def __init__(self):
        pass
    
    def generate_note(self, analysis_result, image_filename, moved_filename=None):
        """분석 결과를 바탕으로 마크다운 노트 생성"""
        try:
            # LLM에서 추출한 날짜 사용
            if analysis_result.get('date'):
                # 메모에서 추출한 날짜를 2025년으로 가정
                extracted_date = analysis_result['date']
                # YYMMDD 형식에서 MM과 DD 추출
                month = extracted_date[2:4]  # 3-4번째 문자 (월)
                day = extracted_date[4:6]    # 5-6번째 문자 (일)
                current_date = f"2025-{month}-{day}"
                current_date_compact = f"2025{extracted_date}"
            else:
                # 날짜 추출 실패 시 현재 날짜 사용
                current_date = datetime.now().strftime('%Y-%m-%d')
                current_date_compact = datetime.now().strftime('%Y%m%d')
            
            # 태그 문자열 생성 (해시태그 형식)
            tags_str = ' '.join([f'#{tag}' for tag in analysis_result['tags']])
            
            # 이미지 링크 경로 - 이동된 파일명 사용
            if moved_filename:
                # Config.LINKED_NOTES_DIR의 상대 경로 계산
                linked_dir_name = os.path.basename(Config.LINKED_NOTES_DIR)
                image_link = f"{linked_dir_name}/{moved_filename}"
            else:
                # fallback: 원본 파일명 사용
                linked_dir_name = os.path.basename(Config.LINKED_NOTES_DIR)
                image_link = f"{linked_dir_name}/{image_filename}"
            
            # 템플릿에 데이터 삽입
            note_content = Config.FLEET_TEMPLATE.format(
                title=analysis_result['title'],
                created_date=current_date,
                tags=tags_str,
                notes=analysis_result['notes'],
                image_link=image_link
            )
            
            # 파일명 생성 (LLM에서 추출한 날짜 사용)
            if analysis_result.get('date'):
                filename = f"{analysis_result['date']}_{analysis_result['title']}.md"
            else:
                filename = f"{current_date_compact}_{analysis_result['title']}.md"
            
            filepath = os.path.join(Config.GENERATED_NOTES_DIR, filename)
            
            # 파일 중복 확인 및 처리
            filepath = self._ensure_unique_filename(filepath)
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            print(f"노트 생성 완료: {os.path.basename(filepath)}")
            return filepath
            
        except Exception as e:
            print(f"노트 생성 중 오류 발생: {e}")
            return None
    
    def _ensure_unique_filename(self, filepath):
        """중복 파일명 처리"""
        if not os.path.exists(filepath):
            return filepath
        
        base_path, extension = os.path.splitext(filepath)
        counter = 1
        
        while os.path.exists(filepath):
            filepath = f"{base_path}_{counter:02d}{extension}"
            counter += 1
        
        return filepath