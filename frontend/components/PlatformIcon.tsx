import { Instagram, Music2, Twitter } from "lucide-react";
import type { Platform } from "@/lib/api";

export function PlatformIcon({ platform, size = 18 }: { platform: Platform; size?: number }) {
  if (platform === "instagram") return <Instagram size={size} />;
  if (platform === "tiktok") return <Music2 size={size} />;
  return <Twitter size={size} />;
}

