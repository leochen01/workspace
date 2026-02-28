import markdown
from weasyprint import HTML, CSS

# Read markdown file
with open('pathfinder-complete-documentation.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert markdown to HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Wrap with full HTML template
full_html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Pathfinder 完整项目文档</title>
<style>
@page {{ margin: 2cm; size: A4; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 11pt;
  line-height: 1.6;
  color: #1e293b;
  max-width: 21cm;
  margin: 0 auto;
}}
h1 {{ color: #6366f1; font-size: 24pt; border-bottom: 3px solid #6366f1; padding-bottom: 10px; page-break-before: always; }}
h2 {{ color: #4f46e5; font-size: 18pt; margin-top: 20pt; page-break-after: avoid; }}
h3 {{ color: #4f46e5; font-size: 14pt; margin-top: 15pt; page-break-after: avoid; }}
code {{ background: #f1f5f9; color: #e11d48; padding: 2px 6px; border-radius: 4px; font-size: 10pt; }}
pre {{ background: #1e293b; color: #e2e8f0; padding: 15px; border-radius: 5px; overflow-x: auto; page-break-inside: avoid; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; page-break-inside: avoid; }}
th, td {{ border: 1px solid #e2e8f0; padding: 8px 12px; text-align: left; }}
th {{ background: #f8fafc; }}
li {{ margin: 5px 0; }}
ul, ol {{ margin: 10px 0; padding-left: 25px; }}
strong {{ color: #6366f1; }}
</style>
</head>
<body>
{html_content}
</body>
</html>
'''

# Generate PDF
output_pdf = 'pathfinder-documentation.pdf'
HTML(string=full_html).write_pdf(output_pdf)

import os
size_kb = os.path.getsize(output_pdf) / 1024
print(f'✅ PDF generated successfully!')
print(f'📄 File: {output_pdf}')
print(f'📊 Size: {size_kb:.2f} KB')
