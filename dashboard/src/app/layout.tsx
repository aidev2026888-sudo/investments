import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Global Markets Monitor",
  description:
    "Investment valuation dashboard — daily monitoring of equity indices, precious metals, FX, and China A-shares",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="theme-color" content="#000000" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
