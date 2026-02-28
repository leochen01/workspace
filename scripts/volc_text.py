#!/usr/bin/env python3
"""
火山引擎文生文工具 (Python版)
输入: prompt文本文件
输出: 生成的文本到txt文件
python volc_text.py prompts/textgen/rgpc.txt -k c2237824-78f5-492d-82d4-a456817a6aa4 -m doubao-seed-1-8-251228 -t 0.5

用法:
    python volc_text.py prompt.txt                    # 输出到 output.txt
    python volc_text.py prompt.txt -o result.txt     # 指定输出文件
    python volc_text.py prompt.txt -m doubao-seed-1-8-251228 # 指定模型
    python volc_text.py prompt.txt -t 0.8            # 设置temperature
"""

import argparse
import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional

# 默认配置
DEFAULT_MODEL = "doubao-seed-1-8-251228"
DEFAULT_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
OUTPUT_FILE = "output.txt"


def load_prompt(prompt_file: str) -> str:
    """从txt文件读取prompt"""
    path = Path(prompt_file)
    if not path.exists():
        raise FileNotFoundError(f"Prompt文件不存在: {prompt_file}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        raise ValueError(f"Prompt文件为空: {prompt_file}")
    
    return content


def generate_text(
    prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    api_url: str = DEFAULT_API_URL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    system_prompt: Optional[str] = None,
    **extra_params
) -> str:
    """
    调用火山引擎API生成文本
    
    Args:
        prompt: 用户prompt
        api_key: 火山引擎API Key
        model: 模型名称
        api_url: API端点URL
        temperature: 温度参数
        max_tokens: 最大token数
        system_prompt: 可选的system prompt
    
    Returns:
        生成的文本内容
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **extra_params
    }
    
    print(f"[INFO] 正在调用 {model} 生成文本...")
    print(f"[INFO] Prompt: {prompt[:100]}...")
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=120)
    
    if response.status_code != 200:
        print(f"[ERROR] API返回错误: {response.status_code}")
        print(f"[ERROR] 响应内容: {response.text}")
        raise Exception(f"API调用失败: {response.text}")
    
    result = response.json()
    
    # 检查错误
    if "error" in result:
        print(f"[ERROR] API返回错误: {result['error']}")
        raise Exception(f"API错误: {result['error']}")
    
    # 提取生成的文本 - 兼容多种响应格式
    generated_text = None
    if "choices" in result and len(result["choices"]) > 0:
        generated_text = result["choices"][0].get("message", {}).get("content")
    elif "output" in result:
        generated_text = result["output"]
    elif "text" in result:
        generated_text = result["text"]
    
    if not generated_text:
        print(f"[ERROR] 无法解析响应: {result}")
        raise Exception("无法从响应中提取生成的文本")
    
    return generated_text


def main():
    parser = argparse.ArgumentParser(
        description="火山引擎文生文工具 - 读取prompt文件生成文本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python volc_text.py prompt.txt
    python volc_text.py prompt.txt -o result.txt
    python volc_text.py prompt.txt -k your_key -t 0.5
    VOLC_API_KEY=xxx python volc_text.py prompt.txt -m doubao-pro-32k

环境变量:
    VOLC_API_KEY    火山引擎API Key
    VOLC_API_URL    API端点URL (可选)
    VOLC_MODEL      模型名称 (可选)
"""
    )
    
    parser.add_argument(
        "prompt_file",
        help="包含prompt的txt文件路径"
    )
    parser.add_argument(
        "-k", "--api-key",
        default=os.environ.get("VOLC_API_KEY", ""),
        help="火山引擎API Key (也可设置环境变量 VOLC_API_KEY)"
    )
    parser.add_argument(
        "-m", "--model",
        default=os.environ.get("VOLC_MODEL", DEFAULT_MODEL),
        help=f"模型名称 (默认: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "-u", "--api-url",
        default=os.environ.get("VOLC_API_URL", DEFAULT_API_URL),
        help=f"API端点URL (默认: {DEFAULT_API_URL})"
    )
    parser.add_argument(
        "-o", "--output",
        default=OUTPUT_FILE,
        help=f"输出文件 (默认: {OUTPUT_FILE})"
    )
    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"温度参数 0-2 (默认: {DEFAULT_TEMPERATURE})"
    )
    parser.add_argument(
        "-M", "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"最大token数 (默认: {DEFAULT_MAX_TOKENS})"
    )
    parser.add_argument(
        "-s", "--system",
        default=None,
        help="system prompt"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示配置，不实际调用API"
    )
    
    args = parser.parse_args()
    
    # 验证API Key
    if not args.api_key:
        print("[ERROR] 请提供API Key: -k 参数或设置 VOLC_API_KEY 环境变量")
        sys.exit(1)
    
    # 读取prompt
    try:
        prompt = load_prompt(args.prompt_file)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    
    # 显示配置
    print("=" * 50)
    print("火山引擎文生文工具")
    print("=" * 50)
    print(f"Prompt文件: {args.prompt_file}")
    print(f"API端点:    {args.api_url}")
    print(f"模型:       {args.model}")
    print(f"Temperature: {args.temperature}")
    print(f"Max Tokens: {args.max_tokens}")
    print(f"输出文件:   {args.output}")
    if args.system:
        print(f"System:     {args.system[:50]}...")
    print("=" * 50)
    
    if args.dry_run:
        print(f"\n[Dry Run] Prompt内容:\n{prompt}")
        sys.exit(0)
    
    # 生成文本
    try:
        result = generate_text(
            prompt=prompt,
            api_key=args.api_key,
            model=args.model,
            api_url=args.api_url,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            system_prompt=args.system
        )
        
        # 保存到输出文件
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"\n[OK] 已保存到: {output_path.absolute()}")
        print("\n========== 生成结果 ==========")
        print(result)
        print("==============================")
        
    except Exception as e:
        print(f"[FAILED] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
