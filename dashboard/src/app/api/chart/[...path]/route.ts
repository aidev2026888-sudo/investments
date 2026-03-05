import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

/**
 * API route to serve chart PNG images from reports directory.
 * URL: /api/chart/{date}/{asset}/{filename}.png
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ path: string[] }> }
) {
    const { path: segments } = await params;

    if (!segments || segments.length < 3) {
        return new NextResponse("Not Found", { status: 404 });
    }

    const [date, asset, ...filenameParts] = segments;
    const filename = filenameParts.join("/");

    // Validate inputs to prevent directory traversal
    if (
        date.includes("..") ||
        asset.includes("..") ||
        filename.includes("..")
    ) {
        return new NextResponse("Forbidden", { status: 403 });
    }

    const filePath = path.join(
        process.cwd(),
        "..",
        "reports",
        date,
        asset,
        filename
    );

    if (!fs.existsSync(filePath)) {
        return new NextResponse("Not Found", { status: 404 });
    }

    const fileBuffer = fs.readFileSync(filePath);
    return new NextResponse(fileBuffer, {
        headers: {
            "Content-Type": "image/png",
            "Cache-Control": "public, max-age=86400",
        },
    });
}
