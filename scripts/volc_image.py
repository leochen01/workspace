#!/usr/bin/env python3
"""
火山引擎图像生成工具
输入: prompt文本文件 + 命令行参数
输出: 生成的图像
python volc_image.py ./prompts/imagegen/rgpc.txt -k 61f454fc-2181-4a38-b24c-df8db3fc12ee -s 2K --model doubao-seedream-4-5-251128          

用法:
    python volc_image.py prompt.txt                    # 使用默认参数
    python volc_image.py prompt.txt -o output.png       # 指定输出文件
    python volc_image.py prompt.txt -n 2               # 生成2张图
    python volc_image.py prompt.txt -s 1024x1024      # 指定尺寸
"""

import argparse
import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional

# 默认配置
DEFAULT_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DEFAULT_MODEL = "doubao-seedream-4-5-251128"  # 根据实际修改
DEFAULT_SIZE = "1024x1024"
DEFAULT_NUM = 1


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


def generate_image(
    prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    api_url: str = DEFAULT_API_URL,
    size: str = DEFAULT_SIZE,
    num: int = DEFAULT_NUM,
    output_dir: str = ".",
    output_prefix: str = "output",
    **extra_params
) -> list[str]:
    """
    调用火山引擎API生成图像
    
    Args:
        prompt: 图像描述提示词
        api_key: 火山引擎API Key
        model: 模型名称
        api_url: API端点URL
        size: 图像尺寸，如 "1024x1024"
        num: 生成数量
        output_dir: 输出目录
        output_prefix: 输出文件前缀
    
    Returns:
        生成图像的保存路径列表
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "n": num,
        "size": size,
        **extra_params
    }
    
    print(f"[INFO] 正在调用 {model} 生成图像...")
    print(f"[INFO] Prompt: {prompt[:100]}...")
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=120)
    
    if response.status_code != 200:
        print(f"[ERROR] API返回错误: {response.status_code}")
        print(f"[ERROR] 响应内容: {response.text}")
        raise Exception(f"API调用失败: {response.text}")
    
    result = response.json()
    print(f"[INFO] API响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
    
    # 解析返回结果，保存图像
    saved_paths = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 根据实际API响应格式解析
    # 火山引擎不同版本响应格式可能有差异
    images = []
    if "data" in result:
        images = result["data"]
    elif "images" in result:
        images = result["images"]
    elif "output" in result:
        images = result["output"]
    else:
        images = [result]  # 可能是单个对象
    
    for i, img_data in enumerate(images):
        # 处理base64或URL
        if isinstance(img_data, dict):
            if "b64_json" in img_data:
                import base64
                img_bytes = base64.b64decode(img_data["b64_json"])
                ext = "png"
            elif "url" in img_data:
                # 下载URL图片
                img_response = requests.get(img_data["url"], timeout=60)
                img_bytes = img_response.content
                ext = img_data["url"].split('.')[-1][:4] or "png"
            else:
                print(f"[WARN] 未知图像格式: {img_data}")
                continue
        else:
            # 直接是base64字符串
            import base64
            img_bytes = base64.b64decode(img_data)
            ext = "png"
        
        # 保存文件
        filename = f"{output_prefix}_{i+1}.{ext}"
        filepath = output_path / filename
        
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        
        saved_paths.append(str(filepath.absolute()))
        print(f"[OK] 已保存: {filepath}")
    
    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="火山引擎图像生成工具 - 读取prompt文件生成图像",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python volc_image.py prompt.txt
    python volc_image.py prompt.txt -o ./images
    python volc_image.py prompt.txt -n 3 -s 512x512
    python volc_image.py prompt.txt --api-key your_key_here

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
        "-s", "--size",
        default=DEFAULT_SIZE,
        help=f"图像尺寸 (默认: {DEFAULT_SIZE}, 如 1024x1024, 512x512)"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        default=DEFAULT_NUM,
        help=f"生成数量 (默认: {DEFAULT_NUM})"
    )
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="输出目录 (默认: 当前目录)"
    )
    parser.add_argument(
        "-p", "--prefix",
        default="volc_image",
        help="输出文件前缀 (默认: volc_image)"
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
    print("火山引擎图像生成工具")
    print("=" * 50)
    print(f"Prompt文件: {args.prompt_file}")
    print(f"API端点:    {args.api_url}")
    print(f"模型:       {args.model}")
    print(f"尺寸:       {args.size}")
    print(f"数量:       {args.num}")
    print(f"输出目录:   {args.output}")
    print("=" * 50)
    
    if args.dry_run:
        print(f"\n[Dry Run] Prompt内容:\n{prompt}")
        sys.exit(0)
    
    # 生成图像
    try:
        saved = generate_image(
            prompt=prompt,
            api_key=args.api_key,
            model=args.model,
            api_url=args.api_url,
            size=args.size,
            num=args.num,
            output_dir=args.output,
            output_prefix=args.prefix
        )
        print(f"\n[SUCCESS] 共生成 {len(saved)} 张图像")
    except Exception as e:
        print(f"[FAILED] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
