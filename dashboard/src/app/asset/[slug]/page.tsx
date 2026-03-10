import { notFound } from "next/navigation";
import { ASSET_CONFIGS } from "@/lib/types";
import {
    getReportDates,
    loadSummary,
    loadReport,
    loadReadme,
    getChartPaths,
    getSignalHistory,
} from "@/lib/data";
import AssetDetailClient from "@/components/AssetDetailClient";

export const dynamic = "force-dynamic";

interface PageProps {
    params: Promise<{ slug: string }>;
}

export default async function AssetDetailPage({ params }: PageProps) {
    const { slug } = await params;
    const asset = ASSET_CONFIGS.find((a) => a.slug === slug);
    if (!asset) notFound();

    const dates = getReportDates();
    const latestDate = dates[0] || null;
    const summary = latestDate ? loadSummary(latestDate) : null;
    const assetData = summary?.assets?.[asset.reportDir];

    // Load serializable data only
    // OVERRIDE: Since 'summary.json' only maps a single report_file ("Gold_report...") 
    // for the entire 'PreciousMetals' block, we must explicitly intercept the "silver" slug.
    let reportFilename = assetData?.report_file;
    if (slug === "silver") {
        reportFilename = "Silver_report";
    } else if (slug === "gold") {
        reportFilename = "Gold_report";
    }

    const reportContent = latestDate
        ? loadReport(latestDate, asset.reportDir, reportFilename || asset.shortName)
        : null;
    const readmeContent = loadReadme(asset.readmeDir);
    let charts = latestDate ? getChartPaths(latestDate, asset.reportDir) : [];
    
    // OVERRIDE: Filter charts for precious metals since they share a directory
    if (slug === "silver") {
        charts = charts.filter(c => c.toLowerCase().includes("silver"));
    } else if (slug === "gold") {
        charts = charts.filter(c => c.toLowerCase().includes("gold"));
    }

    const history = getSignalHistory(asset.reportDir);

    return (
        <AssetDetailClient
            asset={{ slug: asset.slug, name: asset.name, icon: asset.icon, reportDir: asset.reportDir }}
            signal={assetData?.signal || "N/A"}
            score={assetData?.score || 0}
            latestDate={latestDate}
            reportContent={reportContent}
            readmeContent={readmeContent}
            charts={charts}
            history={history}
        />
    );
}
