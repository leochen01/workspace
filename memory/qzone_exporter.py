#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QzoneExporter 对接工具
自动导出QQ说说并转换为回忆馆格式
"""

import json
import os
import subprocess
import shutil
import time
from pathlib import Path

# ==================== 配置 ====================
CONFIG = {
    "qq": "your_qq_number",  # 你的QQ号
    "output_dir": "./exported_moments"  # 导出目录
}

# ==================== 工具类 ====================
class QzoneExporter:
    """QzoneExporter 对接工具"""
    
    def __init__(self, qq_number):
        self.qq = qq_number
        self.tool_dir = Path("./QzoneExporter")
        self.export_dir = Path(CONFIG["output_dir"])
    
    def clone_tool(self):
        """克隆QzoneExporter仓库"""
        print("📦 正在克隆 QzoneExporter...")
        
        # 尝试不同的仓库名
        repos = [
            "OwnGitee/QzoneExporter",
            "qzone-exporter/QzoneExporter", 
            "xiyouMc/QzoneExporter"
        ]
        
        for repo in repos:
            try:
                if self.tool_dir.exists():
                    shutil.rmtree(self.tool_dir)
                
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(self.tool_dir)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"✅ 成功克隆 {repo}")
                    return True
                    
            except Exception as e:
                continue
        
        print("❌ 无法克隆仓库，请手动下载：")
        print("   https://github.com/OwnGitee/QzoneExporter")
        return False
    
    def get_cookie_guide(self):
        """显示获取Cookie的指南"""
        guide = """
📋 获取QQ空间Cookie的步骤：

1. 电脑浏览器登录 QQ空间：https://qzone.qq.com/
2. 按 F12 打开开发者工具
3. 切换到 Application（应用）标签
4. 左侧找到 Cookies → https://qzone.qq.com
5. 复制 p_skey 或 skey 的值
6. 或者复制整个Cookie字符串

⚠️  注意：Cookie有效期较短，需要在运行时获取
"""
        print(guide)
    
    def run_exporter(self, cookie):
        """运行导出器"""
        if not self.tool_dir.exists():
            print("❌ 请先运行 clone_tool() 或手动下载工具")
            return False
        
        # 查找可执行文件
        exe_files = list(self.tool_dir.glob("*.exe")) + list(self.tool_dir.glob("Qzone*"))
        
        if not exe_files:
            # 尝试查找Python版本
            py_files = list(self.tool_dir.glob("*.py"))
            if py_files:
                print(f"🐍 找到Python脚本: {py_files[0].name}")
                print("请手动运行导出")
                return False
        
        print("⏳ 请前往查看导出工具界面进行操作")
        return True
    
    def convert_format(self, source_dir):
        """转换数据格式"""
        print("🔄 正在转换数据格式...")
        
        # 查找导出的说说文件
        possible_files = [
            source_dir / "moments.json",
            source_dir / "shuoshuo.json",
            source_dir / "data" / "moments.json",
            source_dir / "导出结果" / "说说.json"
        ]
        
        source_file = None
        for f in possible_files:
            if f.exists():
                source_file = f
                break
        
        if not source_file:
            print("❌ 未找到说说数据文件")
            print("请手动复制导出文件到: ./data/moments.json")
            return False
        
        # 读取源数据
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        # 转换为目标格式
        moments = self._transform_moments(source_data)
        
        # 保存
        output_data = {
            "user": {
                "qq": self.qq,
                "nickname": "用户"
            },
            "moments": moments
        }
        
        output_file = Path("./data/moments.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已转换 {len(moments)} 条说说到 {output_file}")
        return True
    
    def _transform_moments(self, data):
        """转换说说数据格式"""
        moments = []
        
        # 处理不同的数据格式
        if isinstance(data, list):
            source_moments = data
        elif isinstance(data, dict):
            if 'moments' in data:
                source_moments = data['moments']
            elif 'data' in data:
                source_moments = data['data']
            else:
                source_moments = [data]
        
        for i, m in enumerate(source_moments):
            # 解析不同的时间格式
            created_at = m.get('created_time') or m.get('createTime') or m.get('time', '')
            if created_at:
                # 转换为标准格式
                try:
                    if isinstance(created_at, int):
                        # 时间戳
                        from datetime import datetime
                        created_at = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            moment = {
                'id': str(m.get('id', i + 1)),
                'content': m.get('content', '') or m.get('text', '') or m.get('msg', ''),
                'images': self._extract_images(m),
                'created_at': created_at,
                'like_count': m.get('likeNum', 0) or m.get('favnum', 0) or 0,
                'comment_count': m.get('commentNum', 0) or m.get('cmtnum', 0) or 0,
                'comments': self._extract_comments(m),
                'location': m.get('location', '') or m.get('lbs', {}).get('name', '') if isinstance(m.get('lbs'), dict) else ''
            }
            
            moments.append(moment)
        
        # 按时间排序
        moments.sort(key=lambda x: x['created_at'], reverse=True)
        return moments
    
    def _extract_images(self, m):
        """提取图片"""
        images = []
        
        # 尝试不同的字段
        pic_fields = ['pic', 'pics', 'pic_urls', 'images', 'image']
        for field in pic_fields:
            if field in m:
                pics = m[field]
                if isinstance(pics, list):
                    for p in pics:
                        if isinstance(p, str):
                            images.append(p)
                        elif isinstance(p, dict):
                            img_url = p.get('url') or p.get('big_url') or p.get('small_url') or ''
                            if img_url:
                                images.append(img_url)
                elif isinstance(pics, str):
                    images.append(pics)
        
        return images
    
    def _extract_comments(self, m):
        """提取评论"""
        comments = []
        
        comment_field = m.get('commentlist') or m.get('comments', []) or []
        if isinstance(comment_field, list):
            for c in comment_field:
                if isinstance(c, dict):
                    comments.append({
                        'content': c.get('content', '') or c.get('text', ''),
                        'author': c.get('nickname', '') or c.get('name', '') or c.get('uin', '')
                    })
        
        return comments


# ==================== 主函数 ====================
def main():
    print("=" * 50)
    print("QzoneExporter 对接工具")
    print("=" * 50)
    
    qq = input("请输入你的QQ号: ").strip()
    
    exporter = QzoneExporter(qq)
    
    print("\n请选择操作:")
    print("1. 下载 QzoneExporter 工具")
    print("2. 获取Cookie指南")
    print("3. 转换已有数据")
    
    choice = input("\n请输入选项 (1-3): ").strip()
    
    if choice == '1':
        exporter.clone_tool()
    
    elif choice == '2':
        exporter.get_cookie_guide()
    
    elif choice == '3':
        source_dir = input("请输入导出数据目录: ").strip()
        exporter.convert_format(Path(source_dir))
    
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
