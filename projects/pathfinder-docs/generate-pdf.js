
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
