import type { ReactNode } from "react";

import {
  configureChannel,
  disableSabaFeature,
  enableSabaFeature,
} from "@/lib/api";
import type { SabaChannelInstanceInfo, SabaFeatureInfo, SabaFeaturesPayload } from "@/lib/types";
import { useClient } from "@/providers/ClientProvider";
import {
  ChannelInstancesPanelView,
  type ChannelInstancesPanelCustomization,
  type ChannelInstancesPanelViewProps,
} from "./ChannelInstancesPanelView";

export type { ChannelInstancesPanelCustomization } from "./ChannelInstancesPanelView";

export function ChannelInstancesPanel({
  feature,
  showBrandLogos,
  instances,
  onFeaturesUpdate,
  customization,
  renderView,
}: {
  feature: SabaFeatureInfo;
  showBrandLogos: boolean;
  instances?: SabaChannelInstanceInfo[];
  onFeaturesUpdate: (payload: SabaFeaturesPayload) => void;
  customization?: ChannelInstancesPanelCustomization;
  renderView?: (props: ChannelInstancesPanelViewProps) => ReactNode;
}) {
  const { client } = useClient();
  const viewProps: ChannelInstancesPanelViewProps = {
    feature,
    showBrandLogos,
    instances,
    customization,
    onToggleInstance: async (instance, checked) => {
      const payload = checked
        ? await enableSabaFeature(client, feature.name, { instanceId: instance.id })
        : await disableSabaFeature(client, feature.name, { instanceId: instance.id });
      onFeaturesUpdate(payload);
    },
    onSaveInstance: async (instance, values) => {
      const payload = await configureChannel(client, feature.name, values, {
        enable: instance.enabled,
        instanceId: instance.id,
      });
      if (payload.saba_features) onFeaturesUpdate(payload.saba_features);
    },
  };
  return renderView ? renderView(viewProps) : <ChannelInstancesPanelView {...viewProps} />;
}
