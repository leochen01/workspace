const fs = require('fs');
const PdfKit = require('pdfkit');

// Read markdown content
const mdContent = fs.readFileSync('pathfinder-complete-documentation.md', 'utf8');

// Create PDF document
const doc = new PdfKit({ size: 'A4', margin: 50 });
const pdfStream = fs.createWriteStream('pathfinder-documentation.pdf');
doc.pipe(pdfStream);

// Add title
doc.fontSize(24).fillColor('#6366f1').text('Pathfinder 创业决策支持平台', { align: 'center' });
doc.moveDown();
doc.fontSize(12).fillColor('#64748b').text('完整项目文档 - 包含商业计划书、需求分析、技术架构', { align: 'center' });
doc.moveDown(2);

// Simple markdown parser
const lines = mdContent.split('\n');
let inList = false;

lines.forEach((line, i) => {
  if (line.startsWith('# ')) {
    if (inList) { doc.endList(); inList = false; }
    doc.addPage();
    doc.fontSize(20).fillColor('#4f46e5').text(line.replace('# ', ''), { align: 'left' });
    doc.moveDown();
  } else if (line.startsWith('## ')) {
    if (inList) { doc.endList(); inList = false; }
    doc.fontSize(16).fillColor('#4f46e5').text(line.replace('## ', ''), { align: 'left' });
    doc.moveDown(0.5);
  } else if (line.startsWith('### ')) {
    if (inList) { doc.endList(); inList = false; }
    doc.fontSize(14).fillColor('#4f46e5').text(line.replace('### ', ''), { align: 'left' });
    doc.moveDown(0.3);
  } else if (line.startsWith('- ')) {
    if (!inList) { doc.list = []; inList = true; }
    doc.fontSize(11).fillColor('#1e293b').text('• ' + line.replace('- ', ''), { indent: 20 });
  } else if (line.match(/^\d+\./)) {
    if (!inList) { doc.list = []; inList = true; }
    doc.fontSize(11).fillColor('#1e293b').text(line, { indent: 20 });
  } else if (line.trim() && !line.startsWith('---')) {
    if (inList) { inList = false; }
    doc.fontSize(11).fillColor('#475569').text(line, { align: 'justify' });
    doc.moveDown(0.3);
  }
});

// Finalize
doc.end();

pdfStream.on('finish', () => {
  console.log('✅ PDF generated successfully!');
  console.log('📄 File: pathfinder-documentation.pdf');
  const stats = fs.statSync('pathfinder-documentation.pdf');
  console.log('📊 Size:', (stats.size / 1024).toFixed(2), 'KB');
});
