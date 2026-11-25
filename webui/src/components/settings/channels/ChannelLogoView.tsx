import { useMemo } from "react";

import type { ChannelPresentation } from "@/channel-plugins/catalog";
import { useLogoFallback } from "@/hooks/useLogoFallback";
import { logoFallbackUrls } from "@/lib/provider-brand";
import type { SabaFeatureInfo } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ChannelLogoView({
  feature,
  presentation,
  showBrandLogos,
}: {
  feature: SabaFeatureInfo;
  presentation?: ChannelPresentation;
  showBrandLogos: boolean;
}) {
  const initials = presentation?.initials ?? feature.display_name.slice(0, 2).toUpperCase();
  const Icon = presentation?.icon;
  const logoUrls = useMemo(() => {
    const fallbackUrls = logoFallbackUrls(presentation?.logoFallbackUrl ?? presentation?.logoUrl);
    return presentation?.logoUrl && presentation.logoFallbackUrl
      ? [...new Set([presentation.logoUrl, ...fallbackUrls])]
      : fallbackUrls;
  }, [presentation?.logoUrl, presentation?.logoFallbackUrl]);
  const { logoUrl, logoLoaded, onLogoError, onLogoLoad } = useLogoFallback(logoUrls);
  const showPhoneChannelLogo = ["phone-call", "sms-messages", "ussd"].includes(feature.name);
  const showRemoteLogo = (showBrandLogos || showPhoneChannelLogo) && Boolean(logoUrl);
  const showLoadedLogo = showRemoteLogo && logoLoaded;
  const isLogoTile = presentation?.logoLayout === "tile" && logoUrl === presentation.logoUrl;

  return (
    <span
      data-testid={`channel-logo-${feature.name}`}
      className={cn(
        "relative grid h-8 w-8 shrink-0 place-items-center overflow-hidden rounded-[9px] text-[11px] font-semibold text-muted-foreground",
        showLoadedLogo ? (isLogoTile ? "bg-transparent" : "bg-white") : "bg-muted",
      )}
      aria-hidden
    >
      <span className={cn(
        "transition-opacity duration-150 motion-reduce:transition-none",
        showLoadedLogo ? "opacity-0" : "opacity-100",
      )}>
        {Icon ? <Icon className="h-6 w-6" strokeWidth={2} /> : initials}
      </span>
      {showRemoteLogo ? <img
        src={logoUrl}
        alt=""
        decoding="async"
        loading="lazy"
        referrerPolicy="no-referrer"
        draggable={false}
        className={cn(
          "absolute object-contain transition-opacity duration-150 motion-reduce:transition-none",
          isLogoTile ? "h-8 w-8" : "h-6 w-6",
          logoLoaded ? "opacity-100" : "opacity-0",
        )}
        onLoad={onLogoLoad}
        onError={onLogoError}
      /> : null}
    </span>
  );
}
