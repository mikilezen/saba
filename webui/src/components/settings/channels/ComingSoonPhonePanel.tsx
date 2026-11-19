import { useEffect, useState } from "react";
import { Check, Loader2, Phone } from "lucide-react";

import { ChannelLogo } from "@/components/settings/channels/ChannelIdentity";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ToggleButton } from "@/components/ui/toggle-button";
import type { ChannelPluginPanelProps } from "@/channel-plugins/types";

type PhoneSetup = {
  provider: "ethiotelecom" | "safaricom";
  phoneNumber: string;
  pukCode: string;
  enabled: boolean;
};

export function ComingSoonPhonePanel({
  feature,
  showBrandLogos,
}: ChannelPluginPanelProps) {
  const storageKey = `saba-phone-channel:${feature.name}`;
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [provider, setProvider] = useState<PhoneSetup["provider"]>("ethiotelecom");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [pukCode, setPukCode] = useState("");
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    try {
      const value = window.localStorage.getItem(storageKey);
      if (!value) return;
      const setup = JSON.parse(value) as Partial<PhoneSetup>;
      if (setup.provider === "ethiotelecom" || setup.provider === "safaricom") setProvider(setup.provider);
      setPhoneNumber(setup.phoneNumber ?? "");
      setPukCode(setup.pukCode ?? "");
      setEnabled(setup.enabled === true);
    } catch {
      window.localStorage.removeItem(storageKey);
    }
  }, [storageKey]);

  const save = () => {
    if (!phoneNumber.trim()) return;
    setSaving(true);
    window.localStorage.setItem(storageKey, JSON.stringify({
      provider,
      phoneNumber: phoneNumber.trim(),
      pukCode: pukCode.trim(),
      enabled,
    }));
    window.setTimeout(() => {
      setSaving(false);
      setSaved(true);
      window.setTimeout(() => setSaved(false), 1600);
    }, 300);
  };

  return (
    <aside className="min-h-full rounded-panel bg-settings-surface p-6">
      <div className="flex items-center gap-3 pe-20">
        <ChannelLogo feature={feature} showBrandLogos={showBrandLogos} />
        <h3 className="text-ui-heading">{feature.display_name}</h3>
      </div>
      <div className="mt-5 space-y-5">
        <div className="rounded-control border border-border/60 bg-background px-4 py-3 text-[13px] leading-5 text-muted-foreground">
          <strong className="text-foreground">Coming soon.</strong> Save a setup profile below. Connection activation will be available after the telecom provider integration is installed.
        </div>
        <label className="block space-y-2">
          <span className="text-[13px] font-medium">Telecom provider</span>
          <Select value={provider} onValueChange={(value) => setProvider(value as PhoneSetup["provider"])}>
            <SelectTrigger className="h-10 rounded-full"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="ethiotelecom">Ethio Telecom</SelectItem>
              <SelectItem value="safaricom">Safaricom</SelectItem>
            </SelectContent>
          </Select>
        </label>
        <label className="block space-y-2">
          <span className="text-[13px] font-medium">Phone number</span>
          <Input type="tel" value={phoneNumber} onChange={(event) => setPhoneNumber(event.target.value)} placeholder="+251 9..." />
        </label>
        <label className="block space-y-2">
          <span className="text-[13px] font-medium">PUK code</span>
          <Input type="password" value={pukCode} onChange={(event) => setPukCode(event.target.value)} placeholder="Enter PUK code" />
        </label>
        <div className="flex items-center justify-between gap-3 rounded-control border border-border/60 px-4 py-3">
          <div>
            <p className="text-[13px] font-medium">Enable channel</p>
            <p className="text-[12px] text-muted-foreground">Keep this profile enabled when available.</p>
          </div>
          <ToggleButton
            checked={enabled}
            onChange={setEnabled}
            ariaLabel="Enable channel"
            label={enabled ? "On" : "Off"}
          />
        </div>
        <div className="flex justify-end">
          <Button type="button" className="rounded-full" disabled={!phoneNumber.trim() || saving} onClick={save}>
            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : saved ? <Check className="mr-2 h-4 w-4" /> : <Phone className="mr-2 h-4 w-4" />}
            {saved ? "Saved" : "Save setup"}
          </Button>
        </div>
      </div>
    </aside>
  );
}
