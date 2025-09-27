#!/usr/bin/env python3
"""
Obsidian 노트 네트워크 분석기
00 Notes 폴더의 노트들을 분석하여 DB에 저장하고 네트워크 통계를 생성합니다.
"""

import os
import re
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
import yaml
from config import Config

class ObsidianNoteParser:
    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            # Config에서 생성된 노트 폴더의 상위 디렉토리를 vault_path로 사용
            self.vault_path = Path(Config.GENERATED_NOTES_DIR).parent

        self.notes_path = self.vault_path / "00 Notes"
        self.notes = {}
        self.links_graph = {}

    def parse_frontmatter(self, content: str) -> Dict:
        """YAML frontmatter 파싱"""
        frontmatter = {}
        if content.startswith('---'):
            try:
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    yaml_content = content[3:end_idx].strip()
                    frontmatter = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError:
                pass
        return frontmatter

    def extract_links(self, content: str) -> Set[str]:
        """[[링크]] 형식의 내부 링크 추출"""
        pattern = r'\[\[(.*?)\]\]'
        links = re.findall(pattern, content)

        clean_links = set()
        for link in links:
            # 앵커나 별칭 처리 (예: [[노트#섹션]] 또는 [[노트|별칭]])
            if '#' in link:
                link = link.split('#')[0]
            if '|' in link:
                link = link.split('|')[0]

            link = link.strip()
            if link and not link.startswith('!'):  # 임베드 제외
                clean_links.add(link)

        return clean_links

    def extract_tags(self, content: str, frontmatter: Dict) -> Set[str]:
        """태그 추출 (frontmatter + 본문)"""
        tags = set()

        # Frontmatter의 태그
        if 'tags' in frontmatter:
            fm_tags = frontmatter['tags']
            if isinstance(fm_tags, list):
                tags.update(fm_tags)
            elif isinstance(fm_tags, str):
                # 쉼표로 구분된 태그 문자열 처리
                tag_list = [tag.strip() for tag in fm_tags.split(',')]
                tags.update(tag_list)

        # 본문의 해시태그
        hashtag_pattern = r'#([a-zA-Z0-9가-힣_/-]+)'
        hashtags = re.findall(hashtag_pattern, content)
        tags.update(hashtags)

        return tags

    def parse_note(self, file_path: Path) -> Dict:
        """개별 노트 파싱"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter = self.parse_frontmatter(content)
        links = self.extract_links(content)
        tags = self.extract_tags(content, frontmatter)

        # 파일명에서 확장자 제거
        note_name = file_path.stem

        # 파일 수정 시간 가져오기
        file_mtime = file_path.stat().st_mtime

        return {
            'name': note_name,
            'path': str(file_path.relative_to(self.vault_path)),
            'title': frontmatter.get('title', note_name),
            'created': frontmatter.get('created', ''),
            'modified': str(file_mtime),  # 실제 파일 수정 시간 사용
            'type': frontmatter.get('type', ''),
            'aliases': frontmatter.get('aliases', []),
            'tags': list(tags),
            'links': list(links),
            'content_preview': content[:500] if len(content) > 500 else content
        }

    def parse_all_notes(self, db_path: str = None):
        """모든 노트 파싱 (증분 업데이트 지원)"""
        if not self.notes_path.exists():
            print(f"경로가 존재하지 않습니다: {self.notes_path}")
            return

        md_files = list(self.notes_path.glob("*.md"))
        print(f"{len(md_files)}개의 노트를 발견했습니다.")

        # DB에서 기존 파일들의 수정 시간 조회
        existing_files = {}
        if db_path and Path(db_path).exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT name, path, modified FROM notes')
                for name, path, modified in cursor.fetchall():
                    existing_files[path] = modified
                conn.close()
            except sqlite3.Error:
                print("기존 DB 조회 실패 - 전체 재파싱 진행")

        new_files = 0
        updated_files = 0
        skipped_files = 0

        for file_path in md_files:
            try:
                file_mtime = file_path.stat().st_mtime
                relative_path = str(file_path.relative_to(self.vault_path))

                # 파일이 변경되었는지 확인
                if relative_path in existing_files:
                    if abs(float(existing_files[relative_path]) - file_mtime) < 1.0:  # 1초 오차 허용
                        skipped_files += 1
                        continue
                    else:
                        updated_files += 1
                else:
                    new_files += 1

                note_data = self.parse_note(file_path)
                self.notes[note_data['name']] = note_data

                # 링크 그래프 구축
                self.links_graph[note_data['name']] = note_data['links']

            except Exception as e:
                print(f"파싱 실패: {file_path} - {e}")

        print(f"파싱 완료: 새 파일 {new_files}개, 업데이트 {updated_files}개, 건너뜀 {skipped_files}개")

    def find_backlinks(self) -> Dict[str, List[str]]:
        """백링크 계산"""
        backlinks = {}

        for note_name, links in self.links_graph.items():
            for link in links:
                if link not in backlinks:
                    backlinks[link] = []
                backlinks[link].append(note_name)

        return backlinks

    def calculate_link_stats(self) -> Dict:
        """링크 통계 계산"""
        backlinks = self.find_backlinks()

        stats = {}
        for note_name in self.notes:
            outgoing = len(self.links_graph.get(note_name, []))
            incoming = len(backlinks.get(note_name, []))

            stats[note_name] = {
                'outgoing_links': outgoing,
                'incoming_links': incoming,
                'total_connections': outgoing + incoming
            }

        return stats

class ObsidianNetworkDB:
    def __init__(self, db_path: str = "obsidian_network.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """데이터베이스 테이블 생성"""
        cursor = self.conn.cursor()

        # 노트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                title TEXT,
                created TEXT,
                modified TEXT,
                type TEXT,
                aliases TEXT,
                content_preview TEXT,
                outgoing_links INTEGER DEFAULT 0,
                incoming_links INTEGER DEFAULT 0,
                total_connections INTEGER DEFAULT 0
            )
        ''')

        # 태그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # 노트-태그 관계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY(note_id) REFERENCES notes(id),
                FOREIGN KEY(tag_id) REFERENCES tags(id),
                PRIMARY KEY(note_id, tag_id)
            )
        ''')

        # 링크 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_note_id INTEGER,
                target_note_name TEXT,
                FOREIGN KEY(source_note_id) REFERENCES notes(id)
            )
        ''')

        # 백링크 뷰
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS backlinks AS
            SELECT
                n2.name as source_note,
                n1.name as target_note
            FROM links l
            JOIN notes n1 ON l.source_note_id = n1.id
            LEFT JOIN notes n2 ON l.target_note_name = n2.name
            WHERE n2.name IS NOT NULL
        ''')

        self.conn.commit()

    def save_notes(self, notes: Dict, link_stats: Dict):
        """노트 데이터 저장"""
        cursor = self.conn.cursor()

        for note_name, note_data in notes.items():
            stats = link_stats.get(note_name, {})

            cursor.execute('''
                INSERT OR REPLACE INTO notes
                (name, path, title, created, modified, type, aliases, content_preview,
                 outgoing_links, incoming_links, total_connections)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_name,
                note_data['path'],
                note_data['title'],
                note_data['created'],
                note_data['modified'],
                note_data['type'],
                json.dumps(note_data['aliases']),
                note_data['content_preview'],
                stats.get('outgoing_links', 0),
                stats.get('incoming_links', 0),
                stats.get('total_connections', 0)
            ))

            note_id = cursor.lastrowid

            # 태그 저장
            for tag in note_data['tags']:
                cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
                tag_id = cursor.fetchone()[0]

                cursor.execute('''
                    INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                    VALUES (?, ?)
                ''', (note_id, tag_id))

            # 링크 저장
            for link in note_data['links']:
                cursor.execute('''
                    INSERT INTO links (source_note_id, target_note_name)
                    VALUES (?, ?)
                ''', (note_id, link))

        self.conn.commit()

    def get_network_stats(self) -> Dict:
        """네트워크 통계 조회"""
        cursor = self.conn.cursor()

        stats = {}

        # 전체 노트 수
        cursor.execute('SELECT COUNT(*) FROM notes')
        stats['total_notes'] = cursor.fetchone()[0]

        # 전체 링크 수
        cursor.execute('SELECT COUNT(*) FROM links')
        stats['total_links'] = cursor.fetchone()[0]

        # 전체 태그 수
        cursor.execute('SELECT COUNT(*) FROM tags')
        stats['total_tags'] = cursor.fetchone()[0]

        # 가장 많이 링크된 노트 (상위 10개)
        cursor.execute('''
            SELECT name, incoming_links
            FROM notes
            ORDER BY incoming_links DESC
            LIMIT 10
        ''')
        stats['most_linked'] = cursor.fetchall()

        # 가장 많이 링크하는 노트 (상위 10개)
        cursor.execute('''
            SELECT name, outgoing_links
            FROM notes
            ORDER BY outgoing_links DESC
            LIMIT 10
        ''')
        stats['most_linking'] = cursor.fetchall()

        # 고립된 노트 (링크가 없는 노트)
        cursor.execute('''
            SELECT COUNT(*)
            FROM notes
            WHERE total_connections = 0
        ''')
        stats['orphan_notes'] = cursor.fetchone()[0]

        return stats

    def close(self):
        """데이터베이스 연결 종료"""
        self.conn.close()

def update_notes_network():
    """00 Notes 폴더를 스캔하여 네트워크 DB 업데이트"""
    print("=" * 50)
    print("Obsidian 노트 네트워크 분석 시작")
    print("=" * 50)

    # 파서 초기화 및 노트 파싱 (증분 업데이트 지원)
    parser = ObsidianNoteParser()
    db_path = "obsidian_network.db"
    parser.parse_all_notes(db_path)

    # 링크 통계 계산
    link_stats = parser.calculate_link_stats()
    backlinks = parser.find_backlinks()

    # 데이터베이스 저장
    print("\n데이터베이스에 저장 중...")
    db = ObsidianNetworkDB()
    db.save_notes(parser.notes, link_stats)

    # 통계 출력
    print("\n" + "=" * 50)
    print("네트워크 통계")
    print("=" * 50)

    stats = db.get_network_stats()
    print(f"총 노트 수: {stats['total_notes']}")
    print(f"총 링크 수: {stats['total_links']}")
    print(f"총 태그 수: {stats['total_tags']}")
    print(f"고립된 노트: {stats['orphan_notes']}")

    print("\n가장 많이 참조된 노트 (상위 5개):")
    for name, count in stats['most_linked'][:5]:
        print(f"  - {name}: {count}개 백링크")

    print("\n가장 많이 링크하는 노트 (상위 5개):")
    for name, count in stats['most_linking'][:5]:
        print(f"  - {name}: {count}개 링크")

    db.close()
    print("\n분석 완료! 'obsidian_network.db' 파일이 생성되었습니다.")
    return True

if __name__ == "__main__":
    update_notes_network()