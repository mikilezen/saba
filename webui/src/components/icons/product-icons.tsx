import { forwardRef, type ReactNode } from "react";
import type { LucideIcon, LucideProps } from "lucide-react";

function productIcon(name: string, drawing: ReactNode): LucideIcon {
  const Icon = forwardRef<SVGSVGElement, LucideProps>(({ size = 24, color = "currentColor", strokeWidth = 1.75, absoluteStrokeWidth, className, children, ...props }, ref) => (
    <svg ref={ref} xmlns="http://www.w3.org/2000/svg" width={size} height={size}
      viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={strokeWidth}
      strokeLinecap="round" strokeLinejoin="round"
      vectorEffect={absoluteStrokeWidth ? "non-scaling-stroke" : undefined}
      aria-hidden="true" className={className} data-product-icon={name} {...props}>
      {drawing}{children}
    </svg>
  ));
  Icon.displayName = name;
  return Icon;
}

export const NewChatIcon = productIcon("new-chat", <><path d="M11 20H7l-4 2V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v4" /><path d="M17 14v7m-3.5-3.5h7" /></>);
export const ComposeIcon = productIcon("compose", <g transform="scale(1.5)" fill="currentColor" stroke="none"><path fillRule="evenodd" clipRule="evenodd" d="M7.25 1C7.66414 1 7.99988 1.33589 8 1.75C8 2.16421 7.66421 2.5 7.25 2.5H4.75C3.50745 2.5 2.50012 3.50744 2.5 4.75V11.25C2.5 12.4926 3.50736 13.5 4.75 13.5H11.25C12.4926 13.5 13.5 12.4926 13.5 11.25V8.75C13.5001 8.33589 13.8359 8 14.25 8C14.6641 8 14.9999 8.33589 15 8.75V11.25C15 13.3211 13.3211 15 11.25 15H4.75C2.67893 15 1 13.3211 1 11.25V4.75C1.00012 2.67905 2.67899 1 4.75 1H7.25Z" /><path fillRule="evenodd" clipRule="evenodd" d="M13.4326 1.26953C13.7913 0.910937 14.3728 0.910883 14.7314 1.26953C15.0897 1.6282 15.0899 2.20981 14.7314 2.56836L9.2373 8.06152C8.68101 8.6177 7.94043 8.95161 7.15527 9C7.06754 9.0052 6.99468 8.93248 7 8.84473C7.04847 8.05961 7.38232 7.31897 7.93848 6.7627L13.4326 1.26953Z" /></g>);
export const ConversationIcon = productIcon("conversation", <><path d="M7 4h10a4 4 0 0 1 4 4v7a4 4 0 0 1-4 4H8l-5 3V8a4 4 0 0 1 4-4Z" /><path d="M7 9h10M7 13h6" /></>);
export const SearchIcon = productIcon("search", <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m15.5 15.5 5 5" /></>);
export const AppsIcon = productIcon("apps", <><rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1.75" /><rect x="14" y="3.5" width="6.5" height="6.5" rx="1.75" /><rect x="3.5" y="14" width="6.5" height="6.5" rx="1.75" /><rect x="14" y="14" width="6.5" height="6.5" rx="1.75" /></>);
export const SkillsIcon = productIcon("skills", <path d="M8 6.5H5.5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V16h1a2.5 2.5 0 0 0 0-5h-1V8.5a2 2 0 0 0-2-2H13v-1a2.5 2.5 0 0 0-5 0Z" />);
export const AutomationsIcon = productIcon("automations", <><rect x="3.5" y="3.5" width="17" height="17" rx="3" /><path d="M12 7.5V12l3 2" /></>);
export const ChannelsIcon = productIcon("channels", <path d="M6.5 3.5h11a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H9l-4 2v-2.4a3 3 0 0 1-1.5-2.6v-9a3 3 0 0 1 3-3Z" />);
export const ArchiveIcon = productIcon("archive", <><rect x="3" y="3.5" width="18" height="4.5" rx="1.5" /><path d="M4.5 8v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8M9 12h6" /></>);
export const SettingsIcon = productIcon("settings", <><path d="M10 3h4l.6 2.4 2.1 1.2 2.4-.7 2 3.5-1.8 1.7v1.8l1.8 1.7-2 3.5-2.4-.7-2.1 1.2L14 21h-4l-.6-2.4-2.1-1.2-2.4.7-2-3.5 1.8-1.7v-1.8L2.9 9.4l2-3.5 2.4.7 2.1-1.2L10 3Z" /><circle cx="12" cy="12" r="3" /></>);
export const OverviewIcon = productIcon("overview", <><rect x="3" y="3" width="18" height="18" rx="3" /><path d="M3 9h18M9 9v12m4-4v-3m4 3v-5" /><path d="M6 6h.01" /></>);
export const AppearanceIcon = productIcon("appearance", <><path d="M12 3a9 9 0 0 0 0 18h1a2 2 0 0 0 1.3-3.5 1.7 1.7 0 0 1 1.2-3H18a3 3 0 0 0 3-3A9 9 0 0 0 12 3Z" /><circle cx="7.5" cy="10" r=".8" /><circle cx="11" cy="6.8" r=".8" /><circle cx="16" cy="8" r=".8" /></>);
export const ModelsIcon = productIcon("models", <><path d="m12 3 9 5-9 5-9-5 9-5Zm-9 9 9 5 9-5M3 16l9 5 9-5" /></>);
export const CapabilitiesIcon = productIcon("capabilities", <><path d="m12 8 4 4-4 4-4-4 4-4Zm0-5v5m0 8v5M3 12h5m8 0h5" /><path d="M7 3H5a2 2 0 0 0-2 2v2m14-4h2a2 2 0 0 1 2 2v2M3 17v2a2 2 0 0 0 2 2h2m10 0h2a2 2 0 0 0 2-2v-2" /></>);
export const SystemIcon = productIcon("system", <><rect x="3" y="3" width="18" height="7" rx="2" /><rect x="3" y="14" width="18" height="7" rx="2" /><path d="M7 6.5h.01m0 11h.01M12 6.5h5m-5 11h5" /></>);
export const AdvancedIcon = productIcon("advanced", <><path d="M3 6h5m4 0h9M3 12h11m4 0h3M3 18h2m4 0h12" /><circle cx="10" cy="6" r="2" /><circle cx="16" cy="12" r="2" /><circle cx="7" cy="18" r="2" /></>);
export const AboutIcon = productIcon("about", <><circle cx="12" cy="12" r="9" /><path d="M12 11v6m0-10h.01" /></>);
export const AttachIcon = productIcon("attach", <path d="M8.5 12.5 14 7a2.75 2.75 0 0 1 3.89 3.89l-7.43 7.43a4.25 4.25 0 0 1-6.01-6.01l7.43-7.43a5.75 5.75 0 0 1 8.13 8.13L12.5 20.5" />);
export const SendIcon = productIcon("send", <><path d="m4 5 17 7-17 7 3-7-3-7Z" /><path d="M7 12h14" /></>);
export const VoiceIcon = productIcon("voice", <><rect x="9" y="3" width="6" height="12" rx="3" /><path d="M6 11v1a6 6 0 0 0 12 0v-1M12 18v3m-3 0h6" /></>);
export const StopIcon = productIcon("stop", <rect x="5" y="5" width="14" height="14" rx="2.5" />);
export const RestrictedAccessIcon = productIcon("restricted-access", <><rect x="5" y="10" width="14" height="11" rx="2.5" /><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2" /></>);
export const FullAccessIcon = productIcon("full-access", <><rect x="5" y="10" width="14" height="11" rx="2.5" /><path d="M8 10V7a4 4 0 0 1 7.5-2m-3.5 10v2" /></>);
export const WorkspaceIcon = productIcon("workspace", <path d="M3 7a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" />);
export const PromptNavigationIcon = productIcon("prompt-navigation", <><path d="M5 5v14m4-14h11M9 12h11M9 19h7" /><circle cx="5" cy="5" r="1.5" fill="currentColor" stroke="none" /><circle cx="5" cy="12" r="1.5" fill="currentColor" stroke="none" /><circle cx="5" cy="19" r="1.5" fill="currentColor" stroke="none" /></>);
export const TemporaryChatIcon = productIcon("temporary-chat", <><path d="M7 4h10a4 4 0 0 1 4 4v7a4 4 0 0 1-4 4H8l-5 3V8a4 4 0 0 1 4-4Z" strokeDasharray="3 3" /><path d="M8 10h8m-8 4h4" /></>);
export const GoalIcon = productIcon("goal", <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1.25" fill="currentColor" stroke="none" /></>);
export const DelegationIcon = productIcon("delegation", <><rect x="8" y="3" width="8" height="5" rx="1.5" /><rect x="2" y="16" width="8" height="5" rx="1.5" /><rect x="14" y="16" width="8" height="5" rx="1.5" /><path d="M12 8v4M6 16v-4h12v4" /></>);
export const TaskInspectIcon = productIcon("task-inspect", <><rect x="3" y="3" width="13" height="18" rx="2" /><path d="M7 7h5M7 11h3" /><circle cx="16" cy="15" r="4" /><path d="m19 18 3 3" /></>);
export const TaskMessageIcon = productIcon("task-message", <><path d="M12 19H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v4M7 8h10M7 12h4" /><path d="M14 17h7m-3-3 3 3-3 3" /></>);
export const QueuedTaskIcon = productIcon("task-queued", <><circle cx="12" cy="12" r="8.5" /><path d="M12 7v5l3 2" /></>);
export const RunningTaskIcon = productIcon("task-running", <><path d="M12 3a9 9 0 1 1-9 9" /><path d="M3 7v.01M6 4v.01" /></>);
export const StoppingTaskIcon = productIcon("task-stopping", <><path d="M12 3a9 9 0 1 1-9 9M3 7v.01M6 4v.01" /><rect x="9" y="9" width="6" height="6" rx="1" /></>);
export const CompletedTaskIcon = productIcon("task-completed", <><circle cx="12" cy="12" r="9" /><path d="m7.5 12 3 3 6-6" /></>);
export const CancelledTaskIcon = productIcon("task-cancelled", <><circle cx="12" cy="12" r="9" /><path d="m9 9 6 6m0-6-6 6" /></>);
export const IncompleteTaskIcon = productIcon("task-incomplete", <><path d="M12 3a9 9 0 0 1 9 9M12 21a9 9 0 0 1-9-9" /><path d="M3 8v.01M6 5v.01M8 3v.01M21 16v.01M18 19v.01M16 21v.01" /><path d="M12 8v4" /></>);
export const InterruptedTaskIcon = productIcon("task-interrupted", <><circle cx="12" cy="12" r="9" /><path d="M9 8v8m6-8v8" /></>);
export const ErrorTaskIcon = productIcon("task-error", <><circle cx="12" cy="12" r="9" /><path d="M12 7v6m0 4h.01" /></>);
export const ActivityIcon = productIcon("activity", <><circle cx="4" cy="10" r="2" /><circle cx="12" cy="10" r="2" /><circle cx="20" cy="10" r="2" /><path d="M6 10h4m4 0h4M3 17h3m4 0h4m4 0h3" /></>);
export const StatusIcon = productIcon("status", <><path d="M3 15a9 9 0 1 1 18 0M6 20h12m-6-5 4-5" /><circle cx="12" cy="15" r="1.5" /></>);
export const CompactIcon = productIcon("compact", <><path d="M7 10h10M7 14h10M12 2v5m-2-2 2 2 2-2M12 22v-5m-2 2 2-2 2 2" /></>);
export const ResumeIcon = productIcon("resume", <><path d="m9 5 11 7-11 7V5Z" /><path d="M4 6v12" /></>);
export const RestartIcon = productIcon("restart", <><path d="M20 8a8.5 8.5 0 1 0 0 8M20 3v5h-5" /></>);
export const UpdateIcon = productIcon("update", <><path d="M12 15V3m-4 4 4-4 4 4M4 13v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-6" /></>);
export const ImportIcon = productIcon("import", <><path d="M10 4h7l4 4v11a2 2 0 0 1-2 2h-9M17 4v5h4M3 13h11m-4-4 4 4-4 4" /></>);
export const AppActionsIcon = productIcon("app-actions", <><rect x="3" y="3" width="18" height="18" rx="3" /><path d="M3 8h18M7 5.5h.01M8 14h.01M12 14h.01M16 14h.01" /></>);
export const McpIcon = productIcon("mcp", <g transform="scale(1.5)" fill="currentColor" stroke="none"><path fillRule="evenodd" clipRule="evenodd" d="M14.5565 7.87462C14.5385 7.89312 14.5205 7.91112 14.5025 7.92862L8.69849 13.6201C8.62599 13.6906 8.62449 13.8061 8.69499 13.8786C8.69599 13.8801 8.69749 13.8811 8.69849 13.8821L9.89049 15.0516C10.1075 15.2626 10.1125 15.6101 9.90149 15.8276C9.89799 15.8311 9.89449 15.8351 9.89049 15.8386C9.66699 16.0551 9.31199 16.0551 9.08849 15.8386L7.89649 14.6701C7.38949 14.1776 7.37799 13.3671 7.87049 12.8601C7.87899 12.8511 7.88749 12.8426 7.89649 12.8341L13.7005 7.14212C14.352 6.50762 14.3665 5.46512 13.732 4.81362C13.7215 4.80312 13.711 4.79262 13.7005 4.78212L13.667 4.74962C12.998 4.09862 11.9325 4.09762 11.2625 4.74762L6.48099 9.43712L6.47949 9.43862L6.41399 9.50312C6.19049 9.72062 5.83449 9.72062 5.61149 9.50312C5.39449 9.29162 5.38949 8.94462 5.60049 8.72712C5.60399 8.72362 5.60749 8.71962 5.61149 8.71612L10.46 3.96062C11.1105 3.32512 11.123 2.28262 10.4875 1.63212C10.478 1.62262 10.468 1.61262 10.458 1.60262C9.78799 0.950619 8.72099 0.950619 8.05149 1.60262L1.63499 7.89512C1.41149 8.11212 1.05649 8.11212 0.832987 7.89512C0.615987 7.68412 0.610987 7.33662 0.821987 7.11912C0.825487 7.11562 0.828987 7.11162 0.832987 7.10812L7.24999 0.815119C8.36599 -0.271381 10.1445 -0.271381 11.2605 0.815119C11.8905 1.42762 12.189 2.30512 12.063 3.17512C12.9435 3.05012 13.8325 3.34062 14.469 3.96162L14.5025 3.99512C15.5885 5.05162 15.613 6.78812 14.5565 7.87412V7.87462ZM12.8655 6.32212C13.083 6.11062 13.0875 5.76362 12.8765 5.54612C12.8735 5.54262 12.8695 5.53862 12.8655 5.53512C12.642 5.31762 12.286 5.31762 12.063 5.53512L7.31699 10.1896C6.64699 10.8416 5.57999 10.8416 4.91049 10.1896C4.25899 9.55512 4.24449 8.51262 4.87899 7.86112C4.88949 7.85062 4.89999 7.84012 4.91049 7.82962L9.65699 3.17512C9.87399 2.96362 9.87899 2.61662 9.66799 2.39912C9.66449 2.39562 9.66099 2.39162 9.65699 2.38812C9.43349 2.17062 9.07749 2.17062 8.85449 2.38812L4.10849 7.04262C3.02249 8.09912 2.99799 9.83562 4.05449 10.9216C4.07249 10.9401 4.09049 10.9581 4.10849 10.9756C5.22499 12.0616 7.00299 12.0616 8.11899 10.9756L12.8655 6.32112V6.32212Z" /></g>);
export const ToolRunIcon = productIcon("tool-run", <path d="M14 4a6 6 0 0 0-7 7L3.5 18a2 2 0 0 0 2.5 2.5l7-3.5a6 6 0 0 0 7-7l-4 4-5-1-1-5 4-4Z" />);
export const FileReadIcon = productIcon("file-read", <><path d="M13 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10l-7-7Zm0 0v7h7M8 14h8m-8 3h5" /></>);
export const FileListIcon = productIcon("file-list", <><path d="M3 6a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11H3V6Z" /><path d="M7 12h.01M10 12h7M7 16h.01M10 16h5" /></>);
export const MemoryIcon = productIcon("memory", <><rect x="5" y="3" width="15" height="18" rx="2" /><path d="M5 8H3m2 5H3m2 5H3M14 3v8l2-1.5 2 1.5V3M9 15h7m-7 3h4" /></>);
export const DreamIcon = productIcon("dream", <><path d="M14 4A8.5 8.5 0 1 0 20 15a8 8 0 0 1-6-11Z" /><path d="m18 3 1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3Z" /></>);
export const DreamLogIcon = productIcon("dream-log", <><rect x="4" y="3" width="16" height="18" rx="2" /><path d="M8 7h8m-8 5h8m-8 5h5" /></>);
export const RestoreMemoryIcon = productIcon("restore-memory", <><path d="M13 4h5a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-4M4 4v5h5M4 9a6 6 0 1 1 3 5" /></>);
export const PromptTemplateIcon = productIcon("prompt-template", <><rect x="4" y="3" width="16" height="18" rx="2" /><path d="m10 8-3 4 3 4m4-8 3 4-3 4" /></>);
export const TriggerIcon = productIcon("trigger", <path d="m13 2-9 12h7l-1 8 10-13h-7l0-7Z" />);
export const PairingIcon = productIcon("pairing", <><path d="m9 15-2 2a4 4 0 0 1-6-6l4-4a4 4 0 0 1 6 0m4 2 2-2a4 4 0 0 1 6 6l-4 4a4 4 0 0 1-6 0M8 16l8-8" /></>);
export const HelpIcon = productIcon("help", <><circle cx="12" cy="12" r="9" /><path d="M9 8a3 3 0 0 1 6 0c0 2-3 2-3 5m0 4h.01" /></>);
export const HistoryIcon = productIcon("history", <><path d="M4 9a8.5 8.5 0 1 1 0 7M4 4v5h5M12 7v5l3 2" /></>);
export const WebSearchIcon = productIcon("web-search", <><circle cx="10" cy="10" r="7" /><path d="M3 10h14M10 3a12 12 0 0 0 0 14 12 12 0 0 0 0-14" /><circle cx="17" cy="17" r="4" /><path d="m20 20 2 2" /></>);
export const ImageGenerationIcon = productIcon("image-generation", <><path d="M12 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5M4 16l5-5 8 9" /><circle cx="9" cy="8" r="1" /><path d="m18 2 1 4 3 1-3 1-1 4-1-4-3-1 3-1 1-4Z" /></>);
export const EditIcon = productIcon("edit", <><path d="m15 4 5 5M4 15l11-11a2 2 0 0 1 3 0l2 2a2 2 0 0 1 0 3L9 20l-6 1 1-6Z" /></>);
export const ProviderIcon = productIcon("provider", <><path d="M7 3h10l5 9-5 9H7L2 12l5-9Z" /><path d="M8 8h8v8H8V8Z" /></>);
