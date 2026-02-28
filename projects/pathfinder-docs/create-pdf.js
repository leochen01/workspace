const fs = require('fs');
const { exec } = require('child_process');

// Try to use wkhtmltopdf if available, otherwise create a complete print solution
const htmlFile = 'pathfinder-documentation.html';
const pdfFile = 'pathfinder-documentation.pdf';

// Check if wkhtmltopdf is available
exec('which wkhtmltopdf', (err, stdout) => {
  if (stdout.trim()) {
    console.log('✅ Using wkhtmltopdf to generate PDF...');
    exec(`wkhtmltopdf --enable-local-file-access --quiet ${htmlFile} ${pdfFile}`, (error) => {
      if (!error) {
        console.log(`✅ PDF generated: ${pdfFile}`);
        console.log(`📄 File size: ${(fs.statSync(pdfFile).size / 1024).toFixed(2)} KB`);
      } else {
        console.log('❌ PDF generation failed, showing alternative...');
      }
    });
  } else {
    console.log('📄 wkhtmltopdf not found. Creating print-ready HTML...');
    
    // Read and enhance the HTML
    let html = fs.readFileSync(htmlFile, 'utf8');
    
    // Add print functionality
    const printHtml = html.replace(
      '</body>',
      `
      <script>
        window.onload = function() {
          console.log('Document loaded. To save as PDF:');
          console.log('1. Press Ctrl+P (or Cmd+P on Mac)');
          console.log('2. Select "Save as PDF" as destination');
          console.log('3. Adjust margins to "None" or "Minimum"');
        };
      </script>
      </body>`
    );
    
    fs.writeFileSync('pathfinder-documentation.html', printHtml);
    console.log('✅ Enhanced HTML saved!');
  }
});
