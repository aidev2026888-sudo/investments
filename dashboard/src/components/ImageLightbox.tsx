"use client";

import { useState, useEffect, useCallback } from "react";

interface ImageLightboxProps {
    src: string;
    alt: string;
    style?: React.CSSProperties;
}

/**
 * Stripe-inspired image component that expands into a full-screen
 * lightbox overlay when clicked. Smooth zoom + fade animation.
 */
export default function ImageLightbox({ src, alt, style }: ImageLightboxProps) {
    const [open, setOpen] = useState(false);

    const handleClose = useCallback(() => setOpen(false), []);

    useEffect(() => {
        if (!open) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") handleClose();
        };
        document.addEventListener("keydown", onKey);
        return () => document.removeEventListener("keydown", onKey);
    }, [open, handleClose]);

    return (
        <>
            {/* Thumbnail with expand hint */}
            <div
                onClick={() => setOpen(true)}
                style={{
                    position: "relative",
                    cursor: "zoom-in",
                    ...style,
                }}
            >
                <img
                    src={src}
                    alt={alt}
                    style={{
                        width: "100%",
                        borderRadius: "12px",
                        transition: "transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease",
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.transform = "scale(1.01)";
                        e.currentTarget.style.boxShadow = "0 8px 32px rgba(0,0,0,0.4)";
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.transform = "scale(1)";
                        e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.3)";
                    }}
                />
                {/* Expand icon (Stripe bento-card style) */}
                <div
                    style={{
                        position: "absolute",
                        top: 12,
                        right: 12,
                        width: 32,
                        height: 32,
                        borderRadius: 8,
                        background: "rgba(0, 0, 0, 0.5)",
                        backdropFilter: "blur(8px)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        opacity: 0.6,
                        transition: "opacity 0.2s ease, transform 0.2s ease",
                        color: "white",
                        fontSize: "14px",
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.opacity = "1";
                        e.currentTarget.style.transform = "scale(1.1)";
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.opacity = "0.6";
                        e.currentTarget.style.transform = "scale(1)";
                    }}
                >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <path d="M1 5V1h4M9 1h4v4M13 9v4H9M5 13H1V9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </div>
            </div>

            {/* Lightbox overlay */}
            {open && (
                <div
                    onClick={handleClose}
                    style={{
                        position: "fixed",
                        inset: 0,
                        zIndex: 9999,
                        background: "rgba(0, 0, 0, 0.88)",
                        backdropFilter: "blur(20px)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        cursor: "zoom-out",
                        animation: "lightboxFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
                        padding: "2rem",
                    }}
                >
                    <img
                        src={src}
                        alt={alt}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            maxWidth: "95vw",
                            maxHeight: "92vh",
                            borderRadius: "12px",
                            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
                            animation: "lightboxZoomIn 0.35s cubic-bezier(0.16, 1, 0.3, 1)",
                            cursor: "default",
                        }}
                    />
                    {/* Close button */}
                    <button
                        onClick={handleClose}
                        style={{
                            position: "absolute",
                            top: 20,
                            right: 24,
                            width: 40,
                            height: 40,
                            borderRadius: 10,
                            border: "1px solid rgba(255,255,255,0.15)",
                            background: "rgba(255,255,255,0.08)",
                            color: "white",
                            fontSize: "18px",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            transition: "all 0.2s ease",
                            fontFamily: "inherit",
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = "rgba(255,255,255,0.15)";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = "rgba(255,255,255,0.08)";
                        }}
                    >
                        ✕
                    </button>
                </div>
            )}

            <style jsx global>{`
        @keyframes lightboxFadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes lightboxZoomIn {
          from { opacity: 0; transform: scale(0.92); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
        </>
    );
}
