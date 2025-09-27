#!/usr/bin/env python3
"""
Fleet 노트 추천 및 링크 자동 추가 시스템
Fleet 노트에 유사한 00 Notes 링크를 자동으로 추가합니다.
"""

import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Set, Tuple
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import Config

class FleetNoteRecommender:
    def __init__(self, db_path: str = "obsidian_network.db"):
        self.vault_path = Path(Config.GENERATED_NOTES_DIR).parent
        self.fleet_path = Path(Config.GENERATED_NOTES_DIR)
        self.notes_path = self.vault_path / "00 Notes"
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.notes_data_cache = {}

    def extract_links_from_section(self, content: str) -> List[str]:
        """## Links 섹션에서만 링크 추출"""
        links_section_pattern = r'^## Links?\s*$'
        match = re.search(links_section_pattern, content, re.MULTILINE)

        if not match:
            return []

        # Links 섹션 시작 위치
        start_pos = match.end()

        # 다음 섹션이나 태그 라인 찾기
        remaining_content = content[start_pos:]
        next_section_match = re.search(r'^##\s+|\n#[^#]', remaining_content, re.MULTILINE)

        if next_section_match:
            end_pos = start_pos + next_section_match.start()
        else:
            end_pos = len(content)

        # Links 섹션 내용
        links_content = content[start_pos:end_pos]

        # 링크 추출 (- [[ ]] 형식)
        link_pattern = r'-\s*\[\[(.*?)\]\]'
        links = re.findall(link_pattern, links_content)

        clean_links = []
        for link in links:
            if '#' in link:
                link = link.split('#')[0]
            if '|' in link:
                link = link.split('|')[0]
            link = link.strip()
            if link and not link.startswith('!'):
                clean_links.append(link)

        return clean_links

    def parse_note_content(self, file_path: Path) -> Dict:
        """노트 내용 파싱"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Frontmatter 파싱
        frontmatter = {}
        clean_content = content
        frontmatter_end = 0

        if content.startswith('---'):
            try:
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    yaml_content = content[3:end_idx].strip()
                    frontmatter = yaml.safe_load(yaml_content) or {}
                    clean_content = content[end_idx + 3:].strip()
                    frontmatter_end = end_idx + 3
            except yaml.YAMLError:
                pass

        # 태그 추출 (frontmatter + 본문)
        tags = set()
        if 'tags' in frontmatter:
            fm_tags = frontmatter['tags']
            if isinstance(fm_tags, list):
                tags.update(fm_tags)
            elif isinstance(fm_tags, str):
                # 쉼표로 구분된 태그 또는 대괄호 형식 처리
                if fm_tags.startswith('[') and fm_tags.endswith(']'):
                    # [태그1, 태그2, 태그3] 형식
                    fm_tags = fm_tags[1:-1]
                tag_list = [tag.strip() for tag in fm_tags.split(',')]
                tags.update(tag_list)

        # 본문에서 태그 추출
        hashtag_pattern = r'#([a-zA-Z0-9가-힣_/-]+)'
        body_tags = re.findall(hashtag_pattern, clean_content)
        tags.update(body_tags)

        # ## Links 섹션의 링크만 추출
        clean_links = self.extract_links_from_section(clean_content)

        # 텍스트 정리 (분석용)
        text_content = re.sub(r'\[\[.*?\]\]', '', clean_content)
        text_content = re.sub(r'!\[\[.*?\]\]', '', text_content)
        text_content = re.sub(r'\[.*?\]\(.*?\)', '', text_content)
        text_content = re.sub(r'#\w+', '', text_content)
        text_content = re.sub(r'^#+\s+', '', text_content, flags=re.MULTILINE)
        text_content = re.sub(r'[*_~`]', '', text_content)

        return {
            'frontmatter': frontmatter,
            'content': clean_content,
            'text_content': text_content,
            'tags': list(tags),
            'links': clean_links,
            'full_content': content,
            'frontmatter_end': frontmatter_end
        }

    def get_notes_data(self) -> Dict[str, Dict]:
        """00 Notes 폴더의 노트 데이터 가져오기 (캐시 사용)"""
        if self.notes_data_cache:
            return self.notes_data_cache

        notes_data = {}

        # DB에서 기본 정보 가져오기
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT name, path, title, type
            FROM notes
        ''')

        for name, path, title, note_type in cursor.fetchall():
            full_path = self.vault_path / path
            if full_path.exists():
                try:
                    note_content = self.parse_note_content(full_path)
                    notes_data[name] = {
                        'path': path,
                        'title': title or name,
                        'type': note_type,
                        'content': note_content['text_content'],
                        'tags': note_content['tags']
                    }
                except Exception as e:
                    print(f"노트 파싱 실패: {name} - {e}")

        self.notes_data_cache = notes_data
        return notes_data

    def find_similar_notes(self, fleet_content: str, fleet_tags: List[str], top_n: int = 3) -> List[Tuple[str, float]]:
        """Fleet 노트와 유사한 00 Notes 찾기"""
        notes_data = self.get_notes_data()

        if not notes_data:
            return []

        # TF-IDF 기반 콘텐츠 유사도
        all_texts = [fleet_content]
        note_names = []

        for name, data in notes_data.items():
            if data['content'].strip():
                all_texts.append(data['content'])
                note_names.append(name)

        if len(all_texts) < 2:
            return []

        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(
            max_features=300,
            min_df=1,
            max_df=0.9,
            ngram_range=(1, 2)
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            target_vector = tfidf_matrix[0]
            similarities = cosine_similarity(target_vector, tfidf_matrix[1:]).flatten()

            # 태그 기반 가중치 추가
            fleet_tags_set = set(fleet_tags)
            final_scores = {}

            for i, name in enumerate(note_names):
                content_score = float(similarities[i]) * 0.7  # 콘텐츠 유사도 70%

                # 태그 유사도 30%
                note_tags = set(notes_data[name].get('tags', []))
                if fleet_tags_set and note_tags:
                    tag_overlap = len(fleet_tags_set.intersection(note_tags))
                    tag_score = (tag_overlap / max(len(fleet_tags_set), len(note_tags))) * 0.3
                else:
                    tag_score = 0

                final_scores[name] = content_score + tag_score

            # 상위 N개 선택
            sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_scores[:top_n]

        except Exception as e:
            print(f"유사도 계산 오류: {e}")
            return []

    def update_fleet_note_links(self, file_path: Path, recommended_links: List[str]) -> bool:
        """Fleet 노트에 추천 링크 추가"""
        note_data = self.parse_note_content(file_path)
        content = note_data['full_content']

        if not recommended_links:
            return False

        # Links 섹션 찾기 또는 생성
        links_section_pattern = r'^## Links?\s*$'
        match = re.search(links_section_pattern, content, re.MULTILINE)

        new_links_text = "\n".join([f"- [[{link}]]" for link in recommended_links])

        if match:
            # 기존 Links 섹션에 추가
            insert_pos = match.end()

            # 다음 섹션이나 태그 찾기
            remaining_content = content[insert_pos:]
            next_section_match = re.search(r'^##\s+|\n---', remaining_content, re.MULTILINE)

            if next_section_match:
                # 다음 섹션 전까지
                end_pos = insert_pos + next_section_match.start()
            else:
                end_pos = len(content)

            # 기존 링크 확인
            existing_links_text = content[insert_pos:end_pos].strip()
            if existing_links_text and '- ' in existing_links_text:
                # 기존 링크가 있으면 추가
                updated_section = existing_links_text + "\n" + new_links_text
            else:
                # 비어있으면 새로 작성
                updated_section = new_links_text

            content = content[:insert_pos] + "\n" + updated_section + "\n" + content[end_pos:]
        else:
            # Links 섹션이 없으면 --- 앞에 추가
            if "\n---" in content:
                # --- 앞에 삽입
                insert_pos = content.rfind("\n---")
                new_section = f"\n## Links\n{new_links_text}\n"
                content = content[:insert_pos] + new_section + content[insert_pos:]
            else:
                # 맨 아래에 추가
                content = content.rstrip()
                new_section = f"\n\n## Links\n{new_links_text}\n"
                content = content + new_section

        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    def process_fleet_note(self, file_path: Path, dry_run: bool = False) -> bool:
        """개별 Fleet 노트 처리"""
        try:
            print(f"처리 중: {file_path.name}")

            # 노트 파싱
            note_data = self.parse_note_content(file_path)

            # 이미 링크가 있는지 확인
            existing_links = note_data['links']
            if existing_links:
                print(f"  ⏭️ 건너뜀 - 이미 {len(existing_links)}개의 링크가 존재")
                return False

            # 태그 확인
            tags = note_data['tags']
            if tags:
                print(f"  태그: {', '.join(tags)}")

            # 유사 노트 찾기
            similar_notes = self.find_similar_notes(
                note_data['text_content'],
                tags,
                top_n=3
            )

            if similar_notes:
                print(f"  추천 링크:")
                recommended_links = []
                for name, score in similar_notes:
                    if score > 0.1:  # 최소 임계값
                        print(f"    - [{score:.3f}] {name}")
                        recommended_links.append(name)

                if not dry_run and recommended_links:
                    # 노트 업데이트
                    if self.update_fleet_note_links(file_path, recommended_links):
                        print(f"  ✅ {len(recommended_links)}개 링크 추가 완료")
                        return True
                    else:
                        print(f"  ❌ 링크 추가 실패")
                        return False
                elif dry_run:
                    print(f"  🔍 DRY RUN - 실제 파일은 수정되지 않음")
                    return True
            else:
                print(f"  ℹ️ 유사한 노트를 찾을 수 없음")

            return False

        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
            return False

    def process_all_fleet_notes(self, dry_run: bool = False, target_files: List[str] = None):
        """Fleet 노트 처리 (전체 또는 특정 파일들만)"""
        if target_files:
            # 특정 파일들만 처리
            fleet_files = [Path(f) for f in target_files if Path(f).exists() and Path(f).suffix == '.md']
            print(f"\n새로 생성된 {len(fleet_files)}개의 Fleet 노트에 링크를 추가합니다.")
        else:
            # 전체 폴더 처리
            if not self.fleet_path.exists():
                print(f"Fleet 폴더를 찾을 수 없습니다: {self.fleet_path}")
                return

            fleet_files = list(self.fleet_path.glob("*.md"))
            if not fleet_files:
                print("처리할 Fleet 노트가 없습니다.")
                return

            print(f"\n{len(fleet_files)}개의 Fleet 노트를 처리합니다.")

        print("=" * 60)

        processed = 0
        errors = 0
        skipped = 0

        for i, file_path in enumerate(fleet_files, 1):
            print(f"\n[{i}/{len(fleet_files)}] ", end="")
            result = self.process_fleet_note(file_path, dry_run)

            if result is True:
                processed += 1
            elif result is False:
                skipped += 1
            else:
                errors += 1

        print("\n" + "=" * 60)
        print(f"처리 완료: 성공 {processed}개, 건너뜀 {skipped}개, 실패 {errors}개")

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()

def add_fleet_note_links(dry_run: bool = False, target_files: List[str] = None):
    """Fleet 노트들에 유사한 노트 링크 자동 추가"""
    print("=" * 50)
    print("Fleet 노트 링크 추천 시작")
    print("=" * 50)

    if dry_run:
        print("🔍 DRY RUN 모드 - 실제 파일은 수정되지 않습니다\n")

    recommender = FleetNoteRecommender()

    try:
        recommender.process_all_fleet_notes(dry_run=dry_run, target_files=target_files)
    finally:
        recommender.close()

    print("\n링크 추가 완료!")
    return True

if __name__ == "__main__":
    import sys
    dry_run = '--dry-run' in sys.argv
    add_fleet_note_links(dry_run=dry_run)