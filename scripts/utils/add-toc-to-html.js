const fs = require('fs');

// 读取原始 HTML
const htmlPath = '/Users/chenxiangli/Documents/tsc/docs/OpenClaw 技术深度剖析与部署配置指南.html';
let html = fs.readFileSync(htmlPath, 'utf-8');

// 悬浮目录 HTML
const tocHTML = `
    <!-- 收藏按钮 -->
    <button id="bookmark-btn" onclick="toggleBookmark()" style="position:fixed;top:20px;right:320px;background:#2A81C5;color:#d5f0f8;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;font-size:14px;z-index:1001;transition:all 0.2s ease;box-shadow:0 2px 10px rgba(42,129,197,0.3);">⭐ 收藏本文</button>
    
    <!-- 悬浮目录 -->
    <div id="floating-toc" style="position:fixed;top:20px;right:20px;width:280px;max-height:80vh;overflow-y:auto;background:rgba(23,29,33,0.95);border:1px solid #2A81C5;border-radius:8px;padding:15px;z-index:1000;box-shadow:0 4px 20px rgba(0,0,0,0.4);font-size:13px;line-height:1.6;transition:all 0.3s ease;">
        <h3 onclick="toggleTOC()" style="margin:0 0 10px 0;padding:0 0 8px 0;border-bottom:2px solid #2A81C5;color:#d5f0f8;font-size:15px;font-weight:bold;display:flex;justify-content:space-between;align-items:center;cursor:pointer;">
            📑 目录导航
            <span id="toc-toggle" style="font-size:18px;transition:transform 0.3s ease;">▼</span>
        </h3>
        <div id="toc-content" style="transition:max-height 0.3s ease,opacity 0.3s ease;max-height:1000px;opacity:1;">
            <ul id="toc-list" style="list-style:none;padding:0;margin:0;">
                <!-- 目录项将由 JavaScript 自动生成 -->
            </ul>
        </div>
    </div>

    <script>
        // 自动生成目录
        function generateTOC() {
            const tocList = document.getElementById('toc-list');
            const headings = document.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]');
            
            headings.forEach(heading => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#' + heading.id;
                a.textContent = heading.textContent.replace(/^[#\\s]+/, '');
                a.className = 'toc-' + heading.tagName.toLowerCase();
                a.style.color = '#b5bcc7';
                a.style.textDecoration = 'none';
                a.style.display = 'block';
                a.style.padding = '3px 8px';
                a.style.borderRadius = '4px';
                a.style.transition = 'all 0.2s ease';
                
                if (heading.tagName === 'H1') { a.style.fontWeight = 'bold'; a.style.color = '#d5f0f8'; a.style.marginTop = '8px'; }
                else if (heading.tagName === 'H2') { a.style.paddingLeft = '12px'; a.style.fontSize = '13px'; }
                else if (heading.tagName === 'H3') { a.style.paddingLeft = '24px'; a.style.fontSize = '12px'; a.style.color = '#9a9a9a'; }
                else if (heading.tagName === 'H4') { a.style.paddingLeft = '36px'; a.style.fontSize = '11px'; a.style.color = '#7a7a7a'; }
                
                a.onclick = function(e) {
                    e.preventDefault();
                    const target = document.getElementById(heading.id);
                    if (target) {
                        window.scrollTo({ top: target.offsetTop - 20, behavior: 'smooth' });
                        document.querySelectorAll('#toc-list a').forEach(link => link.style.background = '');
                        a.style.background = 'rgba(42,129,197,0.3)';
                        a.style.color = '#d5f0f8';
                        a.style.borderLeft = '3px solid #2A81C5';
                    }
                };
                
                a.onmouseover = function() {
                    this.style.background = 'rgba(42,129,197,0.2)';
                    this.style.color = '#5ce1e6';
                };
                a.onmouseout = function() {
                    if (!this.style.borderLeft) {
                        this.style.background = '';
                        this.style.color = '#b5bcc7';
                    }
                };
                
                li.appendChild(a);
                tocList.appendChild(li);
            });
        }
        
        function toggleTOC() {
            const content = document.getElementById('toc-content');
            const toggle = document.getElementById('toc-toggle');
            if (content.style.maxHeight === '0px') {
                content.style.maxHeight = '1000px';
                content.style.opacity = '1';
                toggle.style.transform = 'rotate(0deg)';
            } else {
                content.style.maxHeight = '0px';
                content.style.opacity = '0';
                toggle.style.transform = 'rotate(-90deg)';
            }
        }
        
        function toggleBookmark() {
            const btn = document.getElementById('bookmark-btn');
            const isBookmarked = localStorage.getItem('openclaw-doc-bookmarked') === 'true';
            
            if (isBookmarked) {
                localStorage.removeItem('openclaw-doc-bookmarked');
                localStorage.removeItem('openclaw-doc-bookmark-time');
                btn.style.background = '#2A81C5';
                btn.textContent = '⭐ 收藏本文';
                alert('已取消收藏');
            } else {
                localStorage.setItem('openclaw-doc-bookmarked', 'true');
                localStorage.setItem('openclaw-doc-bookmark-time', new Date().toISOString());
                btn.style.background = '#f39c12';
                btn.textContent = '⭐ 已收藏';
                alert('已收藏本文！下次访问时会自动标记。');
            }
        }
        
        function checkBookmarkStatus() {
            const btn = document.getElementById('bookmark-btn');
            const isBookmarked = localStorage.getItem('openclaw-doc-bookmarked') === 'true';
            if (isBookmarked) {
                btn.style.background = '#f39c12';
                btn.textContent = '⭐ 已收藏';
            }
        }
        
        window.addEventListener('load', function() {
            generateTOC();
            checkBookmarkStatus();
        });
    <\/script>
`;

// 在 body 标签后插入
html = html.replace('<body>', '<body>\n' + tocHTML);

// 添加移动端适配 CSS
const mobileCSS = `
<style>
@media (max-width: 768px) {
    #floating-toc, #bookmark-btn { display: none; }
}
#floating-toc::-webkit-scrollbar { width: 6px; }
#floating-toc::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); border-radius: 3px; }
#floating-toc::-webkit-scrollbar-thumb { background: #2A81C5; border-radius: 3px; }
#floating-toc::-webkit-scrollbar-thumb:hover { background: #3a91d5; }
</style>
`;

// 在 head 结束前添加
html = html.replace('</head>', mobileCSS + '\n</head>');

// 写入新文件
const outputPath = '/Users/chenxiangli/Documents/tsc/docs/OpenClaw 技术深度剖析与部署配置指南 (带目录).html';
fs.writeFileSync(outputPath, html, 'utf-8');

console.log('✅ HTML 文件已更新，悬浮目录已添加');
console.log('输出文件:', outputPath);
