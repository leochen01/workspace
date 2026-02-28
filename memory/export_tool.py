#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ说说导出工具 v1.0
用于导出QQ说说并转换为回忆馆可用格式
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================
# 在此填写你的QQ号和昵称
CONFIG = {
    "qq": "your_qq_number",
    "nickname": "你的昵称"
}

# 你的说说数据（在此手动添加或从文件导入）
MOMENTS_DATA = []

# ==================== 数据格式说明 ====================
"""
说说数据格式：

{
    "id": "唯一ID",
    "content": "说说内容文字",
    "images": ["image1.jpg", "image2.jpg"],  # 图片文件名，放在 images 文件夹
    "created_at": "2012-03-15 14:30:00",     # 发表时间
    "like_count": 25,                         # 点赞数
    "comment_count": 8,                       # 评论数
    "comments": [
        {"content": "评论内容", "author": "评论者"}
    ],
    "location": "地点"                        # 可选
}
"""

# ==================== 示例数据 ====================
# 你可以手动在这里添加说说，或使用其他方式导入
SAMPLE_MOMENTS = [
    {
        "id": "1",
        "content": "今天天气真好，和朋友们一起去爬山，站在山顶俯瞰城市的景色，感觉整个人都轻松了！",
        "images": [],
        "created_at": "2012-03-15 14:30:00",
        "like_count": 25,
        "comment_count": 8,
        "comments": [{"content": "真羡慕，我也想去", "author": "小华"}],
        "location": "山顶公园"
    },
    {
        "id": "2",
        "content": "人生第一份工作正式入职！加油！新的开始，新的挑战！",
        "images": [],
        "created_at": "2013-07-01 09:00:00",
        "like_count": 56,
        "comment_count": 15,
        "comments": [{"content": "恭喜恭喜！", "author": "老王"}],
        "location": ""
    },
    {
        "id": "3",
        "content": "和女朋友在一起三周年纪念日！感谢一路有你，未来我们也要一起走！",
        "images": [],
        "created_at": "2015-05-20 20:00:00",
        "like_count": 188,
        "comment_count": 42,
        "comments": [{"content": "百年好合！", "author": "小红"}],
        "location": "浪漫餐厅"
    },
    {
        "id": "4",
        "content": "今天拿到了驾照！历时三个月终于通过了所有考试，太开心了！",
        "images": [],
        "created_at": "2016-11-10 16:00:00",
        "like_count": 78,
        "comment_count": 20,
        "comments": [{"content": "恭喜恭喜！", "author": "教练"}],
        "location": "考场"
    },
    {
        "id": "5",
        "content": "第一次独自旅行，去了大理。苍山洱海，风花雪月，真的太美了！",
        "images": [],
        "created_at": "2018-08-05 12:00:00",
        "like_count": 156,
        "comment_count": 35,
        "comments": [{"content": "求攻略！", "author": "小明"}],
        "location": "大理"
    },
    {
        "id": "6",
        "content": "今天宝宝出生了！当听到第一声啼哭的时候，我的眼泪再也忍不住了...",
        "images": [],
        "created_at": "2020-02-14 08:30:00",
        "like_count": 520,
        "comment_count": 88,
        "comments": [{"content": "恭喜恭喜！", "author": "全家"}],
        "location": "医院"
    },
    {
        "id": "7",
        "content": "买房了！终于在这个城市有了自己的家，虽然很小但很温馨。",
        "images": [],
        "created_at": "2021-06-18 15:00:00",
        "like_count": 298,
        "comment_count": 56,
        "comments": [{"content": "恭喜恭喜！", "author": "朋友们"}],
        "location": "新家"
    },
    {
        "id": "8",
        "content": "疫情三年，感谢每一个为抗疫付出的人。愿山河无恙，人间皆安。",
        "images": [],
        "created_at": "2022-12-07 20:00:00",
        "like_count": 456,
        "comment_count": 102,
        "comments": [],
        "location": ""
    },
    {
        "id": "9",
        "content": "今天带孩子去看了升国旗仪式，看着五星红旗冉冉升起，心中满是自豪！",
        "images": [],
        "created_at": "2023-10-01 06:00:00",
        "like_count": 234,
        "comment_count": 45,
        "comments": [{"content": "爱国教育从小做起", "author": "老婆"}],
        "location": "天安门广场"
    },
    {
        "id": "10",
        "content": "十年前的今天，我发表了第一条说说。十年间，有欢笑，有泪水，有成长。感谢每一个陪伴我的人！",
        "images": [],
        "created_at": "2024-03-15 00:00:00",
        "like_count": 888,
        "comment_count": 166,
        "comments": [{"content": "十年了！", "author": "老友"}],
        "location": ""
    }
]


