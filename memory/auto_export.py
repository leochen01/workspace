#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动导出QQ说说 - 浏览器自动化版
使用Playwright自动登录并导出说说
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime

# ==================== 配置 ====================
CONFIG = {
    "qq": "your_qq_number",
    "password": "your_password",  # QQ密码（可选，会尝试扫码）
    "cookie_file": "./cookies.json",
    "export_dir": "./exported_data"
}

# ==================== 数据格式转换 ====================
class QzoneExporter:
    def __init__(self):
        self.cookies = None
        self.moments = []
    
    def save_cookies(self, cookies):
        """保存Cookie"""
        with open(CONFIG["cookie_file"], 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"✅ Cookie已保存到 {CONFIG['cookie_file']}")
    
    def load_cookies(self):
        """加载Cookie"""
        if os.path.exists(CONFIG["cookie_file"]):
            with open(CONFIG["cookie_file"], 'r') as f:
                self.cookies = json.load(f)
            return True
        return False
    
    async def export_with_playwright(self):
        """使用Playwright导出说说"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("❌ 需要安装 playwright")
            print("   pip install playwright")
            print("   playwright install chromium")
            return False
        
        print("🚀 启动浏览器...")
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            
            # 访问QQ空间登录页面
            page = await context.new_page()
            
            print("📱 请在浏览器中扫码登录QQ空间...")
            print("   登录成功后程序将自动继续")
            
            # 访问QQ空间
            await page.goto("https://qzone.qq.com/")
            
            # 等待登录
            await page.wait_for_url("https://user.qzone.qq.com/*", timeout=120)
            
            print("✅ 登录成功！")
            
            # 获取Cookie
            cookies = await context.cookies()
            self.save_cookies(cookies)
            
            # 获取QQ号
            qq_number = page.url.split('/')[-1]
            print(f"📋 检测到QQ号: {qq_number}")
            
            # 访问说说页面
            print("📥 正在获取说说数据...")
            
            # 方法：通过API获取说说
            # QQ空间说说API
            moment_list = []
            
            # 尝试获取说说
            try:
                # 构造API请求
                uin = qq_number
                hostUin = uin
                func = 0
                needSparse = 0
                os = "O2"
                start = 0
                count = 50
                
                api_url = f"https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/taotao/cgi_get_mood_abstract?uin={uin}"
                
                # 由于QQ空间API需要复杂的签名，这里提供手动方案
                print("⚠️ QQ空间API需要复杂签名，建议使用以下方案：")
                print("")
                print("方案1：使用QzoneExporter（推荐）")
                print("   1. 访问 https://github.com/OwnGitee/QzoneExporter")
                print("   2. 下载并运行工具")
                print("   3. 导出说说为JSON格式")
                print("   4. 使用本工具的 convert 命令转换格式")
                print("")
                print("方案2：手动导出")
                print("   1. 登录QQ空间")
                print("   2. 打开说说页面")
                print("   3. 手动复制内容到文件")
                
            except Exception as e:
                print(f"❌ 获取失败: {e}")
            
            await browser.close()
            
        return True
    
    def convert_from_file(self, source_file, images_dir=None):
        """从文件转换"""
        print(f"📂 正在读取: {source_file}")
        
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        moments = self._transform(source_data)
        
        # 保存结果
        output = {
            "user": {
                "qq": CONFIG["qq"],
                "nickname": "用户"
            },
            "moments": moments
        }
        
        output_file = Path("./data/moments.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已转换 {len(moments)} 条说说到 {output_file}")
        
        # 统计
        print(f"\n📊 统计:")
        print(f"   - 说说总数: {len(moments)}")
        
        # 计算年份
        years = {}
        for m in moments:
            year = m['created_at'][:4]
            years[year] = years.get(year, 0) + 1
        
        for year, count in sorted(years.items(), reverse=True):
            print(f"   - {year}年: {count}条")
        
        return True
    
    def _transform(self, data):
        """转换数据格式"""
        moments = []
        
        # 处理不同格式
        if isinstance(data, list):
            source_moments = data
        elif isinstance(data, dict):
            # 尝试找到说说列表
            for key in ['moments', 'shuoshuo', 'mood', 'data', 'list', 'result', 'msglist']:
                if key in data:
                    source_moments = data[key]
                    if isinstance(source_moments, dict) and 'list' in source_moments:
                        source_moments = source_moments['list']
                    break
            else:
                source_moments = [data]
        else:
            return []
        
        for i, m in enumerate(source_moments):
            if not isinstance(m, dict):
                continue
            
            # 时间处理
            created_at = ""
            for time_field in ['created_time', 'createTime', 'time', 'datetime', 'pubtime', 'modifyTime']:
                if time_field in m:
                    ts = m[time_field]
                    if isinstance(ts, int):
                        try:
                            created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = str(ts)
                    else:
                        created_at = str(ts)
                    break
            
            # 内容
            content = m.get('content') or m.get('text') or m.get('msg') or m.get('message', '')
            
            # 图片
            images = []
            for img_field in ['pic', 'pics', 'pic_urls', 'images', 'image', 'attach']:
                if img_field in m:
                    pics = m[img_field]
                    if isinstance(pics, list):
                        for p in pics:
                            if isinstance(p, str):
                                images.append(p)
                            elif isinstance(p, dict):
                                url = p.get('url') or p.get('big_url') or p.get('small_url') or p.get('raw_url') or ''
                                if url:
                                    images.append(url)
            
            # 点赞评论
            like_count = m.get('likeNum') or m.get('favnum') or m.get('likenum') or 0
            comment_count = m.get('commentNum') or m.get('cmtnum') or m.get('commentnum') or 0
            
            # 评论
            comments = []
            for c_field in ['commentlist', 'comments', 'cmts']:
                if c_field in m and isinstance(m[c_field], list):
                    for c in m[c_field]:
                        if isinstance(c, dict):
                            comments.append({
                                'content': c.get('content') or c.get('text') or '',
                                'author': c.get('nickname') or c.get('name') or c.get('uin') or ''
                            })
            
            # 位置
            location = ""
            for loc_field in ['location', 'lbs', 'position']:
                if loc_field in m:
                    if isinstance(m[loc_field], dict):
                        location = m[loc_field].get('name') or m[loc_field].get('title') or ''
                    else:
                        location = str(m[loc_field])
            
            moment = {
                'id': str(m.get('id', i + 1)),
                'content': content,
                'images': images,
                'created_at': created_at,
                'like_count': int(like_count) if like_count else 0,
                'comment_count': int(comment_count) if comment_count else 0,
                'comments': comments,
                'location': location
            }
            
            moments.append(moment)
        
        # 排序
        moments.sort(key=lambda x: x['created_at'], reverse=True)
        return moments


async def main():
    import sys
    
    exporter = QzoneExporter()
    
    if len(sys.argv) < 2:
        print("QQ说说自动导出工具")
        print("")
        print("用法:")
        print("  python auto_export.py login      - 登录并获取Cookie")
        print("  python auto_export.py convert    - 转换已有数据文件")
        print("  python auto_export.py convert <文件> - 转换指定文件")
        print("")
        return
    
    command = sys.argv[1]
    
    if command == "login":
        await exporter.export_with_playwright()
    
    elif command == "convert":
        if len(sys.argv) > 2:
            source_file = sys.argv[2]
        else:
            # 查找常见文件
            possible = [
                "moments.json",
                "shuoshuo.json", 
                "说说.json",
                "../导出结果/moments.json",
                "./exported_data/moments.json"
            ]
            source_file = None
            for p in possible:
                if os.path.exists(p):
                    source_file = p
                    break
            
            if not source_file:
                print("❌ 请指定要转换的文件")
                print("   python auto_export.py convert <文件>")
                return
        
        exporter.convert_from_file(source_file)
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    asyncio.run(main())
