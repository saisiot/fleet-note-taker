#!/usr/bin/env python3
"""
Fleet Note Generator
손글씨 메모 이미지를 Obsidian Fleet Note로 변환하는 프로그램
"""

import sys
import os
from config import Config
from ocr_processor import OCRProcessor
from note_generator import NoteGenerator
from file_manager import FileManager

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("Fleet Note Generator")
    print("=" * 50)
    
    try:
        # 설정 검증 및 디렉토리 생성
        Config.validate_config()
        Config.create_directories()
        
        # 컴포넌트 초기화
        ocr_processor = OCRProcessor()
        note_generator = NoteGenerator()
        file_manager = FileManager()
        
        # 처리 대기 이미지 확인
        pending_images = file_manager.get_pending_images()
        stats = file_manager.get_stats()
        
        print(f"처리 대기 이미지: {stats['pending']}개")
        print(f"처리 완료 이미지: {stats['processed']}개")
        print("-" * 30)
        
        if not pending_images:
            print("처리할 이미지가 없습니다.")
            print(f"'{Config.ORIGINAL_NOTES_DIR}' 폴더에 이미지를 넣어주세요.")
            return
        
        # 각 이미지 처리
        processed_count = 0
        failed_count = 0
        
        for i, image_path in enumerate(pending_images, 1):
            filename = os.path.basename(image_path)
            print(f"\n[{i}/{len(pending_images)}] 처리 중: {filename}")
            
            # OCR 및 LLM 분석
            print("  - 이미지 분석 중...")
            analysis_result = ocr_processor.extract_text_and_analyze(image_path)
            
            if not analysis_result:
                print("  ❌ 분석 실패")
                failed_count += 1
                continue
            
            # 노트 생성
            print("  - 노트 생성 중...")
            note_path = note_generator.generate_note(analysis_result, filename)
            
            if not note_path:
                print("  ❌ 노트 생성 실패")
                failed_count += 1
                continue
            
            # 파일 이동
            print("  - 파일 이동 중...")
            moved_filename = file_manager.move_to_linked(image_path)
            
            if moved_filename:
                print(f"  ✅ 완료: {analysis_result['title']}")
                processed_count += 1
            else:
                print("  ❌ 파일 이동 실패")
                failed_count += 1
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("처리 완료!")
        print(f"성공: {processed_count}개")
        print(f"실패: {failed_count}개")
        print("=" * 50)
        
    except ValueError as e:
        print(f"설정 오류: {e}")
        print("'.env' 파일의 GOOGLE_API_KEY를 확인해주세요.")
        return 1
    except KeyboardInterrupt:
        print("\n\n처리가 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())