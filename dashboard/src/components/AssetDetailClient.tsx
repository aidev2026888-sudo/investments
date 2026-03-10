"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getSignalColor, getSignalBgColor } from "@/lib/types";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import ImageLightbox from "@/components/ImageLightbox";
import { AssetIcon } from "@/components/AssetIcon";

// Reusable SVG back icon
const BackIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
    </svg>
);

interface AssetDetailClientProps {
    asset: {
        slug: string;
        name: string;
        icon: string;
        reportDir: string;
    };
    signal: string;
    score: number;
    latestDate: string | null;
    reportContent: string | null;
    readmeContent: string | null;
    charts: string[];
    history: { date: string; signal: string; score: number }[];
}

export default function AssetDetailClient({
    asset,
    signal,
    score,
    latestDate,
    reportContent,
    readmeContent,
    charts,
    history,
}: AssetDetailClientProps) {
    const [activeTab, setActiveTab] = useState(0);
    const [running, setRunning] = useState(false);
    const [runResult, setRunResult] = useState<{ status: string; message: string; } | null>(null);

    // Scroll to top on mount for clean cinematic reveal
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    const tabs = [
        { label: "Latest Report" },
        { label: "Methodology" },
        { label: "Historical Trends" },
    ];

    async function handleRun() {
        setRunning(true);
        setRunResult(null);
        try {
            const res = await fetch(`/api/run/${asset.reportDir}`, { method: "POST" });
            const data = await res.json();
            setRunResult(data);
            if (data.status === "ok") {
                setTimeout(() => window.location.reload(), 1500);
            }
        } catch (err) {
            setRunResult({
                status: "error",
                message: err instanceof Error ? err.message : "Network error",
            });
        } finally {
            setRunning(false);
        }
    }

    const badgeStyle = {
        color: getSignalColor(signal),
        backgroundColor: getSignalBgColor(signal),
    };

    return (
        <div style={{ background: "transparent", minHeight: "100vh" }}>
            <nav className="nav">
                <Link href="/" className="nav__brand" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <BackIcon />
                    <span>Global Markets</span>
                </Link>
                {latestDate && <div className="nav__date">{latestDate}</div>}
            </nav>

            <div className="detail">
                <div className="detail__hero">
                    <div className="detail__icon">
                        <AssetIcon slug={asset.slug} />
                    </div>
                    <div style={{ flex: 1 }}>
                        <h1 className="detail__title">{asset.name}</h1>
                        <div className="detail__meta">
                            <span
                                className="signal-badge"
                                style={{
                                    ...badgeStyle,
                                    fontSize: "12px",
                                    height: "28px",
                                    padding: "0 16px",
                                    letterSpacing: "0.08em"
                                }}
                            >
                                {signal.replace(/[<>]/g, "").trim()}
                            </span>
                            <span className="detail__score">
                                Structural Score: <strong>{score >= 0 ? "+" : ""}{score}</strong>
                            </span>
                        </div>
                    </div>

                    {/* Run Analysis Button */}
                    <button
                        className="run-btn"
                        onClick={handleRun}
                        disabled={running}
                    >
                        {running ? (
                            <>
                                <span className="run-btn__spinner" />
                                Processing
                            </>
                        ) : (
                            <>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                </svg>
                                Run Analysis
                            </>
                        )}
                    </button>
                </div>

                {runResult && (
                    <div className={`feedback ${runResult.status === "ok" ? "feedback--ok" : "feedback--error"}`}>
                        {runResult.message}
                    </div>
                )}

                {/* Tabs Component Integration */}
                <div className="tabs">
                    {tabs.map((tab, i) => (
                        <button
                            key={i}
                            className={`tab ${i === activeTab ? "tab--active" : ""}`}
                            onClick={() => setActiveTab(i)}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div key={activeTab} style={{ animation: "fadeIn 0.4s var(--spring)" }}>
                    {activeTab === 0 && (
                        <div>
                            {reportContent ? (
                                <>
                                    {renderInterleavedReport(reportContent, charts, asset.name)}
                                </>
                            ) : (
                                <div className="empty">
                                    <svg className="empty__icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                        <polyline points="14 2 14 8 20 8"></polyline>
                                        <line x1="16" y1="13" x2="8" y2="13"></line>
                                        <line x1="16" y1="17" x2="8" y2="17"></line>
                                        <polyline points="10 9 9 9 8 9"></polyline>
                                    </svg>
                                    <div className="empty__text">
                                        Report pending. Tap <strong>Run Analysis</strong> above
                                        or execute <code>python run_all.py</code> natively.
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 1 && (
                        <div>
                            {readmeContent ? (
                                <MarkdownRenderer content={readmeContent} />
                            ) : (
                                <div className="empty">
                                    <div className="empty__text">
                                        Methodology documentation unavailable.
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 2 && (
                        <div>
                            {history.length > 0 ? (
                                <div className="history-wrap">
                                    <h3>Signal Timeline</h3>
                                    <table className="history-table">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Signal</th>
                                                <th>Score</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {history.map((h, i) => (
                                                <tr key={i}>
                                                    <td style={{ fontVariantNumeric: "tabular-nums" }}>{h.date}</td>
                                                    <td>
                                                        <span style={{ color: getSignalColor(h.signal), fontWeight: 600 }}>
                                                            {h.signal.replace(/[<>]/g, "").trim()}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <strong>{h.score >= 0 ? "+" : ""}{h.score}</strong>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <div className="empty">
                                    <div className="empty__text">
                                        No historical signal data accumulated.
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

/**
 * Dynamically parse the markdown report to interleave charts directly beneath their corresponding headers.
 * E.g., The "Summary" heatmap goes beneath "## Summary", and the USD dashboard goes beneath "## USD".
 * Any charts that don't match a section are gracefully rendered at the top.
 */
function renderInterleavedReport(content: string, charts: string[], assetName: string) {
    const parts = content.split(/(?=^## )/m);
    const usedCharts = new Set<string>();

    const sections = parts.map((part, index) => {
        const lines = part.split("\n");
        const firstLine = lines[0].trim();
        let matchedChartUrl: string | null = null;
        
        if (firstLine.startsWith("## ")) {
            const header = firstLine.replace("## ", "").trim().toLowerCase();
            
            if (header === "summary") {
                matchedChartUrl = charts.find(c => c.toLowerCase().includes("heatmap")) || null;
            } else {
                matchedChartUrl = charts.find(c => {
                    const filename = c.split('/').pop()?.toLowerCase() || '';
                    return filename.includes(`${header}_valuation`);
                }) || null;
            }
        }
        
        if (matchedChartUrl) {
            usedCharts.add(matchedChartUrl);
            const body = lines.slice(1).join("\n");
            return (
                <div key={index} className="report-section" style={{ marginBottom: "32px", animation: "fadeUp 0.6s var(--spring)" }}>
                    <MarkdownRenderer content={firstLine + "\n"} />
                    <div style={{ margin: "24px 0" }}>
                        <ImageLightbox src={matchedChartUrl} alt={`Chart for ${firstLine}`} />
                    </div>
                    <MarkdownRenderer content={body} />
                </div>
            );
        }

        return (
            <div key={index} style={{ marginBottom: matchedChartUrl ? "0" : "16px" }}>
                <MarkdownRenderer content={part} />
            </div>
        );
    });

    const unusedCharts = charts.filter(c => !usedCharts.has(c));

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {unusedCharts.length > 0 && (
                <div style={{ marginBottom: "16px" }}>
                    {unusedCharts.map((chart, i) => (
                        <div key={`unused-${i}`} style={{ marginBottom: "32px" }}>
                            <ImageLightbox src={chart} alt={`${assetName} chart ${i + 1}`} />
                        </div>
                    ))}
                </div>
            )}
            <div>{sections}</div>
        </div>
    );
}
