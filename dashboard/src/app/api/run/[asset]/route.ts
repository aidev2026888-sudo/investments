import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

/**
 * API route to trigger a single asset analyzer run.
 * POST /api/run/{asset}
 *
 * Spawns the Python script, then copies output files (reports + charts)
 * to the dated reports directory — mirroring what run_all.py does.
 */

const ASSET_SCRIPTS: Record<string, { cwd: string; script: string }> = {
    SP500: { cwd: "global_markets/SP500", script: "analyze.py" },
    DAX: { cwd: "global_markets/DAX", script: "analyze.py" },
    CAC40: { cwd: "global_markets/CAC40", script: "analyze.py" },
    FTSE100: { cwd: "global_markets/FTSE100", script: "analyze.py" },
    SMI: { cwd: "global_markets/SMI", script: "analyze.py" },
    PreciousMetals: { cwd: "global_markets/PreciousMetals", script: "analyze.py" },
    FX: { cwd: "global_markets/FX", script: "analyze.py" },
    CIS300: { cwd: "CIS300", script: "PE_percentile.py" },
};

function collectReports(sourceDir: string, destDir: string): number {
    /**
     * Copy generated report files (.md with today's date) and chart PNGs
     * from the source directory to the dated reports directory.
     * Mirrors run_all.py's collect_reports function.
     */
    const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD

    if (!fs.existsSync(destDir)) {
        fs.mkdirSync(destDir, { recursive: true });
    }

    let count = 0;
    try {
        const files = fs.readdirSync(sourceDir);
        for (const file of files) {
            const srcPath = path.join(sourceDir, file);
            if (!fs.statSync(srcPath).isFile()) continue;

            // Copy PNGs (chart images)
            if (file.endsWith(".png")) {
                fs.copyFileSync(srcPath, path.join(destDir, file));
                count++;
            }
            // Copy today's markdown reports
            else if (file.endsWith(".md") && file.includes("report") && file.includes(today)) {
                fs.copyFileSync(srcPath, path.join(destDir, file));
                count++;
            }
            // Copy any markdown report if no date-specific one found
            else if (file.endsWith(".md") && file.includes("report")) {
                fs.copyFileSync(srcPath, path.join(destDir, file));
                count++;
            }
        }
    } catch {
        // Silently continue
    }
    return count;
}

function updateSummary(rootDir: string, asset: string, destDir: string): void {
    /**
     * Update the summary.json for today with the newly-generated asset data.
     */
    const today = new Date().toISOString().split("T")[0];
    const summaryPath = path.join(rootDir, "reports", today, "summary.json");

    let summary: Record<string, unknown> = { date: today, assets: {} };
    try {
        if (fs.existsSync(summaryPath)) {
            summary = JSON.parse(fs.readFileSync(summaryPath, "utf-8"));
        }
    } catch { /* start fresh */ }

    const assets = (summary.assets || {}) as Record<string, unknown>;

    // Find reports and charts
    const mdFiles = fs.existsSync(destDir)
        ? fs.readdirSync(destDir).filter((f) => f.endsWith(".md"))
        : [];
    const pngFiles = fs.existsSync(destDir)
        ? fs.readdirSync(destDir).filter((f) => f.endsWith(".png"))
        : [];

    if (mdFiles.length > 0) {
        // Try to extract signal from report
        let signal = "N/A";
        let score = 0;
        try {
            const content = fs.readFileSync(path.join(destDir, mdFiles[0]), "utf-8");
            // Match: ## Composite Signal\n**<<< STRONG SELL >>>** — Score: -4
            const m = content.match(/## Composite Signal\s*\n\*\*(.+?)\*\*.*?Score:\s*([+-]?\d+)/);
            if (m) {
                signal = m[1].trim();
                score = parseInt(m[2], 10);
            } else {
                // Chinese format: 综合信号
                const m2 = content.match(/综合信号[：:]\s*(.+?)\s*[（(]评分[：:]\s*([+-]?\d+)/);
                if (m2) {
                    signal = m2[1].trim();
                    score = parseInt(m2[2], 10);
                }
            }
        } catch { /* ignore */ }

        assets[asset] = {
            signal,
            score,
            status: "ok",
            report_file: mdFiles[0],
            charts: pngFiles,
        };
    } else if (pngFiles.length > 0) {
        // Charts but no markdown report (like CIS300)
        assets[asset] = {
            signal: assets[asset] && (assets[asset] as Record<string, unknown>).signal || "N/A",
            score: assets[asset] && (assets[asset] as Record<string, unknown>).score || 0,
            status: "ok",
            charts: pngFiles,
        };
    }

    summary.assets = assets;

    const reportDir = path.join(rootDir, "reports", today);
    if (!fs.existsSync(reportDir)) fs.mkdirSync(reportDir, { recursive: true });
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2), "utf-8");
}

export async function POST(
    request: NextRequest,
    { params }: { params: Promise<{ asset: string }> }
) {
    const { asset } = await params;
    const config = ASSET_SCRIPTS[asset];

    if (!config) {
        return NextResponse.json(
            { error: `Unknown asset: ${asset}` },
            { status: 404 }
        );
    }

    const rootDir = path.join(process.cwd(), "..");
    const cwd = path.join(rootDir, config.cwd);
    const today = new Date().toISOString().split("T")[0];
    const destDir = path.join(rootDir, "reports", today, asset);

    // Find Python executable
    const venvPython = path.join(rootDir, "venv", "Scripts", "python.exe");
    const python = fs.existsSync(venvPython) ? venvPython : "python";

    return new Promise<NextResponse>((resolve) => {
        const proc = spawn(python, [config.script], {
            cwd,
            env: { ...process.env, PYTHONIOENCODING: "utf-8" },
            timeout: 300000,
        });

        let stdout = "";
        let stderr = "";

        proc.stdout?.on("data", (data) => { stdout += data.toString(); });
        proc.stderr?.on("data", (data) => { stderr += data.toString(); });

        proc.on("close", (code) => {
            if (code === 0) {
                // Copy reports + charts to dated reports directory
                const copied = collectReports(cwd, destDir);
                // Update summary.json
                updateSummary(rootDir, asset, destDir);

                resolve(
                    NextResponse.json({
                        status: "ok",
                        message: `${asset} analysis completed — ${copied} file(s) collected`,
                        output: stdout.slice(-500),
                    })
                );
            } else {
                resolve(
                    NextResponse.json(
                        {
                            status: "error",
                            message: `${asset} analysis failed (exit code ${code})`,
                            error: stderr.slice(-500),
                        },
                        { status: 500 }
                    )
                );
            }
        });

        proc.on("error", (err) => {
            resolve(
                NextResponse.json(
                    { status: "error", message: err.message },
                    { status: 500 }
                )
            );
        });
    });
}
