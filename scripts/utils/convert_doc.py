#!/usr/bin/env python3
import subprocess
import sys
import os

doc_dir = "/Users/chenxiangli/Documents/zzxy/专利"
doc_pattern = "202512-*.doc"
output_md = os.path.join(doc_dir, "202512-技术方案.md")
temp_doc = "/tmp/temp_patent.doc"

# 先复制文件到临时位置（避免中文路径问题）
import shutil
import glob

doc_files = glob.glob(os.path.join(doc_dir, doc_pattern))
if not doc_files:
    print(f"❌ 未找到文件：{os.path.join(doc_dir, doc_pattern)}")
    sys.exit(1)

doc_file_full = doc_files[0]
print(f"📁 找到文件：{doc_file_full}")

# 复制到临时位置
shutil.copy(doc_file_full, temp_doc)

# 使用 antiword 默认文本输出
try:
    result = subprocess.run(
        ['antiword', temp_doc],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0 and result.stdout.strip():
        content = result.stdout
        # 添加 markdown 标题
        md_content = f"""# 技术方案文档

## 基于大模型的调度风险预警和防控体系构建及智能体实践研究

---

{content}
"""
        with open(output_md, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✅ 转换成功：{output_md}")
        print(f"📊 文件大小：{len(content)} 字符")
    else:
        print(f"❌ antiword 失败：{result.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"❌ 错误：{e}")
    sys.exit(1)
