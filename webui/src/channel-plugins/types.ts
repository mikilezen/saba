import type { ComponentType } from "react";

import type { ChannelPresentation } from "@/channel-plugins/catalog";
import type {
  SabaFeatureInfo,
  SabaFeaturesPayload,
} from "@/lib/types";

export type ChannelFeatureActionOptions = {
  confirmed?: boolean;
  installOnly?: boolean;
};

export type ChannelFeatureAction = (
  action: "enable" | "disable",
  name: string,
  options?: ChannelFeatureActionOptions,
) => void;

export type ChannelPluginPanelProps = {
  connectRequestId?: number;
  token: string;
  feature: SabaFeatureInfo;
  actionKey: string | null;
  showBrandLogos: boolean;
  onAction: ChannelFeatureAction;
  onFeaturesUpdate: (payload: SabaFeaturesPayload) => void;
  onConfigureMcp?: (name: string) => void;
  onBeforeCloseChange?: (handler: (() => Promise<boolean>) | null) => void;
};

export type ChannelPluginConnectFlowProps = {
  token: string;
  feature: SabaFeatureInfo;
  idleLabel?: string;
  connectRequestId?: number;
  onOpenAdvanced?: () => void;
  onFeaturesUpdate: (payload: SabaFeaturesPayload) => void;
};

export type ChannelPluginHelpProps = {
  feature: SabaFeatureInfo;
};

export type ChannelUiContribution = {
  presentation: ChannelPresentation;
  aliases?: Record<string, Partial<ChannelPresentation>>;
  Panel?: ComponentType<ChannelPluginPanelProps>;
  HelpContent?: ComponentType<ChannelPluginHelpProps>;
  ConnectFlow?: ComponentType<ChannelPluginConnectFlowProps>;
  canConnectBeforeConfigured?: boolean;
};

export type RegisteredChannelUiContribution = {
  channel: string;
  webui: string;
  contribution: ChannelUiContribution;
};
