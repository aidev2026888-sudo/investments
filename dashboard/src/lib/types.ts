// Asset type definitions for the investment dashboard

export interface AssetSummary {
    signal: string;
    score: number;
    status: "ok" | "failed" | "no_report";
    report_file?: string;
    charts?: string[];
    // Optional metrics per asset type
    pe?: number;
    gsr?: number;
    premium_pct?: number;
    reer_z?: number;
}

export interface DailySummary {
    date: string;
    assets: Record<string, AssetSummary>;
}

export interface AssetConfig {
    slug: string;
    name: string;
    shortName: string;
    category: "equity" | "china" | "precious_metals" | "fx";
    icon: string;
    reportDir: string; // Directory name in reports/{date}/
    readmeDir: string; // Directory containing README.md
}

export const ASSET_CONFIGS: AssetConfig[] = [
    // Global Equity Indices
    {
        slug: "sp500",
        name: "S&P 500",
        shortName: "SP500",
        category: "equity",
        icon: "US",
        reportDir: "SP500",
        readmeDir: "global_markets/SP500",
    },
    {
        slug: "dax",
        name: "DAX (Germany)",
        shortName: "DAX",
        category: "equity",
        icon: "DE",
        reportDir: "DAX",
        readmeDir: "global_markets/DAX",
    },
    {
        slug: "cac40",
        name: "CAC 40 (France)",
        shortName: "CAC40",
        category: "equity",
        icon: "FR",
        reportDir: "CAC40",
        readmeDir: "global_markets/CAC40",
    },
    {
        slug: "ftse100",
        name: "FTSE 100 (UK)",
        shortName: "FTSE100",
        category: "equity",
        icon: "GB",
        reportDir: "FTSE100",
        readmeDir: "global_markets/FTSE100",
    },
    {
        slug: "smi",
        name: "SMI (Switzerland)",
        shortName: "SMI",
        category: "equity",
        icon: "CH",
        reportDir: "SMI",
        readmeDir: "global_markets/SMI",
    },
    // China A-Shares
    {
        slug: "csi300",
        name: "CSI 300 (沪深300)",
        shortName: "CSI300",
        category: "china",
        icon: "CN",
        reportDir: "CIS300",
        readmeDir: "CIS300",
    },
    // Precious Metals
    {
        slug: "gold",
        name: "Gold",
        shortName: "Gold",
        category: "precious_metals",
        icon: "Au",
        reportDir: "PreciousMetals",
        readmeDir: "global_markets/PreciousMetals",
    },
    {
        slug: "silver",
        name: "Silver",
        shortName: "Silver",
        category: "precious_metals",
        icon: "Ag",
        reportDir: "PreciousMetals",
        readmeDir: "global_markets/PreciousMetals",
    },
    // FX
    {
        slug: "fx",
        name: "FX (9 Currencies)",
        shortName: "FX",
        category: "fx",
        icon: "FX",
        reportDir: "FX",
        readmeDir: "global_markets/FX",
    },
];

export const CATEGORIES: { key: string; label: string }[] = [
    { key: "equity", label: "Global Equity Indices" },
    { key: "china", label: "China A-Shares" },
    { key: "precious_metals", label: "Precious Metals" },
    { key: "fx", label: "Currencies" },
];

export function getSignalColor(signal: string): string {
    const s = signal.toUpperCase();
    if (s.includes("STRONG BUY") || s.includes("强烈买入")) return "#34d399";
    if (s.includes("BUY") || s.includes("买入")) return "#6ee7b7";
    if (s.includes("STRONG SELL") || s.includes("强烈卖出")) return "#f87171";
    if (s.includes("SELL") || s.includes("卖出")) return "#fca5a5";
    return "#94a3b8";
}

export function getSignalBgColor(signal: string): string {
    const s = signal.toUpperCase();
    if (s.includes("STRONG BUY") || s.includes("强烈买入")) return "rgba(52, 211, 153, 0.12)";
    if (s.includes("BUY") || s.includes("买入")) return "rgba(110, 231, 183, 0.10)";
    if (s.includes("STRONG SELL") || s.includes("强烈卖出")) return "rgba(248, 113, 113, 0.12)";
    if (s.includes("SELL") || s.includes("卖出")) return "rgba(252, 165, 165, 0.10)";
    return "rgba(148, 163, 184, 0.10)";
}
