const fs = require('fs');
const path = require('path');
const cwd = process.cwd();
const REPORTS_DIR = path.join(cwd, "..", "reports");
console.log('CWD:', cwd);
console.log('REPORTS_DIR:', REPORTS_DIR);
console.log('Exists?', fs.existsSync(REPORTS_DIR));
if (fs.existsSync(REPORTS_DIR)) {
    const dirs = fs.readdirSync(REPORTS_DIR).filter((d) => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort().reverse();
    console.log('Dates:', dirs);
}
