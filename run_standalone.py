#!/usr/bin/env python3
"""
단독 실행 스크립트들 - 각 단계를 개별적으로 실행할 수 있습니다.
"""

import sys
import argparse
from network_analyzer import update_notes_network
from note_recommender import add_fleet_note_links

def run_network_analysis():
    """2단계만 실행: 네트워크 분석"""
    print("🔍 네트워크 분석만 실행합니다.")
    return update_notes_network()

def run_link_recommendation(dry_run=False, target_files=None):
    """3단계만 실행: 링크 추천"""
    print("🔗 링크 추천만 실행합니다.")
    return add_fleet_note_links(dry_run=dry_run, target_files=target_files)

def main():
    parser = argparse.ArgumentParser(description='Fleet Note 시스템 - 단독 실행')
    parser.add_argument('command', choices=['network', 'links'],
                       help='실행할 단계: network (네트워크 분석) 또는 links (링크 추천)')
    parser.add_argument('--dry-run', action='store_true',
                       help='링크 추천 시 DRY RUN 모드로 실행')
    parser.add_argument('--files', nargs='*',
                       help='링크 추천할 특정 파일들 (선택사항)')

    args = parser.parse_args()

    if args.command == 'network':
        if run_network_analysis():
            print("✅ 네트워크 분석 완료!")
        else:
            print("❌ 네트워크 분석 실패")
            return 1

    elif args.command == 'links':
        if run_link_recommendation(dry_run=args.dry_run, target_files=args.files):
            print("✅ 링크 추천 완료!")
        else:
            print("❌ 링크 추천 실패")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())