def load_from_csv(csv_file):
    """从CSV文件导入说说数据"""
    import csv
    
    moments = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            moment = {
                "id": str(i),
                "content": row.get('content', ''),
                "images": row.get('images', '').split(',') if row.get('images') else [],
                "created_at": row.get('created_at', ''),
                "like_count": int(row.get('like_count', 0)),
                "comment_count": int(row.get('comment_count', 0)),
                "comments": [],
                "location": row.get('location', '')
            }
            
            # 解析评论
            comments_str = row.get('comments', '')
            if comments_str:
                for c in comments_str.split(';'):
                    if ':' in c:
                        author, content = c.split(':', 1)
                        moment["comments"].append({
                            "author": author.strip(),
                            "content": content.strip()
                        })
            
            moments.append(moment)
    
    return moments


def load_from_excel(excel_file):
    """从Excel文件导入说说数据"""
    try:
        import pandas as pd
        df = pd.read_excel(excel_file)
        
        moments = []
        for i, row in df.iterrows():
            moment = {
                "id": str(i + 1),
                "content": str(row.get('content', '')),
                "images": [],
                "created_at": str(row.get('created_at', '')),
                "like_count": int(row.get('like_count', 0)),
                "comment_count": int(row.get('comment_count', 0)),
                "comments": [],
                "location": str(row.get('location', ''))
            }
            moments.append(moment)
        
        return moments
    except ImportError:
        print("需要安装 pandas: pip install pandas openpyxl")
        return []


def export_to_json(moments, output_file='moments.json'):
    """导出为JSON文件"""
    data = {
        "user": CONFIG,
        "moments": moments
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✓ 已导出 {len(moments)} 条说说到 {output_file}")
    return data


def validate_data(moments):
    """验证数据格式"""
    required_fields = ['id', 'content', 'created_at']
    errors = []
    
    for i, m in enumerate(moments):
        for field in required_fields:
            if field not in m:
                errors.append(f"第{i+1}条说说缺少字段: {field}")
    
    if errors:
        print("⚠ 数据验证警告:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✓ 数据格式验证通过")
    
    return len(errors) == 0


def sort_by_date(moments):
    """按日期排序"""
    return sorted(moments, key=lambda x: x['created_at'], reverse=True)


def main():
    print("=" * 50)
    print("QQ说说导出工具")
    print("=" * 50)
    
    # 选择数据源
    print("\n请选择数据导入方式:")
    print("1. 使用示例数据")
    print("2. 从CSV文件导入")
    print("3. 从Excel文件导入")
    print("4. 手动输入")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    moments = []
    
    if choice == '1':
        moments = SAMPLE_MOMENTS
        print("✓ 已加载示例数据")
    
    elif choice == '2':
        csv_file = input("请输入CSV文件路径: ").strip()
        if os.path.exists(csv_file):
            moments = load_from_csv(csv_file)
        else:
            print(f"✗ 文件不存在: {csv_file}")
            return
    
    elif choice == '3':
        excel_file = input("请输入Excel文件路径: ").strip()
        if os.path.exists(excel_file):
            moments = load_from_excel(excel_file)
        else:
            print(f"✗ 文件不存在: {excel_file}")
            return
    
    elif choice == '4':
        print("\n请手动编辑脚本中的 MOMENTS_DATA 变量")
        return
    
    else:
        print("无效选项")
        return
    
    # 验证和排序
    if moments:
        validate_data(moments)
        moments = sort_by_date(moments)
        
        # 导出
        output_file = 'moments.json'
        export_to_json(moments, output_file)
        
        print("\n" + "=" * 50)
        print("导出完成！")
        print(f"共 {len(moments)} 条说说")
        print(f"时间范围: {moments[-1]['created_at'][:4]} - {moments[0]['created_at'][:4]}")
        print("=" * 50)


if __name__ == "__main__":
    main()
