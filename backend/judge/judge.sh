#!/bin/bash
set -e

LANGUAGE=$1
CODE_FILE=$2
INPUT_FILE=$3
TIME_LIMIT=$4
MEMORY_LIMIT=$5

# 编译（C++）
if [ "$LANGUAGE" = "cpp" ]; then
    g++ -std=c++17 -O2 -o /app/program "$CODE_FILE" 2>&1
fi

# 运行
if [ "$LANGUAGE" = "cpp" ]; then
    timeout "$((TIME_LIMIT / 1000))s" /app/program < "$INPUT_FILE"
else
    timeout "$((TIME_LIMIT / 1000))s" python3 "$CODE_FILE" < "$INPUT_FILE"
fi
