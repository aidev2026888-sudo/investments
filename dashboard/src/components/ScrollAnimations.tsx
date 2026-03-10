"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Only register plugin on client side
if (typeof window !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
}

export default function ScrollAnimations() {
    const initialized = useRef(false);

    useEffect(() => {
        if (typeof window === "undefined" || initialized.current) return;
        initialized.current = true;

        // Give Next.js a moment to paint the DOM
        const timer = setTimeout(() => {
            // 1. Reveal Elements
            const elements = document.querySelectorAll('.reveal');
            elements.forEach((el) => {
                ScrollTrigger.create({
                    trigger: el,
                    start: "top 85%",
                    onEnter: () => el.classList.add('active'),
                    once: true,
                });
            });

            // 2. Parallax Effects on Charts
            const charts = document.querySelectorAll('.asset-card__chart');
            charts.forEach((chart) => {
                const wrap = chart.parentElement;
                if (!wrap) return;
                
                // Set initial scale to allow room for parallax down
                gsap.set(chart, { y: -20, scale: 1.1 });

                gsap.to(chart, {
                    y: 20,
                    ease: "none",
                    scrollTrigger: {
                        trigger: wrap,
                        start: "top bottom", // when top of element hits bottom of viewport
                        end: "bottom top",   // when bottom of element hits top of viewport
                        scrub: true,
                    }
                });
            });

            // 3. Staggered reveal for grid items
            const grids = document.querySelectorAll('.asset-grid');
            grids.forEach((grid) => {
                const cards = grid.querySelectorAll('.asset-card');
                if (cards.length === 0) return;

                gsap.fromTo(
                    cards,
                    { 
                        opacity: 0, 
                        y: 40,
                        scale: 0.95
                    },
                    {
                        opacity: 1,
                        y: 0,
                        scale: 1,
                        duration: 0.6,
                        stagger: 0.1,
                        ease: "power2.out",
                        scrollTrigger: {
                            trigger: grid,
                            start: "top 85%",
                            once: true
                        }
                    }
                );
            });

        }, 100);

        return () => {
            clearTimeout(timer);
            ScrollTrigger.getAll().forEach(t => t.kill());
        };
    }, []);

    return null; // This component just mounts the animation logic
}
