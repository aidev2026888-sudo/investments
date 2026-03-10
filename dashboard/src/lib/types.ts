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
    group: "equity" | "china" | "precious_metals" | "fx";
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
        group: "equity",
        icon: "US",
        reportDir: "SP500",
        readmeDir: "global_markets/SP500",
    },
    {
        slug: "dax",
        name: "DAX (Germany)",
        shortName: "DAX",
        group: "equity",
        icon: "DE",
        reportDir: "DAX",
        readmeDir: "global_markets/DAX",
    },
    {
        slug: "cac40",
        name: "CAC 40 (France)",
        shortName: "CAC40",
        group: "equity",
        icon: "FR",
        reportDir: "CAC40",
        readmeDir: "global_markets/CAC40",
    },
    {
        slug: "ftse100",
        name: "FTSE 100 (UK)",
        shortName: "FTSE100",
        group: "equity",
        icon: "GB",
        reportDir: "FTSE100",
        readmeDir: "global_markets/FTSE100",
    },
    {
        slug: "smi",
        name: "SMI (Switzerland)",
        shortName: "SMI",
        group: "equity",
        icon: "CH",
        reportDir: "SMI",
        readmeDir: "global_markets/SMI",
    },
    // China A-Shares
    {
        slug: "csi300",
        name: "CSI 300 (沪深300)",
        shortName: "CSI300",
        group: "china",
        icon: "CN",
        reportDir: "CIS300",
        readmeDir: "CIS300",
    },
    // Precious Metals
    {
        slug: "gold",
        name: "Gold",
        shortName: "Gold",
        group: "precious_metals",
        icon: "Au",
        reportDir: "PreciousMetals",
        readmeDir: "global_markets/PreciousMetals",
    },
    {
        slug: "silver",
        name: "Silver",
        shortName: "Silver",
        group: "precious_metals",
        icon: "Ag",
        reportDir: "PreciousMetals",
        readmeDir: "global_markets/PreciousMetals",
    },
    // FX
    {
        slug: "fx",
        name: "FX (9 Currencies)",
        shortName: "FX",
        group: "fx",
        icon: "FX",
        reportDir: "FX",
        readmeDir: "global_markets/FX",
    },
];

export const ASSET_GROUPS: { key: string; label: string }[] = [
    { key: "equity", label: "Global Equity Indices" },
    { key: "china", label: "China A-Shares" },
    { key: "precious_metals", label: "Precious Metals" },
    { key: "fx", label: "Currencies" },
];

/**
 * Helper: get color for a signal string (matches CSS variables)
 */
export function getSignalColor(signal: string): string {
    const s = signal.toLowerCase();
    if (s.includes("buy") || s.includes("买入")) return "var(--accent-green)";
    if (s.includes("sell") || s.includes("卖出")) return "var(--accent-red)";
    if (s.includes("neutral") || s.includes("中性") || s.includes("持有")) return "var(--accent-orange)";
    return "var(--text-4)";
}

/**
 * Helper: get background color for a signal string
 */
export function getSignalBgColor(signal: string): string {
    const s = signal.toLowerCase();
    if (s.includes("buy") || s.includes("买入")) return "rgba(48, 209, 88, 0.15)";
    if (s.includes("sell") || s.includes("卖出")) return "rgba(255, 69, 58, 0.15)";
    if (s.includes("neutral") || s.includes("中性") || s.includes("持有")) return "rgba(255, 159, 10, 0.15)";
    return "rgba(255, 255, 255, 0.08)";
}
