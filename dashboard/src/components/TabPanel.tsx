"use client";

import { useState } from "react";

interface TabPanelProps {
    tabs: { label: string; content: React.ReactNode }[];
}

export default function TabPanel({ tabs }: TabPanelProps) {
    const [active, setActive] = useState(0);

    return (
        <div>
            <div className="tabs">
                {tabs.map((tab, i) => (
                    <button
                        key={i}
                        className={`tab ${i === active ? "tab--active" : ""}`}
                        onClick={() => setActive(i)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            <div>{tabs[active]?.content}</div>
        </div>
    );
}
