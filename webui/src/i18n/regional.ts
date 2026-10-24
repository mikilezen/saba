import type { SupportedLocale } from "./config";

type TranslationTree = Record<string, unknown>;

export const regionalTranslations: Partial<Record<SupportedLocale, TranslationTree>> = {
  am: {
    app: {
      loading: { connecting: "ሳባን በማገናኘት ላይ…", boot: "ሳባን በመጫን ላይ…" },
      meta: { description: "የሳባ ዌብ UI — ከሳባ የስራ ቦታዎ ጋር ይወያዩ።" },
      error: { title: "ሳባን ማግኘት አልተቻለም", gatewayHint: "ጌትዌዩ እየሰራ መሆኑን እና አሳሹ የWebUI አድራሻውን ማግኘት መቻሉን ያረጋግጡ።" },
      auth: {
        title: "ከሳባ ጋር ይገናኙ", label: "የWebUI ይለፍ ቃል",
        helpTitle: "ይለፍ ቃሉን የት ማግኘት እችላለሁ?", submit: "ይገናኙ",
        required: "ይለፍ ቃል ያስገቡ", invalid: "የተሳሳተ ይለፍ ቃል",
      },
      account: { section: "መለያ", logoutHint: "ይህን አሳሽ ከጌትዌዩ ያላቅቁ።", logout: "ይውጡ" },
      system: { section: "ስርዓት", restartAction: "እንደገና አስነሳ", restart: "ሳባን እንደገና አስነሳ", restarting: "እንደገና በማስነሳት ላይ…" },
    },
    common: { retry: "እንደገና ሞክር", dismiss: "ዝጋ", close: "ዝጋ", current: "የአሁኑ", cancel: "ሰርዝ" },
    sidebar: {
      resize: "የጎን አሞሌን መጠን ቀይር", navigation: "የጎን አሞሌ አሰሳ", collapse: "የጎን አሞሌን ሰብስብ",
      newChat: "አዲስ ውይይት", searchAria: "ፈልግ", searchPlaceholder: "ፈልግ", searchResults: "ውጤቶች",
      noSearchResults: "ተመሳሳይ ርዕስ የለም።", recent: "የቅርብ ጊዜ ርዕሶች", settings: "ቅንብሮች",
      language: { label: "ቋንቋ", ariaLabel: "ቋንቋ ቀይር" }, apps: "መተግበሪያዎች", automations: "አውቶሜሽኖች",
      skills: { title: "ክህሎቶች" },
    },
    settings: {
      backToChat: "ወደ ውይይት ተመለስ", sidebar: { title: "ቅንብሮች", ariaLabel: "የቅንብሮች ክፍሎች" },
      nav: { appearance: "ገጽታ", overview: "አጠቃላይ እይታ", models: "ሞዴሎች", providers: "አቅራቢዎች", channels: "ቻናሎች", notifications: "ማሳወቂያዎች", capabilities: "ችሎታዎች", mcp: "MCP", runtime: "ስርዓት", advanced: "የላቀ" },
      sections: { interface: "በይነገጽ", localPreferences: "የበይነገጽ ምርጫዎች", system: "ስርዓት", capabilities: "ችሎታዎች", mcp: "የMCP አገልግሎቶች" },
      rows: { theme: "ገጽታ", language: "ቋንቋ", readingTextSize: "የንባብ ጽሑፍ መጠን", activityMode: "የእንቅስቃሴ ዝርዝሮች", codeWrap: "የኮድ መጠቅለያ", localServiceAccess: "የአካባቢ አገልግሎቶች", webuiDefaultAccess: "ነባሪ መዳረሻ" },
      values: { light: "ብርሃን", auto: "ራስ-ሰር", default: "ነባሪ", expanded: "የተስፋፋ", summary: "ማጠቃለያ", diff: "ልዩነት", collapsedDiff: "የተጠቀለለ ልዩነት", defaultPermission: "ነባሪ ፈቃድ", fullAccess: "ሙሉ መዳረሻ", on: "አብራ", off: "አጥፋ" },
      readingTextSize: { small: "ትንሽ ጽሑፍ", standard: "መደበኛ ጽሑፍ", large: "ትልቅ ጽሑፍ" },
      help: { language: "የበይነገጹን ቋንቋ ይምረጡ።", localServiceAccess: "የሙሉ መዳረሻ የሼል ትዕዛዞች የአካባቢ አገልግሎቶችን ማግኘት ይችላሉ።", webuiDefaultAccess: "ፕሮጀክቱ የተለየ ፈቃድ ከሌለው ይህ ይጠቀማል።" },
      notifications: { scope: "ይህ አሳሽ", intro: "አንድ ተግባር ሲጠናቀቅ እንዴት እንደሚያሳውቅዎ ይምረጡ።", pageRequired: "ይህ ገጽ ሲዘጋ አዲስ ማሳወቂያ አይኖርም።", permissionFailed: "ፈቃድ መጠየቅ አልተቻለም። እንደገና ይሞክሩ።", completed: "ተግባሩ ተጠናቋል።", failed: "ተግባሩ አልተሳካም።", interrupted: "ተግባሩ ትኩረት ይፈልጋል።" },
      capabilities: { providerSupport: "የአቅራቢ ጥገኞች", searchSupport: "የፍለጋ ጥገኞች", installing: "አስፈላጊ ጥቅሎች በመጫን ላይ…" },
      apps: { filterPlugins: "ፕለጊኖች", filterMcp: "MCP", mcpTools: "የMCP መሣሪያዎች" },
      models: { primary: "ዋና" },
    },
    chat: { loading: "በመጫን ላይ…", noSessions: "እስካሁን ምንም ክፍለ ጊዜ የለም።", newChat: "አዲስ ርዕስ", rename: "እንደገና ሰይም", delete: "ሰርዝ", cancelSelection: "ምርጫን ሰርዝ" },
    thread: { composer: { placeholderThread: "መልዕክትዎን ይጻፉ…", placeholderHero: "ማድረግ የሚፈልጉትን ይግለጹ", inputAria: "የመልዕክት ማስገቢያ", send: "መልዕክት ላክ", stop: "ምላሹን አቁም" } },
  },
  om: {
    app: {
      loading: { connecting: "Saba waliin wal qunnamaa jira…", boot: "Saba fe'amaa jira…" },
      meta: { description: "Web UI saba — bakka hojii saba kee waliin haasa'i." },
      error: { title: "Saba gahuu hin dandeenye", gatewayHint: "Gateway'n hojjechaa jiraachuu fi biraawzari kun teessoo WebUI argachuu danda'uu mirkaneessi." },
      auth: { title: "Saba waliin wal qunnami", label: "Jecha darbii WebUI", helpTitle: "Jecha darbii eessaa argachuu danda'a?", submit: "Wal qunnami", required: "Jecha darbii galchi", invalid: "Jecha darbii sirrii miti" },
      account: { section: "Herrega", logoutHint: "Biraawzara kana gateway irraa baasi.", logout: "Ba'i" },
      system: { section: "Sirna", restartAction: "Irra deebi'ii kaasi", restart: "Saba irra deebi'ii kaasi", restarting: "Irra deebi'aa jira…" },
    },
    common: { retry: "Irra deebi'ii yaali", dismiss: "Cufi", close: "Cufi", current: "Ammaa", cancel: "Haqi" },
    sidebar: { resize: "Guddina barruu cinaa jijjiiri", navigation: "Navigeeshinii barruu cinaa", collapse: "Barruu cinaa kuusi", newChat: "Haasa'a haaraa", searchAria: "Barbaadi", searchPlaceholder: "Barbaadi", searchResults: "Bu'aawwan", noSearchResults: "Mata-dureen walfakkaataan hin jiru.", recent: "Mata-dureewwan dhiheenyaa", settings: "Qindaa'ina", language: { label: "Afaan", ariaLabel: "Afaan jijjiiri" }, apps: "Appilikeeshinoota", automations: "Ofumaan hojjechuu", skills: { title: "Dandeettiiwwan" } },
    settings: { backToChat: "Gara haasa'aatti deebi'i", sidebar: { title: "Qindaa'ina", ariaLabel: "Kutaa qindaa'inaa" }, nav: { appearance: "Bifa", overview: "Ibsa waliigalaa", models: "Moodeelota", providers: "Dhiyeessitoota", channels: "Chaanaalota", advanced: "Dabalataa" }, sections: { interface: "Interfeesii", localPreferences: "Filannoo interfeesii" }, rows: { theme: "Bifa", language: "Afaan", readingTextSize: "Hammamtaa barruu dubbisummaa", activityMode: "Bal'ina sochii", codeWrap: "Marsiimoo koodii" }, values: { light: "Ifaa", auto: "Ofumaan", expanded: "Bal'aa", on: "Banaa", off: "Cufaa" }, readingTextSize: { small: "Barruu xiqqaa", standard: "Barruu idilee", large: "Barruu guddaa" }, help: { language: "Afaan interfeesii filadhu." } },
    chat: { loading: "Fe'amaa jira…", noSessions: "Ammaaf seeshinii hin jiru.", newChat: "Mata-duree haaraa", rename: "Maqaa jijjiiri", delete: "Haqi", cancelSelection: "Filannoo haqii" },
    thread: { composer: { placeholderThread: "Ergaa kee barreessi…", placeholderHero: "Wanta gochuu barbaaddu ibsi", inputAria: "Galtee ergaa", send: "Ergaa ergi", stop: "Deebii dhaabi" } },
  },
  ti: {
    app: {
      loading: { connecting: "ሳባ ይገናን ኣሎ…", boot: "ሳባ ይጽዓን ኣሎ…" },
      meta: { description: "Web UI ሳባ — ምስ ቦታ ስራሕ ሳባኻ ተዘራረብ።" },
      error: { title: "ሳባ ምብጻሕ ኣይተኻእለን", gatewayHint: "ጌትዌይ ይሰርሕ ከምዘሎን እዚ ብራውዘር ናይ WebUI ኣድራሻ ክረኽቦ ከምዝኽእልን ኣረጋግጽ።" },
      auth: { title: "ምስ ሳባ ተራኸብ", label: "ናይ WebUI መሕለፊ ቃል", helpTitle: "መሕለፊ ቃል ኣበይ ክረኽቦ እኽእል?", submit: "ተራኸብ", required: "መሕለፊ ቃል ኣእቱ", invalid: "ጌጋ መሕለፊ ቃል" },
      account: { section: "ሕሳብ", logoutHint: "ነዚ ብራውዘር ካብ ጌትዌይ ኣላቅቆ።", logout: "ውጻእ" },
      system: { section: "ስርዓት", restartAction: "እንደገና ኣስእን", restart: "ሳባ እንደገና ኣስእን", restarting: "እንደገና ይስእን ኣሎ…" },
    },
    common: { retry: "እንደገና ፈትን", dismiss: "ዕጸው", close: "ዕጸው", current: "ሕጂ", cancel: "ሰርዝ" },
    sidebar: { resize: "ናይ ጎድኒ መስመር መጠን ቀይር", navigation: "ናይ ጎድኒ መስመር ኣሰሳ", collapse: "ናይ ጎድኒ መስመር ኣከብ", newChat: "ሓድሽ ዕላል", searchAria: "ድለ", searchPlaceholder: "ድለ", searchResults: "ውጽኢታት", noSearchResults: "ተመሳሳሊ ኣርእስቲ የለን።", recent: "ናይ ቀረባ ኣርእስታት", settings: "ቅንብራት", language: { label: "ቋንቋ", ariaLabel: "ቋንቋ ቀይር" }, apps: "መተግበሪያታት", automations: "ኣውቶሜሽን", skills: { title: "ክእለታት" } },
    settings: { backToChat: "ናብ ዕላል ተመለስ", sidebar: { title: "ቅንብራት", ariaLabel: "ክፍልታት ቅንብራት" }, nav: { appearance: "ትርኢት", overview: "ሓፈሻዊ ርእይቶ", models: "ሞዴላት", providers: "ኣቕረብቲ", channels: "ቻነላት", advanced: "ዝማዕበለ" }, sections: { interface: "ኢንተርፌስ", localPreferences: "ምርጫታት ኢንተርፌስ" }, rows: { theme: "ትርኢት", language: "ቋንቋ", readingTextSize: "መጠን ጽሑፍ ንባብ", activityMode: "ዝርዝር ንጥፈታት", codeWrap: "ምጥቕላል ኮድ" }, values: { light: "ብርሃን", auto: "ብኣውቶማቲክ", expanded: "ዝሰፍሐ", on: "ኣብ", off: "ጠፍአ" }, readingTextSize: { small: "ንእሽቶ ጽሑፍ", standard: "መደበኛ ጽሑፍ", large: "ዓቢ ጽሑፍ" }, help: { language: "ቋንቋ ኢንተርፌስ ምረጽ።" } },
    chat: { loading: "ይጽዓን ኣሎ…", noSessions: "ገና ሰሽን የለን።", newChat: "ሓድሽ ኣርእስቲ", rename: "እንደገና ሰይም", delete: "ሰርዝ", cancelSelection: "ምርጫ ሰርዝ" },
    thread: { composer: { placeholderThread: "መልእኽትኻ ጽሓፍ…", placeholderHero: "ክትገብሮ ደሊኻ ዘለኻ ግለጽ", inputAria: "መእተዊ መልእኽቲ", send: "መልእኽቲ ስደድ", stop: "ምላሽ ኣቁም" } },
  },
};
