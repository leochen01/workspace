const { exec } = require('child_process');
const fs = require('fs');

// Create a simple Node.js PDF generator
const pdfContent = `
const puppeteer = require('puppeteer');
const path = require('path');

async function generatePDF() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  const htmlPath = path.join(__dirname, 'pathfinder-complete.html');
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle0' });
  
  const pdfPath = path.join(__dirname, 'pathfinder-complete-documentation.pdf');
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: { top: '2cm', right: '2cm', bottom: '2cm', left: '2cm' },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:10px;margin-left:2cm;">Pathfinder 文档</div>',
    footerTemplate: '<div style="font-size:10px;margin-right:2cm;text-align:center;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
  });
  
  await browser.close();
  console.log('✅ PDF saved to:', pdfPath);
catch(}

generatePDF().console.error);
`;

// Check if we can use a pre-installed tool
exec('which wkhtmltopdf', (error, stdout) => {
  if (stdout.trim()) {
    console.log('✅ Found wkhtmltopdf, generating PDF...');
    exec(`wkhtmltopdf --enable-local-file-access --quiet --print-media-type --margin-top 2cm --margin-bottom 2cm --margin-left 2cm --margin-right 2cm pathfinder-complete.html pathfinder-complete-documentation.pdf`, (err) => {
      if (!err) {
        const stats = fs.statSync('pathfinder-complete-documentation.pdf');
        console.log('✅ PDF generated successfully!');
        console.log('📄 File:', 'pathfinder-complete-documentation.pdf');
        console.log('📊 Size:', (stats.size / 1024).toFixed(2), 'KB');
      } else {
        console.log('❌ wkhtmltopdf failed');
      }
    });
  } else {
    console.log('📄 PDF工具未安装。创建打印脚本...');
    
    fs.writeFileSync('generate-pdf.js', pdfContent);
    console.log('✅ 打印脚本已创建: generate-pdf.js');
    console.log('');
    console.log('📋 使用方法:');
    console.log('1. 双击打开 pathfinder-complete.html');
    console.log('2. 按 Ctrl+P (Windows) 或 Cmd+P (Mac)');
    console.log('3. 选择 "另存为 PDF"');
    console.log('4. 边距设置为 "无" 或 "最小"');
    console.log('');
    console.log('或安装 Puppeteer 后运行:');
    console.log('  npm install puppeteer');
    console.log('  node generate-pdf.js');
  }
});
