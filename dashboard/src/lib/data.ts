import fs from "fs";
import path from "path";
import { DailySummary } from "./types";

const REPORTS_DIR = path.join(process.cwd(), "..", "reports");

/**
 * Get all available report dates (sorted newest first).
 */
export function getReportDates(): string[] {
    try {
        if (!fs.existsSync(REPORTS_DIR)) return [];
        const dirs = fs
            .readdirSync(REPORTS_DIR)
            .filter((d) => /^\d{4}-\d{2}-\d{2}$/.test(d))
            .sort()
            .reverse();
        return dirs;
    } catch {
        return [];
    }
}

/**
 * Load summary.json for a given date.
 */
export function loadSummary(date: string): DailySummary | null {
    try {
        const summaryPath = path.join(REPORTS_DIR, date, "summary.json");
        if (!fs.existsSync(summaryPath)) return null;
        const raw = fs.readFileSync(summaryPath, "utf-8");
        return JSON.parse(raw) as DailySummary;
    } catch {
        return null;
    }
}

/**
 * Load a markdown report file for a given date and asset.
 */
export function loadReport(
    date: string,
    reportDir: string,
    reportPattern?: string
): string | null {
    try {
        const assetDir = path.join(REPORTS_DIR, date, reportDir);
        if (!fs.existsSync(assetDir)) return null;

        // Find the first matching markdown file
        const files = fs.readdirSync(assetDir).filter((f) => f.endsWith(".md"));
        if (reportPattern) {
            const match = files.find((f) =>
                f.toLowerCase().includes(reportPattern.toLowerCase())
            );
            if (match) {
                return fs.readFileSync(path.join(assetDir, match), "utf-8");
            }
        }
        if (files.length > 0) {
            return fs.readFileSync(path.join(assetDir, files[0]), "utf-8");
        }
        return null;
    } catch {
        return null;
    }
}

/**
 * Load a README.md for a given asset, filtering out technical sections.
 * Keeps only financial methodology (metrics, signals, references).
 */
export function loadReadme(readmeDir: string): string | null {
    try {
        const readmePath = path.join(process.cwd(), "..", readmeDir, "README.md");
        if (fs.existsSync(readmePath)) {
            const raw = fs.readFileSync(readmePath, "utf-8");
            return filterMethodology(raw);
        }
        return null;
    } catch {
        return null;
    }
}

/**
 * Filter README content to keep finance explanations only.
 * Strips technical setup sections (Quick Start, Configuration, Dependencies, etc.)
 */
function filterMethodology(content: string): string {
    const technicalHeadings = [
        "quick start", "configuration", "dependencies", "installation",
        "setup", "output", "usage", "getting started", "how to run",
        "running", "file structure", "project structure", "requirements",
    ];

    const lines = content.split("\n");
    const result: string[] = [];
    let skipSection = false;
    let skipLevel = 0;

    for (const line of lines) {
        const headingMatch = line.match(/^(#{1,4})\s+(.+)/);
        if (headingMatch) {
            const level = headingMatch[1].length;
            const title = headingMatch[2].toLowerCase().trim();

            const isTechnical = technicalHeadings.some((h) => title.includes(h));

            if (isTechnical) {
                skipSection = true;
                skipLevel = level;
                continue;
            }

            if (skipSection && level <= skipLevel) {
                skipSection = false;
            }
        }

        if (!skipSection) {
            result.push(line);
        }
    }

    return result.join("\n").trim();
}

/**
 * Get chart image paths for a given date and asset.
 */
export function getChartPaths(date: string, reportDir: string): string[] {
    try {
        const assetDir = path.join(REPORTS_DIR, date, reportDir);
        if (!fs.existsSync(assetDir)) return [];
        return fs
            .readdirSync(assetDir)
            .filter((f) => f.endsWith(".png"))
            .map((f) => `/api/chart/${date}/${reportDir}/${f}`);
    } catch {
        return [];
    }
}

/**
 * Get historical signal data for an asset across all dates.
 */
export function getSignalHistory(
    reportDir: string
): { date: string; signal: string; score: number }[] {
    const dates = getReportDates();
    const history: { date: string; signal: string; score: number }[] = [];

    for (const date of dates) {
        const summary = loadSummary(date);
        if (summary?.assets?.[reportDir]) {
            const asset = summary.assets[reportDir];
            history.push({
                date,
                signal: asset.signal,
                score: asset.score,
            });
        }
    }

    return history;
}
