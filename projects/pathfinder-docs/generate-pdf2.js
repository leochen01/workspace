const fs = require('fs');
const { htmlToPdf } = require('html-pdf-node');

const htmlContent = fs.readFileSync('pathfinder-complete.html', 'utf8');

const options = {
  format: 'A4',
  margin: { top: '2cm', right: '2cm', bottom: '2cm', left: '2cm' },
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: '<div style="font-size:10px;margin-left:2cm;">Pathfinder 文档</div>',
  footerTemplate: '<div style="font-size:10px;margin-right:2cm;text-align:center;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
};

htmlToPdf({ content: htmlContent, htmlPdfNode: { options } }, (err, buffer) => {
  if (!err) {
    fs.writeFileSync('pathfinder-complete-documentation.pdf', buffer);
    console.log('✅ PDF generated successfully!');
    console.log('📄 File: pathfinder-complete-documentation.pdf');
    console.log('📊 Size:', (fs.statSync('pathfinder-complete-documentation.pdf').size / 1024).toFixed(2), 'KB');
  } else {
    console.log('❌ Error:', err.message);
  }
});
