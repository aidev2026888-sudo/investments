import Link from "next/link";
import { ASSET_GROUPS, ASSET_CONFIGS } from "@/lib/types";
import { getReportDates, loadSummary } from "@/lib/data";
import ScrollAnimations from "@/components/ScrollAnimations";
import { AssetIcon } from "@/components/AssetIcon";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
    const dates = getReportDates();
    const latestDate = dates[0] || null;
    let summary = null;
    if (latestDate) {
        summary = loadSummary(latestDate);
    }

    const { assets = {} } = summary || {};
    const totalAssets = ASSET_CONFIGS.length;

    // Calculate aggregated metrics
    let buyCount = 0;
    let sellCount = 0;
    let neutralCount = 0;

    for (const config of ASSET_CONFIGS) {
        const val = assets[config.reportDir]?.signal?.toLowerCase() || "";
        if (val.includes("buy") || val.includes("买入")) buyCount++;
        else if (val.includes("sell") || val.includes("卖出")) sellCount++;
        else neutralCount++;
    }

    return (
        <>
            <ScrollAnimations />
            
            <nav className="nav">
                <div className="nav__brand">
                    <div className="nav__logo">GM</div>
                    <span>Global Markets Monitor</span>
                </div>
                <div className="nav__links">
                    {ASSET_GROUPS.map(g => (
                        <a key={g.key} href={`#${g.key}`} className="nav__link">{g.label}</a>
                    ))}
                    {latestDate && <span className="nav__date" style={{ marginLeft: 16 }}>{latestDate}</span>}
                </div>
            </nav>

            <main className="main">
                {/* ---------- Hero Section (Cinematic Sticky) ---------- */}
                <section className="hero" style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                    <div className="hero__overline">Quantitative Analysis</div>
                    <h1 className="hero__title">Global Markets</h1>
                    <p className="hero__subtitle">
                        Multi-factor valuation signals powered by Python and data APIs.
                        Monitoring global equities, precious metals, and foreign exchange daily.
                    </p>

                    <div className="hero__metrics">
                        <div className="hero__pill">
                            <span>Assets Tracked</span>
                            <span className="hero__pill-value">{totalAssets}</span>
                        </div>
                        <div className="hero__pill">
                            <span style={{ color: "var(--accent-green)" }}>Buy Signals</span>
                            <span className="hero__pill-value">{buyCount}</span>
                        </div>
                        <div className="hero__pill">
                            <span style={{ color: "var(--accent-orange)" }}>Neutral</span>
                            <span className="hero__pill-value">{neutralCount}</span>
                        </div>
                        <div className="hero__pill">
                            <span style={{ color: "var(--accent-red)" }}>Sell Signals</span>
                            <span className="hero__pill-value">{sellCount}</span>
                        </div>
                    </div>
                </section>

                {/* ---------- Overview Section (Stacks over Hero) ---------- */}
                <div style={{ position: 'relative', zIndex: 10, background: 'rgba(0,0,0,0.2)', backdropFilter: 'blur(10px)', WebkitBackdropFilter: 'blur(10px)' }}>
                    
                    {ASSET_GROUPS.map((group) => {
                        const groupAssets = ASSET_CONFIGS.filter((a) => a.group === group.key);
                        if (groupAssets.length === 0) return null;

                        return (
                            <section id={group.key} key={group.key} className="section">
                                <div className="section__label">{group.label}</div>
                                <h2 className="section__title">
                                    {group.key === "equity" ? "Global Equities" :
                                     group.key === "china"  ? "China A-Shares" :
                                     group.key === "metals" ? "Precious Metals" :
                                     "Foreign Exchange"}
                                </h2>
                                <p className="section__subtitle reveal">
                                    {group.key === "equity" ? "Valuation percentiles and CAPE ratios across major global indices." :
                                     group.key === "china"  ? "Earnings yield, bond yield correlations, and ERP metrics." :
                                     group.key === "metals" ? "Real interest rates and inflation-adjusted historical pricing models." :
                                     "Purchasing Power Parity (PPP) deviations and carry trade models."}
                                </p>

                                <div className="asset-grid">
                                    {groupAssets.map((asset, index) => {
                                        const assetData = assets[asset.reportDir];
                                        const signal = assetData?.signal || "N/A";
                                        const score = assetData?.score || 0;
                                        
                                        // Determine sizing strategy based on group position
                                        // First item in big groups gets hero sizing
                                        let sizeClass = "";
                                        if (groupAssets.length >= 3 && index === 0) {
                                            sizeClass = "asset-card--hero";
                                        } else if (groupAssets.length === 2) {
                                            sizeClass = "asset-card--wide";
                                        }

                                        // Use the first chart specified in summary.json for this asset, fallback if missing
                                        const latestChart = assetData?.charts?.[0];
                                        const fallbackChart = `/api/chart/${latestDate || 'fallback'}/${asset.reportDir}/valuation_summary.png`;
                                        const chartUrl = (latestDate && latestChart) 
                                            ? `/api/chart/${latestDate}/${asset.reportDir}/${latestChart}` 
                                            : fallbackChart;
                                        // Helper functions inside map closure (or we can use the imported ones directly on detail page instead for consistency, but here we just need inline styling for the signal)
                                        const getBadgeStyle = (s: string) => {
                                            const sl = s.toLowerCase();
                                            if (sl.includes("buy") || sl.includes("买入")) return { color: "var(--accent-green)", background: "rgba(48, 209, 88, 0.15)" };
                                            if (sl.includes("sell") || sl.includes("卖出")) return { color: "var(--accent-red)", background: "rgba(255, 69, 58, 0.15)" };
                                            if (sl.includes("neutral") || sl.includes("中性") || sl.includes("持有")) return { color: "var(--accent-orange)", background: "rgba(255, 159, 10, 0.15)" };
                                            return { color: "var(--text-4)", background: "rgba(255, 255, 255, 0.08)" };
                                        };

                                        return (
                                            <Link 
                                                key={asset.slug} 
                                                href={`/asset/${asset.slug}`}
                                                className={`asset-card ${sizeClass}`}
                                            >
                                                {/* Ambient glow for hover effect */}
                                                <div 
                                                    className="asset-card__glow" 
                                                    style={{
                                                        background: `radial-gradient(120% 120% at 50% 0%, ${getBadgeStyle(signal).background.replace("0.15", "0.08")}, transparent)`
                                                    }}
                                                />
                                                
                                                <div className="asset-card__body">
                                                    <div className="asset-card__header">
                                                        <div className="asset-card__identity">
                                                            <div className="asset-card__icon">
                                                                <AssetIcon slug={asset.slug} />
                                                            </div>
                                                            <div>
                                                                <h3 className="asset-card__name">{asset.name}</h3>
                                                                <div className="asset-card__score">Score: <strong>{score >= 0 ? '+' : ''}{score}</strong></div>
                                                            </div>
                                                        </div>
                                                        <div className="signal-badge" style={getBadgeStyle(signal)}>
                                                            {signal.replace(/[<>]/g, "").trim()}
                                                        </div>
                                                    </div>

                                                    <div className="asset-card__chart-wrap">
                                                        {latestDate && (
                                                            // eslint-disable-next-line @next/next/no-img-element
                                                            <img 
                                                                src={chartUrl}
                                                                alt={`${asset.name} Chart`}
                                                                className="asset-card__chart"
                                                            />
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="asset-card__footer">
                                                    <div>
                                                        <span className="status-dot" style={{ backgroundColor: getBadgeStyle(signal).color }} />
                                                        {latestDate ? "Updated" : "Awaiting Data"}
                                                    </div>
                                                    <div className="asset-card__arrow">View Details →</div>
                                                </div>
                                            </Link>
                                        );
                                    })}
                                </div>
                            </section>
                        );
                    })}

                    <footer className="footer reveal">
                        <p>© {new Date().getFullYear()} Global Markets Monitor. Generated by <a href="https://akshare.akfamily.xyz/" target="_blank" rel="noopener noreferrer">AKShare</a> data.</p>
                    </footer>
                </div>
            </main>
        </>
    );
}
