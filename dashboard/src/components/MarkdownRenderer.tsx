interface MarkdownRendererProps {
    content: string;
}

/**
 * Simple server-side markdown-to-HTML renderer.
 * Handles the subset of markdown used in our reports:
 * headers, tables, lists, bold, code, blockquotes, links, images.
 */
export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
    const html = markdownToHtml(content);
    return (
        <div className="report" dangerouslySetInnerHTML={{ __html: html }} />
    );
}

function markdownToHtml(md: string): string {
    let html = md;

    // Escape HTML entities (but preserve our own tags later)
    html = html
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italic
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Links
    html = html.replace(
        /\[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener">$1</a>'
    );

    // Images
    html = html.replace(
        /!\[([^\]]*)\]\(([^)]+)\)/g,
        '<img src="$2" alt="$1" />'
    );

    // Blockquotes
    html = html.replace(
        /^&gt; (.+)$/gm,
        "<blockquote>$1</blockquote>"
    );

    // Tables
    html = convertTables(html);

    // Unordered lists
    html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`);

    // Horizontal rules
    html = html.replace(/^---$/gm, "<hr />");

    // Paragraphs: wrap loose lines
    html = html.replace(/^(?!<[a-z/])((?!^\s*$).+)$/gm, "<p>$1</p>");

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, "");

    return html;
}

function convertTables(html: string): string {
    const lines = html.split("\n");
    const result: string[] = [];
    let inTable = false;
    let headerDone = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        const isTableRow = line.startsWith("|") && line.endsWith("|");

        if (isTableRow) {
            // Check if this is a separator row (|---|---|)
            const isSeparator = /^\|[\s-:|]+\|$/.test(line);

            if (isSeparator) {
                headerDone = true;
                continue;
            }

            if (!inTable) {
                result.push("<table>");
                inTable = true;
                headerDone = false;
            }

            const cells = line
                .split("|")
                .filter((c) => c.trim() !== "")
                .map((c) => c.trim());

            if (!headerDone) {
                result.push(
                    "<thead><tr>" +
                    cells.map((c) => `<th>${c}</th>`).join("") +
                    "</tr></thead><tbody>"
                );
            } else {
                result.push(
                    "<tr>" + cells.map((c) => `<td>${c}</td>`).join("") + "</tr>"
                );
            }
        } else {
            if (inTable) {
                result.push("</tbody></table>");
                inTable = false;
                headerDone = false;
            }
            result.push(lines[i]);
        }
    }

    if (inTable) {
        result.push("</tbody></table>");
    }

    return result.join("\n");
}
