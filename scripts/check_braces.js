const fs = require('fs');
const path = require('path');
const target = path.join(__dirname, '..', 'React', 'src', 'pages', 'ProductRawMaterials.jsx');
const s = fs.readFileSync(target, 'utf8');
let counts = { '(':0, ')':0, '{':0, '}':0, '[':0, ']':0 };
for (const ch of s) if (counts.hasOwnProperty(ch)) counts[ch]++;
console.log('Counts:', counts);
// Show last 60 lines for context
const lines = s.split(/\r?\n/);
console.log('\nLast 60 lines:');
console.log(lines.slice(-60).map((l,i)=>`${lines.length-60+i+1}: ${l}`).join('\n'));
