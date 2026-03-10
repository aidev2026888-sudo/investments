const fs = require('fs');
const md = fs.readFileSync('c:/work/workspaces/investments/investments/reports/2026-03-10/CIS300/CSI300_report_2026-03-10.md', 'utf-8');

let html = md;
html = html.replace(/\*\*Signal:\*\* .*?\n/gi, '');
html = html.replace(/\*\*Score:\*\* .*?\n/gi, '');
html = html.replace(/&/g, &amp;).replace(/</g, &lt;).replace(/>/g, &gt;);
html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
html = html.replace(/^## (.+)$/gm, '<h2><span style="color: var(--accent-blue); margin-right: 8px;">//</span> $1</h2>');
html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />');
html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => '<ul>' + match + '</ul>');
html = html.replace(/^---$/gm, '<hr />');
html = html.replace(/^(?!<[a-z/])((?!^\s*$).+)$/gm, '<p>$1</p>');
html = html.replace(/<p>\s*<\/p>/g, '');

console.log('Result length:', html.length);
if (html.length < 100) console.log('CONTENT:', html);
