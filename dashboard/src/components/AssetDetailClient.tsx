"use client";

import { useState } from "react";
import Link from "next/link";
import { getSignalColor, getSignalBgColor } from "@/lib/types";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import ImageLightbox from "@/components/ImageLightbox";

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
    const [runResult, setRunResult] = useState<{
        status: string;
        message: string;
    } | null>(null);

    const tabs = [
        { label: "Latest Report" },
        { label: "Methodology" },
        { label: "Historical Trends" },
    ];

    async function handleRun() {
        setRunning(true);
        setRunResult(null);
        try {
            const res = await fetch(`/api/run/${asset.reportDir}`, {
                method: "POST",
            });
            const data = await res.json();
            setRunResult(data);
            if (data.status === "ok") {
                // Reload page after 1.5s to show fresh data
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

    return (
        <>
            <header className="header">
                <div style={{ display: "flex", alignItems: "center" }}>
                    <div className="header__title">
                        <span className="header__logo">GM</span>
                        Global Markets Monitor
                    </div>
                    <span className="header__subtitle">Valuation Dashboard</span>
                </div>
                {latestDate && <div className="header__date">{latestDate}</div>}
            </header>

            <div className="detail">
                <Link href="/" className="detail__back">
                    ← Back to Dashboard
                </Link>

                <div className="detail__header">
                    <span className="card__icon" style={{ width: 48, height: 48, fontSize: "0.9rem" }}>
                        {asset.icon}
                    </span>
                    <div style={{ flex: 1 }}>
                        <h1 className="detail__title">{asset.name}</h1>
                        <div
                            style={{
                                display: "flex",
                                gap: "1rem",
                                alignItems: "center",
                                marginTop: "6px",
                            }}
                        >
                            <span
                                className="card__signal"
                                style={{
                                    color: getSignalColor(signal),
                                    backgroundColor: getSignalBgColor(signal),
                                    fontSize: "0.72rem",
                                }}
                            >
                                {signal.replace(/[<>]/g, "").trim()}
                            </span>
                            <span
                                style={{
                                    color: "var(--color-text-secondary)",
                                    fontSize: "0.88rem",
                                    fontVariantNumeric: "tabular-nums",
                                }}
                            >
                                Score: <strong style={{ color: "var(--color-text)" }}>{score >= 0 ? "+" : ""}{score}</strong>
                            </span>
                        </div>
                    </div>

                    {/* Run trigger button */}
                    <button
                        onClick={handleRun}
                        disabled={running}
                        style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "8px",
                            padding: "8px 20px",
                            borderRadius: "8px",
                            border: "1px solid rgba(99, 91, 255, 0.3)",
                            background: running
                                ? "rgba(99, 91, 255, 0.08)"
                                : "linear-gradient(135deg, rgba(99, 91, 255, 0.15), rgba(14, 165, 233, 0.1))",
                            color: running ? "var(--color-text-muted)" : "#a5b4fc",
                            fontSize: "0.8rem",
                            fontWeight: 600,
                            cursor: running ? "wait" : "pointer",
                            transition: "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
                            fontFamily: "inherit",
                            whiteSpace: "nowrap",
                            flexShrink: 0,
                        }}
                        onMouseEnter={(e) => {
                            if (!running) {
                                e.currentTarget.style.background =
                                    "linear-gradient(135deg, rgba(99, 91, 255, 0.25), rgba(14, 165, 233, 0.15))";
                                e.currentTarget.style.borderColor = "rgba(99, 91, 255, 0.5)";
                                e.currentTarget.style.transform = "translateY(-1px)";
                            }
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background =
                                "linear-gradient(135deg, rgba(99, 91, 255, 0.15), rgba(14, 165, 233, 0.1))";
                            e.currentTarget.style.borderColor = "rgba(99, 91, 255, 0.3)";
                            e.currentTarget.style.transform = "translateY(0)";
                        }}
                    >
                        {running ? (
                            <>
                                <span
                                    style={{
                                        display: "inline-block",
                                        width: 14,
                                        height: 14,
                                        border: "2px solid rgba(99, 91, 255, 0.3)",
                                        borderTopColor: "#a5b4fc",
                                        borderRadius: "50%",
                                        animation: "spin 0.8s linear infinite",
                                    }}
                                />
                                Running...
                            </>
                        ) : (
                            <>▶ Run Analysis</>
                        )}
                    </button>
                </div>

                {/* Run result feedback */}
                {runResult && (
                    <div
                        style={{
                            padding: "10px 16px",
                            marginBottom: "1.5rem",
                            borderRadius: "10px",
                            fontSize: "0.82rem",
                            fontWeight: 500,
                            background:
                                runResult.status === "ok"
                                    ? "rgba(16, 185, 129, 0.1)"
                                    : "rgba(244, 63, 94, 0.1)",
                            color: runResult.status === "ok" ? "#34d399" : "#f87171",
                            border: `1px solid ${runResult.status === "ok"
                                ? "rgba(16, 185, 129, 0.2)"
                                : "rgba(244, 63, 94, 0.2)"
                                }`,
                            animation: "fadeInUp 0.3s ease",
                        }}
                    >
                        {runResult.message}
                    </div>
                )}

                {/* Tabs */}
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

                {/* Tab Content */}
                {activeTab === 0 && (
                    <div>
                        {reportContent ? (
                            <>
                                {charts.length > 0 && (
                                    <div style={{ marginBottom: "1.5rem" }}>
                                        {charts.map((chart, i) => (
                                            <ImageLightbox
                                                key={i}
                                                src={chart}
                                                alt={`${asset.name} chart ${i + 1}`}
                                                style={{ marginBottom: "1rem" }}
                                            />
                                        ))}
                                    </div>
                                )}
                                <MarkdownRenderer content={reportContent} />
                            </>
                        ) : (
                            <div className="empty">
                                <div className="empty__icon">—</div>
                                <div className="empty__text">
                                    No report available. Click <strong>▶ Run Analysis</strong> above
                                    or run <code>python run_all.py</code> to generate reports.
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
                                <div className="empty__icon">—</div>
                                <div className="empty__text">
                                    No methodology documentation (README.md) found for this asset.
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 2 && (
                    <div>
                        {history.length > 0 ? (
                            <div
                                style={{
                                    background: "var(--color-bg-card)",
                                    border: "1px solid var(--color-border)",
                                    borderRadius: "16px",
                                    padding: "1.5rem",
                                }}
                            >
                                <h3
                                    style={{
                                        fontSize: "0.9rem",
                                        fontWeight: 600,
                                        marginBottom: "1rem",
                                        color: "var(--color-text-secondary)",
                                    }}
                                >
                                    Signal History
                                </h3>
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
                                                <td style={{ fontVariantNumeric: "tabular-nums" }}>
                                                    {h.date}
                                                </td>
                                                <td>
                                                    <span
                                                        style={{
                                                            color: getSignalColor(h.signal),
                                                            fontWeight: 600,
                                                        }}
                                                    >
                                                        {h.signal.replace(/[<>]/g, "").trim()}
                                                    </span>
                                                </td>
                                                <td>
                                                    <strong>
                                                        {h.score >= 0 ? "+" : ""}
                                                        {h.score}
                                                    </strong>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="empty">
                                <div className="empty__icon">—</div>
                                <div className="empty__text">
                                    No historical data yet. Run daily to build up trend data.
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Spinner keyframe (injected once) */}
            <style jsx global>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
        </>
    );
}
