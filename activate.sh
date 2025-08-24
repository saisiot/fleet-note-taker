#!/bin/bash

# Fleet Note Generator 가상환경 활성화 스크립트

echo "🚀 Fleet Note Generator 가상환경을 활성화합니다..."

# 가상환경이 존재하는지 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 존재하지 않습니다."
    echo "다음 명령어로 가상환경을 생성하세요:"
    echo "python -m venv venv"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# Python 경로 확인
echo "✅ 가상환경이 활성화되었습니다."
echo "Python 경로: $(which python)"
echo "Python 버전: $(python --version)"

# 필요한 패키지가 설치되어 있는지 확인
if ! python -c "import openai, dotenv, PIL" 2>/dev/null; then
    echo "⚠️  필요한 패키지가 설치되지 않았습니다."
    echo "다음 명령어로 패키지를 설치하세요:"
    echo "pip install -r requirements.txt"
else
    echo "✅ 모든 필요한 패키지가 설치되어 있습니다."
fi

echo ""
echo "🎯 프로그램을 실행하려면: python main.py"
echo "가상환경을 비활성화하려면: deactivate"
