import React from "react";
import { 
  Building2, 
  Map, 
  Euro, 
  PoundSterling, 
  Landmark,
  Coins,
  Gem,
  LineChart,
  Globe2 
} from "lucide-react";

export function AssetIcon({ slug, className = "" }: { slug: string; className?: string }) {
    const props = { 
        className, 
        strokeWidth: 1.5,
        size: 24,
        style: { filter: "drop-shadow(0px 2px 8px rgba(255,255,255,0.2))" }
    };

    switch (slug) {
        case "sp500":
            return <Building2 {...props} />;
        case "dax":
            return <Euro {...props} />;
        case "cac40":
            return <Map {...props} />;
        case "ftse100":
            return <PoundSterling {...props} />;
        case "smi":
            return <Landmark {...props} />;
        case "csi300":
            return <LineChart {...props} />;
        case "gold":
            return <Coins {...props} color="#FFD700" style={{ filter: "drop-shadow(0px 2px 10px rgba(255,215,0,0.4))" }}/>;
        case "silver":
            return <Gem {...props} color="#E5E4E2" style={{ filter: "drop-shadow(0px 2px 10px rgba(229,228,226,0.4))" }}/>;
        case "fx":
            return <Globe2 {...props} color="#2997FF" style={{ filter: "drop-shadow(0px 2px 10px rgba(41,151,255,0.4))" }}/>;
        default:
            return <LineChart {...props} />;
    }
}
