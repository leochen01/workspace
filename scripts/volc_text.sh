#!/bin/bash
#=============================================================================
# 火山引擎文生文工具 (curl版)
# 输入: prompt文本文件
# 输出: 生成的文本到txt文件
#
# 用法:
#   ./volc_text.sh prompt.txt                        # 输出到 output.txt
#   ./volc_text.sh prompt.txt -o result.txt          # 指定输出文件
#   ./volc_text.sh prompt.txt -m doubao-pro-32k      # 指定模型
#   ./volc_text.sh prompt.txt -t 0.8                 # 设置temperature
#=============================================================================

# 默认配置
DEFAULT_MODEL="doubao-pro-32k"           # 默认模型
DEFAULT_API_URL="https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DEFAULT_TEMPERATURE="0.7"
DEFAULT_MAX_TOKENS="4096"
OUTPUT_FILE="output.txt"

# 解析参数
MODEL="$DEFAULT_MODEL"
API_URL="$DEFAULT_API_URL"
TEMPERATURE="$DEFAULT_TEMPERATURE"
MAX_TOKENS="$DEFAULT_MAX_TOKENS"
OUTPUT="$OUTPUT_FILE"
SYSTEM_PROMPT=""

# 显示帮助
show_help() {
    echo "火山引擎文生文工具"
    echo ""
    echo "用法: $0 <prompt文件> [选项]"
    echo ""
    echo "选项:"
    echo "  -k, --api-key <key>      API Key (也可设置环境变量 VOLC_API_KEY)"
    echo "  -m, --model <model>       模型名称 (默认: $DEFAULT_MODEL)"
    echo "  -u, --api-url <url>      API端点 (默认: $DEFAULT_API_URL)"
    echo "  -o, --output <file>      输出文件 (默认: $OUTPUT_FILE)"
    echo "  -t, --temperature <n>    温度参数 0-2 (默认: $DEFAULT_TEMPERATURE)"
    echo "  -M, --max-tokens <n>     最大token数 (默认: $DEFAULT_MAX_TOKENS)"
    echo "  -s, --system <text>      system prompt"
    echo "  -h, --help               显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 prompt.txt"
    echo "  $0 prompt.txt -o result.txt -t 0.5"
    echo "  VOLC_API_KEY=xxx $0 prompt.txt -m doubao-pro-32k"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--api-key)
            API_KEY="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -u|--api-url)
            API_URL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -t|--temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        -M|--max-tokens)
            MAX_TOKENS="$2"
            shift 2
            ;;
        -s|--system)
            SYSTEM_PROMPT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
        *)
            PROMPT_FILE="$1"
            shift
            ;;
    esac
done

# 检查API Key
if [ -z "$API_KEY" ]; then
    API_KEY="${VOLC_API_KEY:-}"
fi

if [ -z "$API_KEY" ]; then
    echo "错误: 请提供API Key (-k 参数或设置 VOLC_API_KEY 环境变量)"
    exit 1
fi

# 检查prompt文件
if [ -z "$PROMPT_FILE" ]; then
    echo "错误: 请指定prompt文件"
    show_help
    exit 1
fi

if [ ! -f "$PROMPT_FILE" ]; then
    echo "错误: prompt文件不存在: $PROMPT_FILE"
    exit 1
fi

# 读取prompt内容
PROMPT_CONTENT=$(cat "$PROMPT_FILE")

if [ -z "$PROMPT_CONTENT" ]; then
    echo "错误: prompt文件为空: $PROMPT_FILE"
    exit 1
fi

# 构建messages数组
if [ -n "$SYSTEM_PROMPT" ]; then
    MESSAGES="[
        {\"role\": \"system\", \"content\": \"$SYSTEM_PROMPT\"},
        {\"role\": \"user\", \"content\": \"$PROMPT_CONTENT\"}
    ]"
else
    MESSAGES="[
        {\"role\": \"user\", \"content\": \"$PROMPT_CONTENT\"}
    ]"
fi

# 构建JSON请求体
# 对content进行JSON转义
PROMPT_ESCAPED=$(echo "$PROMPT_CONTENT" | jq -Rs .)
SYSTEM_ESCAPED=$(echo "$SYSTEM_PROMPT" | jq -Rs .)

if [ -n "$SYSTEM_PROMPT" ]; then
    JSON_BODY=$(cat <<EOF
{
    "model": "$MODEL",
    "messages": [
        {"role": "system", "content": $SYSTEM_ESCAPED},
        {"role": "user", "content": $PROMPT_ESCAPED}
    ],
    "temperature": $TEMPERATURE,
    "max_tokens": $MAX_TOKENS
}
EOF
)
else
    JSON_BODY=$(cat <<EOF
{
    "model": "$MODEL",
    "messages": [
        {"role": "user", "content": $PROMPT_ESCAPED}
    ],
    "temperature": $TEMPERATURE,
    "max_tokens": $MAX_TOKENS
}
EOF
)
fi

# 显示配置
echo "========================================"
echo "火山引擎文生文工具"
echo "========================================"
echo "Prompt文件:  $PROMPT_FILE"
echo "API端点:     $API_URL"
echo "模型:        $MODEL"
echo "Temperature: $TEMPERATURE"
echo "Max Tokens:  $MAX_TOKENS"
echo "输出文件:    $OUTPUT"
echo "========================================"
echo ""

# 调用API
echo "[INFO] 正在调用API..."

RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$JSON_BODY")

# 检查响应
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "[ERROR] API返回错误:"
    echo "$RESPONSE" | jq '.error'
    exit 1
fi

# 提取生成的文本
# 兼容不同响应格式
GENERATED_TEXT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // .output // .text // empty')

if [ -z "$GENERATED_TEXT" ] || [ "$GENERATED_TEXT" = "null" ]; then
    echo "[ERROR] 无法解析API响应:"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

# 保存到输出文件
echo "$GENERATED_TEXT" > "$OUTPUT"

echo "[OK] 已保存到: $OUTPUT"
echo ""
echo "========== 生成结果 =========="
echo "$GENERATED_TEXT"
echo "=============================="
