"use client";

import { useState, useEffect, useCallback } from "react";

interface ImageLightboxProps {
    src: string;
    alt: string;
    style?: React.CSSProperties;
}

/**
 * Cinematic Dark Mode Image Lightbox
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
        // Lock body scroll
        document.body.style.overflow = "hidden";
        return () => {
            document.removeEventListener("keydown", onKey);
            document.body.style.overflow = "";
        };
    }, [open, handleClose]);

    return (
        <>
            {/* Cinematic container with glow hover effect */}
            <div
                className="chart-container"
                onClick={() => setOpen(true)}
                style={style}
            >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt={alt} />
                <div className="chart-container__expand">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <path d="M1 5V1h4M9 1h4v4M13 9v4H9M5 13H1V9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </div>
            </div>

            {/* Lightbox full-screen overlay */}
            {open && (
                <div className="lightbox" onClick={handleClose}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        src={src}
                        alt={alt}
                        onClick={(e) => e.stopPropagation()}
                    />
                    <button className="lightbox__close" onClick={handleClose}>✕</button>
                </div>
            )}
        </>
    );
}
