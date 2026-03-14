#!/bin/bash

# Multi-Agent Debate for Translation
# Usage: ./debate4tran.sh [input_file] [output_dir] [lang_pair] [api_key]

INPUT_FILE=$1
OUTPUT_DIR=$2
LANG_PAIR=$3
API_KEY=$4

python3 code/debate4tran.py \
    --input-file $INPUT_FILE \
    --output-dir $OUTPUT_DIR \
    --lang-pair $LANG_PAIR \
    --api-key $API_KEY \
    --model-name gpt-3.5-turbo \
    --temperature 0
