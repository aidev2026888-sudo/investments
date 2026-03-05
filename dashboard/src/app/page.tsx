import Link from "next/link";
import {
  ASSET_CONFIGS,
  CATEGORIES,
  getSignalColor,
  getSignalBgColor,
} from "@/lib/types";
import { getReportDates, loadSummary } from "@/lib/data";

export const dynamic = "force-dynamic";

/**
 * Bento grid layout sizes per asset — featured assets get larger cards.
 */
const CARD_SIZES: Record<string, "hero" | "wide" | "tall" | "normal"> = {
  sp500: "hero",       // 2×2 — the most important asset
  gold: "wide",        // 2×1 — precious metals hero
  fx: "wide",          // 2×1 — multi-currency
  dax: "tall",         // 1×2
  csi300: "tall",      // 1×2
  cac40: "normal",
  ftse100: "normal",
  smi: "normal",
  silver: "normal",
};

/**
 * Per-asset gradient accents for visual variety
 */
const CARD_GRADIENTS: Record<string, string> = {
  sp500: "linear-gradient(135deg, rgba(99,91,255,0.12), rgba(14,165,233,0.06))",
  dax: "linear-gradient(135deg, rgba(14,165,233,0.10), rgba(99,91,255,0.05))",
  cac40: "linear-gradient(135deg, rgba(169,96,238,0.10), rgba(99,91,255,0.05))",
  ftse100: "linear-gradient(135deg, rgba(14,165,233,0.08), rgba(17,239,165,0.04))",
  smi: "linear-gradient(135deg, rgba(128,233,255,0.08), rgba(99,91,255,0.04))",
  csi300: "linear-gradient(135deg, rgba(244,63,94,0.08), rgba(169,96,238,0.05))",
  gold: "linear-gradient(135deg, rgba(250,204,21,0.10), rgba(245,158,11,0.05))",
  silver: "linear-gradient(135deg, rgba(148,163,184,0.10), rgba(128,233,255,0.05))",
  fx: "linear-gradient(135deg, rgba(17,239,165,0.10), rgba(14,165,233,0.05))",
};

export default function HomePage() {
  const dates = getReportDates();
  const latestDate = dates[0] || null;
  const summary = latestDate ? loadSummary(latestDate) : null;

  // Count signals
  const buyCount = summary
    ? Object.values(summary.assets).filter(
      (a) => a.signal?.toLowerCase().includes("buy")
    ).length
    : 0;
  const sellCount = summary
    ? Object.values(summary.assets).filter(
      (a) => a.signal?.toLowerCase().includes("sell")
    ).length
    : 0;
  const totalAssets = ASSET_CONFIGS.length;

  return (
    <>
      {/* ═══ Stripe-style Nav ═══ */}
      <header className="header">
        <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
          <div className="header__title">
            <span className="header__logo">GM</span>
            Global Markets
          </div>
          <nav className="header__nav">
            <a href="#equity" className="header__link">Equities</a>
            <a href="#precious_metals" className="header__link">Metals</a>
            <a href="#fx" className="header__link">FX</a>
            <a href="#china" className="header__link">China</a>
          </nav>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {latestDate && <div className="header__date">{latestDate}</div>}
          <a href="/asset/sp500" className="header__cta">View Signals →</a>
        </div>
      </header>

      <main className="main">
        {!summary ? (
          <div className="empty">
            <div className="empty__icon">—</div>
            <div className="empty__text">
              No reports yet. Run <code>python run_all.py</code> to generate
              your first daily report.
            </div>
          </div>
        ) : (
          <>
            {/* ═══ Stripe-style Hero ═══ */}
            <section className="hero">
              <div className="hero__badge">Investment Intelligence Platform</div>
              <h1 className="hero__title">
                Global market<br />
                valuation signals
              </h1>
              <p className="hero__sub">
                Quantitative multi-factor analysis across equities, precious metals,
                and currencies. Automated daily scoring powered by PE percentiles,
                CAPE deviation, equity risk premiums, and macro indicators.
              </p>
              <div className="hero__metrics">
                <div className="hero__metric">
                  <span className="hero__metric-value">{totalAssets}</span>
                  <span className="hero__metric-label">Assets monitored</span>
                </div>
                <div className="hero__metric-divider" />
                <div className="hero__metric">
                  <span className="hero__metric-value" style={{ color: "#11efa5" }}>{buyCount}</span>
                  <span className="hero__metric-label">Buy signals</span>
                </div>
                <div className="hero__metric-divider" />
                <div className="hero__metric">
                  <span className="hero__metric-value" style={{ color: "#f43f5e" }}>{sellCount}</span>
                  <span className="hero__metric-label">Sell signals</span>
                </div>
                <div className="hero__metric-divider" />
                <div className="hero__metric">
                  <span className="hero__metric-value">5</span>
                  <span className="hero__metric-label">Dimensions per asset</span>
                </div>
              </div>
            </section>

            {CATEGORIES.map((cat) => {
              const assets = ASSET_CONFIGS.filter(
                (a) => a.category === cat.key
              );
              if (assets.length === 0) return null;

              return (
                <section key={cat.key} id={cat.key} className="category">
                  <h2 className="category__title">{cat.label}</h2>
                  <div className="bento-grid">
                    {assets.map((asset) => {
                      const data = summary.assets[asset.reportDir];
                      const signal = data?.signal || "N/A";
                      const score = data?.score || 0;
                      const status = data?.status || "failed";
                      const size = CARD_SIZES[asset.slug] || "normal";
                      const gradient = CARD_GRADIENTS[asset.slug] || "";

                      return (
                        <Link
                          key={asset.slug}
                          href={`/asset/${asset.slug}`}
                          className={`bento-card bento-card--${size}`}
                          style={{
                            textDecoration: "none",
                            color: "inherit",
                          }}
                        >
                          {/* Per-card gradient overlay */}
                          <div
                            className="bento-card__gradient"
                            style={{ background: gradient }}
                          />

                          <div className="bento-card__content">
                            <div className="bento-card__top">
                              <div className="bento-card__identity">
                                <span className="card__icon">{asset.icon}</span>
                                <div>
                                  <div className="bento-card__name">
                                    {asset.name}
                                  </div>
                                  <div className="bento-card__score">
                                    Score:{" "}
                                    <strong>
                                      {score >= 0 ? "+" : ""}
                                      {score}
                                    </strong>
                                  </div>
                                </div>
                              </div>
                              <span
                                className="card__signal"
                                style={{
                                  color: getSignalColor(signal),
                                  backgroundColor: getSignalBgColor(signal),
                                }}
                              >
                                {signal.replace(/[<>]/g, "").trim()}
                              </span>
                            </div>

                            {/* Chart — show larger in hero/wide/tall cards */}
                            {data?.charts && data.charts.length > 0 && (
                              <div className="bento-card__chart-wrap">
                                <img
                                  className="bento-card__chart"
                                  src={`/api/chart/${latestDate}/${asset.reportDir}/${data.charts[0]}`}
                                  alt={`${asset.name} chart`}
                                  loading="lazy"
                                />
                              </div>
                            )}
                          </div>

                          <div className="bento-card__footer">
                            <span>
                              <span
                                className="card__status-dot"
                                style={{
                                  backgroundColor:
                                    status === "ok" ? "#11efa5" : "#f43f5e",
                                }}
                              />
                              {status === "ok" ? "Live" : "No data"}
                            </span>
                            <span className="bento-card__arrow">→</span>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </>
        )}
      </main>
    </>
  );
}
