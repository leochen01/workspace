const fs = require('fs');
const HtmlPdfNode = require('html-pdf-node');

const htmlContent = fs.readFileSync('pathfinder-complete.html', 'utf8');

const options = {
  format: 'A4',
  margin: { top: '2cm', right: '2cm', bottom: '2cm', left: '2cm' },
  printBackground: true,
};

HtmlPdfNode.generatePdf({ content: htmlContent, htmlPdfNode: { options } }, (err, buffer) => {
  if (!err) {
    fs.writeFileSync('pathfinder-complete-documentation.pdf', buffer);
    console.log('✅ PDF generated successfully!');
    console.log('📄 File: pathfinder-complete-documentation.pdf');
    const stats = fs.statSync('pathfinder-complete-documentation.pdf');
    console.log('📊 Size:', (stats.size / 1024).toFixed(2), 'KB');
  } else {
    console.log('❌ Error:', err.message);
  }
});
