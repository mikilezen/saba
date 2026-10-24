"""Language-first, consent-based Saba conversation workflow."""

import re
from datetime import date
from collections.abc import Awaitable, Callable

from saba_et.audit import AuditLog
from saba_et.agent import GeminiSearchError
from saba_et.domain import OutgoingMessage
from saba_et.knowledge import ServiceCatalog
from saba_et.permissions import ApprovalPolicy
from saba_et.profile_store import ProfileStore
from saba_et.task_store import TaskStore


LANGUAGES = {
    "am": "አማርኛ",
    "om": "Afaan Oromoo",
    "ti": "ትግርኛ",
    "en": "English",
}

TASK_TEXT = {
    "usage": {
        "en": "Task commands: /tasks · /task create <goal> · /task <id> · /task pause <id> · /task resume <id>. Don’t put passwords, OTPs, ID numbers, or document contents in a task.",
        "am": "የተግባር ትዕዛዞች፦ /tasks · /task create <ግብ> · /task <id> · /task pause <id> · /task resume <id>። የይለፍ ቃል፣ OTP፣ መታወቂያ ቁጥር ወይም የሰነድ ይዘት አያስገቡ።",
        "om": "Ajajoota hojii: /tasks · /task create <kaayyoo> · /task <id> · /task pause <id> · /task resume <id>. Jecha iccitii, OTP, lakkoofsa eenyummaa ykn qabiyyee galmee hin galchin.",
        "ti": "ትእዛዛት ዕማም፦ /tasks · /task create <ዕላማ> · /task <id> · /task pause <id> · /task resume <id>። መሕለፊ ቃል፣ OTP፣ ቁጽሪ መንነት ወይ ትሕዝቶ ሰነድ ኣይተእትዉ።",
    },
    "none": {"en": "You have no open tasks.", "am": "ክፍት ተግባር የለዎትም።", "om": "Hojii banaa hin qabdu.", "ti": "ክፉት ዕማም የብልኩምን።"},
    "created": {"en": "Task created", "am": "ተግባሩ ተፈጥሯል", "om": "Hojiin uumameera", "ti": "ዕማም ተፈጢሩ"},
    "not_found": {"en": "I couldn’t find that task under your account, or the command is invalid.", "am": "ያንን ተግባር በመለያዎ ውስጥ አላገኘሁም ወይም ትዕዛዙ ልክ አይደለም።", "om": "Hojii sana herrega kee keessatti hin arganne ykn ajajni sirrii miti.", "ti": "ነቲ ዕማም ኣብ መለያኹም ኣይረኸብኩዎን ወይ ትእዛዙ ቅኑዕ ኣይኮነን።"},
    "paused": {"en": "Task paused.", "am": "ተግባሩ ታግዷል።", "om": "Hojiin dhaabbateera.", "ti": "ዕማም ተኣጊዱ።"},
    "resumed": {"en": "Task resumed. It is pending; Saba will confirm the safe next step before acting.", "am": "ተግባሩ ቀጥሏል። ከመተግበሩ በፊት Saba ቀጣዩን ደህንነቱ የተጠበቀ እርምጃ ያረጋግጣል።", "om": "Hojiin itti fufeera. Saba tarkaanfii nageenya qabu mirkaneessuun dura hin raawwatu.", "ti": "ዕማም ቀጺሉ ኣሎ። Saba ቅድሚ ምግባሩ ቀጻሊ ውሑስ ስጉምቲ ከረጋግጽ እዩ።"},
}

TEXT = {
    "language_prompt": {
        "am": "Hello / ሰላም / Akkam / ሰላም — ቋንቋ ይምረጡ / Afaan filadhu:",
        "om": "Hello / ሰላም / Akkam / ሰላም — Afaan filadhu / ቋንቋ ይምረጡ:",
        "ti": "Hello / ሰላም / Akkam / ሰላም — ቋንቋ ምረጹ / Afaan filadhu:",
        "en": "Hello / ሰላም / Akkam / ሰላም — choose your language / Afaan filadhu:",
    },
    "back": {"am": "⬅️ ተመለስ", "om": "⬅️ Duubatti", "ti": "⬅️ ተመለስ", "en": "⬅️ Back"},
    "method_prompt": {
        "am": "መቀጠል የሚፈልጉት እንዴት ነው? ፋይዳ ግንኙነት ገና ዝግጁ አይደለም።",
        "om": "Akkamitti itti fufuu barbaadda? Wal-qunnamtiin Fayda ammaaf hin jiru.",
        "ti": "ብኸመይ ክትቅጽሉ ትደልዩ? ምስ ፋይዳ ምትእስሳር ገና ኣይተዳለወን።",
        "en": "How would you like to continue? Fayda connection is not available yet.",
    },
    "fayda": {
        "am": "🔗 ፋይዳ ያገናኙ (በቅርቡ)",
        "om": "🔗 Fayda wal-qunnamsi (dhiyootti)",
        "ti": "🔗 ፋይዳ ኣራኽብ (ቀረባ ግዜ)",
        "en": "🔗 Connect Fayda (coming soon)",
    },
    "manual": {
        "am": "✍️ በእጅ መረጃ ያስገቡ",
        "om": "✍️ Odeeffannoo harkaan galchi",
        "ti": "✍️ ሓበሬታ ብኢድ ኣእቱ",
        "en": "✍️ Enter details manually",
    },
    "fayda_unavailable": {
        "am": "የፋይዳ ግንኙነት አሁን የለም፤ ምንም የመታወቂያ ቁጥር ወይም የይለፍ ቃል አይላኩ። በእጅ መረጃ ወይም ቋንቋ መቀየር ይችላሉ።",
        "om": "Wal-qunnamtiin Fayda amma hin jiru. Lakkoofsa eenyummaa ykn jecha iccitii hin ergin. Odeeffannoo harkaan galchi ykn afaan jijjiiri.",
        "ti": "ምትእስሳር ፋይዳ ሕጂ የለን፤ ቁጽሪ መንነት ወይ መሕለፊ ቃል ኣይትልኣኹ። ብኢድ ሓበሬታ ኣእትዉ ወይ ቋንቋ ቀይሩ።",
        "en": "Fayda connection is not available yet. Do not send an ID number or password. You can enter details manually or change language.",
    },
    "privacy_consent": {
        "am": "በእጅ ለመቀጠል ስም፣ ዕድሜ፣ የትውልድ ዓመት እና አካባቢ እጠይቃለሁ። ከተስማሙ ዝርዝሮቹ በዚህ ኮምፒውተር ላይ ይቀመጣሉ፤ ወደ Gemini አይላኩም። /forget በማለት ማጥፋት ይችላሉ። የፋይዳ/መታወቂያ ቁጥር ወይም የይለፍ ቃል አይላኩ። ይስማማሉ?",
        "om": "Harkaan itti fufuuf maqaa, umurii, bara dhalootaa fi naannoo si gaafadha. Yoo waliigalte, odeeffannoon kun kompiitara kana irratti ni kuufama; Gemini'itti hin ergamu. /forget jechuun ni haqama. Lakkoofsa Fayda/eenyummaa ykn jecha iccitii hin ergin. Ni waliigaltaa?",
        "ti": "ብኢድ ንምቕጻል ስም፣ ዕድመ፣ ዓመት ልደትን ከባቢን ክሓትት እየ። እንተ ተሰማሚዕኩም እዚ ሓበሬታ ኣብዚ ኮምፒውተር ይቕመጥ፤ ናብ Gemini ኣይለኣኽን። /forget ብምጽሓፍ ክትድምስስዎ ትኽእሉ። ቁጽሪ ፋይዳ/መንነት ወይ መሕለፊ ቃል ኣይትልኣኹ። ትሰማምዑ ዶ?",
        "en": "To continue manually, I’ll ask for your contact name, age, birth year, and location. If you agree, these details will be stored in Saba’s local database on this computer and will not be sent to Gemini. Send /forget to clear them. Do not send a Fayda/ID number or password. Continue?",
    },
    "yes": {"am": "እሺ፣ ቀጥል", "om": "Eeyyee, itti fufi", "ti": "እወ፣ ቀጽል", "en": "Yes, continue"},
    "no": {"am": "አይ፣ አቁም", "om": "Lakki, dhaabi", "ti": "ኣይፋል፣ ኣቋርጽ", "en": "No, stop"},
    "ask_name": {"am": "ስምዎን ይጻፉ (ወይም ዝለል ይበሉ)። የመታወቂያ ቁጥር አይላኩ።", "om": "Maqaa kee barreessi (ykn 'skip' jedhi). Lakkoofsa eenyummaa hin ergin.", "ti": "ስምኩም ጽሓፉ (ወይ 'skip' በሉ)። ቁጽሪ መንነት ኣይትልኣኹ።", "en": "Enter your name (or type skip). Do not send an ID number."},
    "ask_age": {"am": "ዕድሜዎ ስንት ነው? ቁጥር ብቻ ይጻፉ ወይም ዝለል ይበሉ።", "om": "Umuriin kee meeqa? Lakkoofsa qofa barreessi ykn 'skip' jedhi.", "ti": "ዕድመኹም ክንደይ እዩ? ቁጽሪ ጥራይ ጽሓፉ ወይ 'skip' በሉ።", "en": "How old are you? Enter a number or type skip."},
    "ask_birth_year": {"am": "የትውልድ ዓመትዎን በ4 አሃዝ ይጻፉ (ወይም ዝለል)።", "om": "Bara dhalootaa kee (lakkoofsa 4) barreessi ykn 'skip' jedhi.", "ti": "ዓመት ልደትኩም ብ4 ኣሃዝ ጽሓፉ (ወይ 'skip')።", "en": "Enter your 4-digit birth year (or type skip)."},
    "ask_location": {"am": "አካባቢዎን ወይ ከተማዎን ይጻፉ (ወይም ዝለል)።", "om": "Naannoo ykn magaalaa kee barreessi ykn 'skip' jedhi.", "ti": "ከባቢኹም ወይ ከተማኹም ጽሓፉ (ወይ 'skip')።", "en": "Enter your location or city (or type skip)."},
    "ask_service": {"am": "እንዴት ልርዳዎ? የሚፈልጉትን የመንግስት አገልግሎት ይግለጹ። ምንጮችን በራስ-ሰር እፈልጋለሁ።", "om": "Akkamitti si gargaaru? Tajaajila mootummaa barbaaddu ibsi. Maddoota nan barbaada.", "ti": "ብኸመይ ክሕግዘኩም? ዝደለኹምዎ ኣገልግሎት መንግስቲ ግለጹ። ምንጭታት ብርእሰ-ሰር ክደሊ እየ።", "en": "What government service do you need? Describe it and I’ll search for official sources."},
    "manual_done": {"am": "አመሰግናለሁ። ዝርዝሮቹ በዚህ ኮምፒውተር ላይ ተቀምጠዋል፤ /forget በማለት ያጥፏቸው። አሁን የሚፈልጉትን አገልግሎት ይጻፉ።", "om": "Galatoomi. Odeeffannoon kompiitara kana irratti kuufameera; /forget jechuun haqi. Amma tajaajila barbaaddu barreessi.", "ti": "የቐንየለይ። ሓበሬታ ኣብዚ ኮምፒውተር ተቐሚጡ እዩ፤ /forget ብምጽሓፍ ደምስስዎ። ሕጂ ዝደለኹምዎ ኣገልግሎት ጽሓፉ።", "en": "Thanks. Those details are saved locally on this computer; send /forget to clear them. Now describe the service you need."},
    "no_consent": {"am": "እሺ፣ ዝርዝር አልጠይቅም። /start በማለት ቋንቋ ይምረጡ።", "om": "Tole, odeeffannoo dhuunfaa hin gaafadhu. Afaan filachuuf /start barreessi.", "ti": "እሺ፣ ውልቃዊ ሓበሬታ ኣይሓትትን። ቋንቋ ንምምራጽ /start ጽሓፉ።", "en": "Okay, I won’t ask for personal details. Send /start to choose a language."},
    "bad_age": {"am": "እባክዎ ከ0 እስከ 120 ያለ ዕድሜ ይጻፉ ወይ ዝለል ይበሉ።", "om": "Umurii 0 hanga 120 barreessi ykn 'skip' jedhi.", "ti": "ካብ 0 ክሳብ 120 ዝኾነ ዕድመ ጽሓፉ ወይ 'skip' በሉ።", "en": "Enter an age from 0 to 120, or type skip."},
    "bad_year": {"am": "እባክዎ ትክክለኛ የ4 አሃዝ ዓመት ይጻፉ ወይ ዝለል ይበሉ።", "om": "Bara sirrii lakkoofsa 4 barreessi ykn 'skip' jedhi.", "ti": "ትኽክለኛ ዓመት ብ4 ኣሃዝ ጽሓፉ ወይ 'skip' በሉ።", "en": "Enter a valid 4-digit year or type skip."},
    "id_warning": {"am": "ይህ የመታወቂያ ቁጥር ይመስላል። አልያዝኩትም። እባክዎ ቁጥሩን አቁሙና የሚጠየቀውን መረጃ ብቻ ይላኩ።", "om": "Kun lakkoofsa eenyummaa fakkaata; hin kuufne. Lakkoofsa sana hin ergin; odeeffannoo gaafatame qofa ergi.", "ti": "እዚ ቁጽሪ መንነት ይመስል፤ ኣይሓዝኩዎን። እቲ ቁጽሪ ኣይትልኣኹ፤ እቲ ዝተሓተተ ሓበሬታ ጥራይ ስደዱ።", "en": "That looks like an ID number, so I did not keep it. Please send only the requested information, not the ID number."},
    "forget": {"am": "የግል ዝርዝሮቹ ከዳታቤዝ ተሰርዘዋል፤ የቋንቋ ምርጫ ይቆያል።", "om": "Odeeffannoon dhuunfaa kuusdeetaa keessaa haqameera; filannoon afaanii ni hafa.", "ti": "ውልቃዊ ሓበሬታ ካብ ዳታቤዝ ተደምሲሱ እዩ፤ ምርጫ ቋንቋ ግን ይተርፍ።", "en": "Your saved personal details have been deleted; your language preference is kept."},
    "privacy": {"am": "ምንጭ መፈለግ ከጠየቁ በኋላ በራስ-ሰር ይሄዳል። ስልክ ጥሪ፣ ክፍያ ወይም ቅጽ ማስገባት ሁልጊዜ አዲስ ግልጽ ፈቃድ ይፈልጋል። በእጅ የሚሰጡ ዝርዝሮች ከፈቀዱ በኋላ በዚህ ኮምፒውተር ይቀመጣሉ። /forget ያጥፋቸዋል።", "om": "Madda barbaadu yeroo ati gaafattu ofumaan ni raawwatama. Bilbila, kaffaltii ykn unka erguun eeyyama haaraa ifa ta'e barbaada. Odeeffannoon harkaan kennamu yoo waliigalte kompiitara kana irratti kuufama; /forget jechuun haqi.", "ti": "ምንጪ ምድላይ ክትሓቱ ከለኹም ብርእሰ-ሰር ይካየድ። ስልኪ፣ ክፍሊት ወይ ቅጥዒ ምልኣኽ ሓድሽ ግልጺ ፍቓድ ይሓትት። ብኢድ ዝተዋህበ ሓበሬታ እንተ ፈቒድኩም ኣብዚ ኮምፒውተር ይቕመጥ፤ /forget ይድምስሶ።", "en": "Read-only source search runs when you ask for help. Calls, payments, and form submissions require a fresh explicit yes. Manual profile details are saved locally only after consent; send /forget to delete them."},
    "agent_needed": {"am": "የAI የፍለጋ ኤጀንቱ አልተዋቀረም። በፕሮጀክቱ .env ፋይል ውስጥ GEMINI_API_KEY ያስገቡ።", "om": "AI agentiin barbaacha hin qophoofne. Faayila .env pirojektii keessatti GEMINI_API_KEY galchi.", "ti": "ኤጀንት ድለያ AI ኣይተዳለወን። GEMINI_API_KEY ኣብ ፋይል .env ኣእትዉ።", "en": "The AI search agent is not configured. Put GEMINI_API_KEY in the project-root .env file or the process environment, then restart Saba."},
    "agent_error": {"am": "የGemini ፍለጋ ሳይጠበቅ ተቋርጧል። የSaba ሎግ ያረጋግጡ።", "om": "Barbaachi Gemini haala hin eegamneen dhaabbate. Galmee Saba ilaali.", "ti": "ድለያ Gemini ብዘይተጸበናዮ ተቛሪጹ። ሎግ Saba መርምሩ።", "en": "Gemini search stopped unexpectedly. Check the Saba console log for the error category."},
}

GEMINI_FAILURES = {
    "credentials": {
        "en": "Gemini rejected the API key or access. Check GEMINI_API_KEY in the project .env, confirm the Gemini API is enabled, then restart Saba.",
        "am": "Gemini ቁልፉን ወይም ፈቃዱን አልተቀበለም። በፕሮጀክቱ .env ውስጥ GEMINI_API_KEY ያረጋግጡ፣ Gemini API መንቃቱን ያረጋግጡና Saba እንደገና ያስነሱ።",
        "om": "Gemini furtuu ykn hayyama API hin fudhanne. GEMINI_API_KEY faayila .env keessatti mirkaneessi; Gemini API banuun Saba irra deebi'ii jalqabi.",
        "ti": "Gemini ነቲ API key ወይ ፍቓድ ኣይተቐበሎን። GEMINI_API_KEY ኣብ .env መርምሩ፣ Gemini API ከም ዝነቐሐ ኣረጋግጹን Saba ደጊምኩም ኣበግሱ።",
    },
    "quota": {
        "en": "Gemini hit its request quota or billing limit. Check the Gemini AI Studio usage and quota page; wait for reset or enable billing.",
        "am": "የGemini የጥያቄ ገደብ ወይም የክፍያ ገደብ ደርሷል። በGemini AI Studio የአጠቃቀምና የገደብ ገጽ ይመልከቱ።",
        "om": "Daangaan gaaffii ykn kaffaltii Gemini ga'eera. Fuula usage fi quota Gemini AI Studio ilaali.",
        "ti": "ደረት ሕቶ ወይ ክፍሊት Gemini በጺሑ። ኣብ Gemini AI Studio ናይ usage እና quota ገጽ ርኣዩ።",
    },
    "timeout": {
        "en": "Gemini took longer than 25 seconds and timed out. Try again when the connection is stable.",
        "am": "Gemini ከ25 ሰከንድ በላይ ወስዶ ጊዜው አልቋል። ግንኙነቱ ሲረጋጋ እንደገና ይሞክሩ።",
        "om": "Gemini sekondii 25 caalaa fudhatee yeroo darbe. Wal-qunnamtiin yeroo tasgabbaa'u irra deebi'i.",
        "ti": "Gemini ካብ 25 ሰከንድ ንላዕሊ ወሲዱ ግዜ ኣብቂዑ። መርበብ ምስ ዝረጋጋ ደጊምኩም ፈትኑ።",
    },
    "network": {
        "en": "Saba could not reach Gemini. Check your internet connection, firewall, or VPN, then try again.",
        "am": "Saba Geminiን ማግኘት አልቻለም። ኢንተርኔት፣ firewall ወይም VPN ያረጋግጡና እንደገና ይሞክሩ።",
        "om": "Saba Gemini bira ga'uu hin dandeenye. Intarneetii, firewall ykn VPN ilaali; achiis irra deebi'i.",
        "ti": "Saba ናብ Gemini ክበጽሕ ኣይከኣለን። ኢንተርነት፣ firewall ወይ VPN መርምሩ።",
    },
    "unavailable": {
        "en": "Gemini is temporarily unavailable or rejected this request. Wait a moment and retry; if it repeats, check the Saba console log.",
        "am": "Gemini ለጊዜው አይገኝም ወይም ጥያቄውን አልተቀበለም። ትንሽ ጠብቀው ይሞክሩ፤ ከቀጠለ የSaba ሎግ ይመልከቱ።",
        "om": "Gemini yeroo muraasaaf hin hojjetu ykn gaaffii kana hin fudhanne. Xiqqoo eegii yaali; yoo itti fufe galmee Saba ilaali.",
        "ti": "Gemini ንሓጺር ግዜ ኣይሰርሕን ወይ ነዚ ሕቶ ኣይተቐበሎን። ቁሩብ ጽንሑ ደጊምኩም ፈትኑ።",
    },
    "searchapi_credentials": {
        "en": "SearchAPI rejected its key. Check the rotated SEARCHAPI_API_KEY in your environment.",
        "am": "SearchAPI ቁልፉን አልተቀበለም። አዲሱን SEARCHAPI_API_KEY ያረጋግጡ።",
        "om": "SearchAPI furtuu hin fudhanne. SEARCHAPI_API_KEY haaraa ilaali.",
        "ti": "SearchAPI ነቲ key ኣይተቐበሎን። ሓድሽ SEARCHAPI_API_KEY መርምሩ።",
    },
    "searchapi_quota": {
        "en": "SearchAPI reached its account quota or credit limit. Check your SearchAPI dashboard.",
        "am": "የSearchAPI የአጠቃቀም ወይም የክሬዲት ገደብ ደርሷል። ዳሽቦርዱን ይመልከቱ።",
        "om": "Daangaan SearchAPI ykn credit ga'eera. Dashboard isaa ilaali.",
        "ti": "ናይ SearchAPI መጠን ወይ credit ደረት በጺሑ። Dashboard መርምሩ።",
    },
    "searchapi_timeout": {
        "en": "SearchAPI timed out. Check the connection and try again.",
        "am": "SearchAPI ጊዜው አልቋል። ግንኙነቱን ያረጋግጡና እንደገና ይሞክሩ።",
        "om": "SearchAPI yeroo isaa fixate. Wal-qunnamtii ilaaliitii irra deebi'i.",
        "ti": "SearchAPI ግዜ ኣብቂዑ። መርበብ መርምሩን ደጊምኩም ፈትኑን።",
    },
    "searchapi_network": {
        "en": "Saba could not reach SearchAPI. Check the server's internet connection and try again.",
        "am": "Saba SearchAPIን ማግኘት አልቻለም። የአገልጋዩን ኢንተርኔት ያረጋግጡ።",
        "om": "Saba SearchAPI bira ga'uu hin dandeenye. Intarneetii server ilaali.",
        "ti": "Saba ናብ SearchAPI ክበጽሕ ኣይከኣለን። ኢንተርነት ኣገልጋሊ መርምሩ።",
    },
    "searchapi_invalid_response": {
        "en": "SearchAPI returned an unreadable response. Retry later; no unsupported answer was given.",
        "am": "SearchAPI የማይነበብ ምላሽ ሰጥቷል። ቆይተው ይሞክሩ።",
        "om": "SearchAPI deebii dubbifamuu hin dandeenye kenne. Booda irra deebi'i.",
        "ti": "SearchAPI ዘይንበብ ምላሽ ሂቡ። ድሕሪ ግዜ ደጊምኩም ፈትኑ።",
    },
    "searchapi_unavailable": {
        "en": "SearchAPI is temporarily unavailable. Try again later; no unsupported answer was given.",
        "am": "SearchAPI ለጊዜው አይገኝም። ቆይተው ይሞክሩ።",
        "om": "SearchAPI yeroo muraasaaf hin hojjetu. Booda irra deebi'i.",
        "ti": "SearchAPI ንሓጺር ግዜ ኣይሰርሕን። ድሕሪ ግዜ ፈትኑ።",
    },
    "invalid_output": {
        "en": "Gemini returned a response that did not match Saba’s required answer structure. Please retry; no action was taken.",
        "am": "Gemini ከSaba የምላሽ ቅርጽ ጋር የማይዛመድ ምላሽ ሰጥቷል። እንደገና ይሞክሩ፤ ምንም እርምጃ አልተወሰደም።",
        "om": "Deebiin Gemini caasaa barbaachisu hin guunne. Irra deebi'i; tarkaanfiin hin fudhatamne.",
        "ti": "Gemini ምላሽ ኣብ ዝተወሰነ ቅርጺ ኣይመጸን። ደጊምኩም ፈትኑ፤ ስጉምቲ ኣይተወሰደን።",
    },
}


PROGRESS = {
    "catalog": {
        "am": "የሳባ ET አገልግሎት መዝገብ እየፈተሽኩ ነው…",
        "om": "Galmee tajaajilaa Saba ET sakatta'aa jira…",
        "ti": "ካታሎግ ኣገልግሎት Saba ET ይምርምር ኣለኹ…",
        "en": "Checking Saba ET’s service directory…",
    },
    "search": {
        "am": "በGemini Google Search ይፋዊ ምንጮችን እየፈለግኩ ነው…",
        "om": "Gemini Google Search fayyadamuun maddoota mootummaa barbaadaa jira…",
        "ti": "ብGemini Google Search ወግዓዊ ምንጭታት ይደሊ ኣለኹ…",
        "en": "Searching with Gemini Google Search…",
    },
    "searchapi": {
        "am": "በSearchAPI የኢትዮጵያ ይፋዊ ድረ-ገጾችን እየፈለግኩ ነው…",
        "om": "SearchAPI fayyadamuun marsariitii mootummaa Itoophiyaa barbaadaa jira…",
        "ti": "ብSearchAPI ወግዓዊ ናይ ኢትዮጵያ መርበባት ይደሊ ኣለኹ…",
        "en": "Searching Ethiopian official websites with SearchAPI…",
    },
    "gemini": {
        "am": "ለቋንቋዎ ምላሽ እያዘጋጀሁ ነው…",
        "om": "Deebii afaan keetiin qopheessaa jira…",
        "ti": "ብቋንቋኹም መልሲ የዳሉ ኣለኹ…",
        "en": "Preparing the answer in your language…",
    },
    "verify": {
        "am": "የምንጭ አገናኞችን እያረጋገጥኩ ነው…",
        "om": "Liinkii maddootaa mirkaneessaa jira…",
        "ti": "መራኸቢ ምንጭታት የረጋግጽ ኣለኹ…",
        "en": "Checking source links…",
    },
    "call": {
        "am": "በVapi በኩል የተመረጠውን ይፋዊ ቢሮ እየደወልኩ ነው…",
        "om": "Waajjira mootummaa filatame Vapi fayyadamuun bilbilaa jira…",
        "ti": "ብVapi ናብቲ ዝተመርጸ ወግዓዊ ቤት ጽሕፈት ይድውል ኣለኹ…",
        "en": "Calling the selected public office through Vapi…",
    },
}


class SabaApplication:
    def __init__(self, catalog: ServiceCatalog, audit_log: AuditLog, agent=None, profile_store: ProfileStore | None = None, provider_directory=None, task_store: TaskStore | None = None) -> None:
        self._catalog = catalog
        self._audit_log = audit_log
        self._agent = agent
        self._profile_store = profile_store
        self._provider_directory = provider_directory
        self._task_store = task_store
        self._languages: dict[int, str] = {}
        self._stages: dict[int, str] = {}
        self._profiles: dict[int, dict[str, str]] = {}
        self._policy = ApprovalPolicy()

    def _say(self, key: str, language: str) -> str:
        return TEXT[key].get(language, TEXT[key]["en"])

    @staticmethod
    def _format_agent_result(result, language: str) -> str:
        risk_names = {
            "low": {"en": "LOW · read-only", "am": "ዝቅተኛ · ንማንበብ ብቻ", "om": "GAD AANEE · dubbisa qofa", "ti": "ትሑት · ንምንባብ ጥራይ"},
            "medium": {"en": "MEDIUM · review before use", "am": "መካከለኛ · ከመጠቀም በፊት ይገምግሙ", "om": "GIDDU-GALEESSA · fayyadamuun dura ilaali", "ti": "ማእከላይ · ቅድሚ ምጥቃም ገምግሙ"},
            "high": {"en": "HIGH · explicit approval required", "am": "ከፍተኛ · ግልጽ ፈቃድ ያስፈልጋል", "om": "OL-AANAA · eeyyama ifa ta'e barbaada", "ti": "ልዑል · ግልጺ ፍቓድ የድሊ"},
        }
        labels = {
            "en": ("Risk", "Tools", "Next step"),
            "am": ("የአደጋ ደረጃ", "የተጠቀሙ መሣሪያዎች", "ቀጣይ እርምጃ"),
            "om": ("Sadarkaa balaa", "Meeshaalee fayyadaman", "Tarkaanfii itti aanu"),
            "ti": ("ደረጃ ሓደጋ", "ዝተጠቕሙሎም መሳርሒታት", "ዝቕጽል ስጉምቲ"),
        }
        approval_labels = {
            "en": "Approval required before any future action; Saba did not execute it.",
            "am": "ለወደፊት እርምጃ ግልጽ ፈቃድ ያስፈልጋል፤ Saba እርምጃውን አልፈጸመም።",
            "om": "Tarkaanfii fuulduraatiif eeyyamni ifa ta'e barbaachisa; Saba hin raawwanne.",
            "ti": "ንዝቕጽል ስጉምቲ ግልጺ ፍቓድ የድሊ፤ Saba ኣይፈጸሞን።",
        }
        risk_label, tools_label, next_label = labels.get(language, labels["en"])
        risk = risk_names.get(result.risk_level, risk_names["low"]).get(language, risk_names.get(result.risk_level, risk_names["low"])["en"])
        tool_names = {
            "service_catalog": "service catalog",
            "provider_directory": "provider directory",
            "gemini_google_search": "Gemini Google Search",
            "searchapi_google": "SearchAPI Google Search",
        }
        tools = ", ".join(tool_names.get(tool, tool) for tool in result.tools_used) or "none"
        parts = [f"{risk_label}: {risk}", f"{tools_label}: {tools}", result.answer]
        call_messages = {
            "started": {
                "en": f"Saba is calling {result.call_contact_name} via Vapi now. I’ll send you the available result when the call ends.",
                "am": f"Saba በVapi አሁን {result.call_contact_name}ን እየደወለ ነው። ጥሪው ሲያበቃ የተገኘውን ውጤት እልክልዎታለሁ።",
                "om": f"Saba amma Vapi fayyadamuun {result.call_contact_name} bilbilaa jira. Bilbilichi yeroo xumuramu bu'aa siif erga.",
                "ti": f"Saba ብVapi ሕጂ {result.call_contact_name} ይድውሎ ኣሎ። ጻውዒቱ ምስ ወደአ ውጽኢቱ ክልእከልኩም እየ።",
            },
            "not_configured": {"en": "Saba found that a call may help, but Vapi calling is not enabled or fully configured.", "am": "ጥሪ ሊረዳ እንደሚችል Saba አግኝቷል፤ ግን Vapi አልተነቃም ወይም ሙሉ በሙሉ አልተዋቀረም።", "om": "Saba bilbiluun gargaaruu akka danda'u arge, garuu Vapi hin qophoofne.", "ti": "Saba ጻውዒት ክሕግዝ ከምዝኽእል ረኺቡ፤ Vapi ግን ኣይተዳለወን።"},
            "no_contact": {"en": "I could not find a matching verified public office contact, so I did not call.", "am": "ተዛማጅ የተረጋገጠ የሕዝብ ቢሮ ስልክ አላገኘሁም፤ ስለዚህ አልደወልኩም።", "om": "Lakkoofsa waajjira mootummaa mirkanaa'e hin arganne; kanaaf hin bilbille.", "ti": "ዝተረጋገጸ ተዛማዲ ቁጽሪ ቤት ጽሕፈት ኣይረኸብኩን፤ ስለዚ ኣይደወልኩን።"},
            "daily_limit": {"en": "The daily Vapi call limit has been reached; Saba did not place another call.", "am": "የዕለቱ የVapi ጥሪ ገደብ ደርሷል፤ Saba ሌላ ጥሪ አላደረገም።", "om": "Daangaan bilbilaa Vapi guyyaa kanaa gaheera; Saba bilbila biraa hin goone.", "ti": "ናይ ሎሚ መደብ ጻውዒት Vapi በጺሑ፤ Saba ተወሳኺ ጻውዒት ኣይገበረን።"},
            "disabled": {"en": "A call could help, but outbound calling is disabled. Set VAPI_AUTO_CALL_ENABLED=true after reviewing the Vapi setup.", "am": "ጥሪ ሊረዳ ይችላል፤ ግን ውጭ ጥሪ ተዘግቷል። የVapi ዝግጅትን ከገመገሙ በኋላ VAPI_AUTO_CALL_ENABLED=true ያድርጉ።", "om": "Bilbiluun gargaaruu danda'a, garuu bilbilli alaa cufameera. Qophii Vapi ilaalii booda qindeessi.", "ti": "ጻውዒት ክሕግዝ ይኽእል፤ ግን ወጻኢ ጻውዒት ተዓጽዩ ኣሎ። ቅድሚ ምኽፋት ምድላው Vapi ገምግሙ።"},
            "approval_required": {"en": "This request needs your explicit approval before any call; Saba did not call.", "am": "ይህ ጥያቄ ከመደወል በፊት ግልጽ ፈቃድዎን ይፈልጋል፤ Saba አልደወለም።", "om": "Gaaffiin kun bilbiluun dura eeyyama kee ifaa barbaada; Saba hin bilbille.", "ti": "እዚ ሕቶ ቅድሚ ምድዋል ግልጺ ፍቓድኩም የድሊ፤ Saba ኣይደወለን።"},
            "failed": {"en": "Vapi could not start the call. Check its API key, assistant, phone number, and destination permissions.", "am": "Vapi ጥሪውን ማስጀመር አልቻለም። የAPI ቁልፉን፣ assistant፣ ስልክ ቁጥሩን እና የመዳረሻ ፈቃዱን ያረጋግጡ።", "om": "Vapi bilbila jalqabuu hin dandeenye. API key, assistant, lakkoofsa bilbilaa fi hayyama biyya ilaali.", "ti": "Vapi ነቲ ጻውዒት ክጅምሮ ኣይከኣለን። API key፣ assistant፣ ቁጽሪ ስልኪን ፍቓድ መዳረሻን መርምሩ።"},
        }
        if result.call_status in call_messages:
            parts.append(call_messages[result.call_status].get(language, call_messages[result.call_status]["en"]))
        if result.requires_approval:
            parts.insert(1, approval_labels.get(language, approval_labels["en"]))
        if result.next_step:
            parts.append(f"{next_label}: {result.next_step}")
        if result.process_summary:
            parts.append(result.process_summary)
        return "\n\n".join(parts)

    def _set_stage(self, user_id: int, stage: str) -> None:
        self._stages[user_id] = stage
        if self._profile_store:
            self._profile_store.save_stage(user_id, stage)

    def _current_stage(self, user_id: int) -> str:
        stage = self._stages.get(user_id)
        if stage:
            return stage
        if self._profile_store:
            stage = self._profile_store.get_stage(user_id)
            if stage:
                return stage
            saved = self._profile_store.get(user_id)
            if saved:
                if saved["personal_data_consent"]:
                    return next(
                        (field for field in ("name", "age", "birth_year", "location") if saved.get(field) is None),
                        "service",
                    )
                return "method"
        return "language"

    def _language_buttons(self) -> tuple[tuple[str, ...], ...]:
        return ((LANGUAGES["am"], LANGUAGES["om"]), (LANGUAGES["ti"], LANGUAGES["en"]))

    def _key_for_choice(self, message: str, key: str) -> str | None:
        cleaned = message.strip().casefold()
        for language in LANGUAGES:
            if cleaned == TEXT[key][language].casefold():
                return language
        return None

    @staticmethod
    def _stage_prompt_key(stage: str) -> str | None:
        return {
            "name": "ask_name",
            "age": "ask_age",
            "birth_year": "ask_birth_year",
            "location": "ask_location",
            "manual_consent": "privacy_consent",
            "service": "ask_service",
        }.get(stage)

    def _back_button(self, language: str) -> tuple[tuple[str, ...], ...]:
        return ((TEXT["back"][language],),)

    def _is_back(self, message: str) -> bool:
        cleaned = message.strip().casefold()
        return cleaned == "/back" or any(cleaned == TEXT["back"][code].casefold() for code in LANGUAGES)

    def requires_agent(self, user_id: int, message: str) -> bool:
        return self._current_stage(user_id) == "service" and not message.startswith("/") and not self._is_back(message)

    def language_for(self, user_id: int) -> str:
        return self._languages.get(user_id, "en")

    def progress_label(self, user_id: int, stage: str) -> str:
        language = self.language_for(user_id)
        return PROGRESS.get(stage, PROGRESS["search"]).get(language, PROGRESS["search"]["en"])

    async def handle(
        self,
        user_id: int,
        text: str,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> OutgoingMessage:
        message = text.strip()
        lowered = message.casefold()
        if user_id not in self._languages and self._profile_store:
            saved_profile = self._profile_store.get(user_id)
            if saved_profile:
                self._languages[user_id] = str(saved_profile["language"] or "en")

        if lowered == "/tasks":
            language = self._languages.get(user_id, "en")
            if not self._task_store:
                return OutgoingMessage(TASK_TEXT["usage"].get(language, TASK_TEXT["usage"]["en"]))
            tasks = self._task_store.list_open(user_id)
            if not tasks:
                return OutgoingMessage(TASK_TEXT["none"].get(language, TASK_TEXT["none"]["en"]))
            return OutgoingMessage("\n".join(f"{t['task_id']} · {t['status']} · {t['goal']}" for t in tasks))

        if lowered == "/task" or lowered.startswith("/task "):
            language = self._languages.get(user_id, "en")
            args = message.split(maxsplit=2)
            if len(args) >= 3 and args[1].casefold() == "create":
                goal = args[2].strip()
                if not self._task_store or len(goal) < 4 or len(goal) > 300 or re.search(r"\d{8,}", goal):
                    return OutgoingMessage(TASK_TEXT["usage"].get(language, TASK_TEXT["usage"]["en"]))
                task = self._task_store.create(user_id, "telegram", goal, goal)
                if self._audit_log:
                    self._audit_log.record(user_id, "goal_created", True)
                return OutgoingMessage(f"{TASK_TEXT['created'].get(language, TASK_TEXT['created']['en'])}: {task['task_id']}\nStatus: pending\nNext: confirm the service and requirements before acting.")
            if len(args) == 3 and args[1].casefold() in {"pause", "resume"}:
                if not self._task_store:
                    return OutgoingMessage(TASK_TEXT["usage"].get(language, TASK_TEXT["usage"]["en"]))
                status = "paused" if args[1].casefold() == "pause" else "pending"
                task = self._task_store.set_status(user_id, args[2], status)
                if not task:
                    return OutgoingMessage(TASK_TEXT["not_found"].get(language, TASK_TEXT["not_found"]["en"]))
                label = "paused" if status == "paused" else "resumed"
                return OutgoingMessage(TASK_TEXT[label].get(language, TASK_TEXT[label]["en"]))
            if len(args) == 2 and self._task_store:
                task = self._task_store.get(user_id, args[1])
                if task:
                    return OutgoingMessage(f"{task['goal']}\nStatus: {task['status']}\nCurrent step: {task.get('current_step') or 'not set'}\nNext action: {task.get('next_action') or 'not set'}\nTask ID: {task['task_id']}")
            return OutgoingMessage(TASK_TEXT["usage"].get(language, TASK_TEXT["usage"]["en"]))

        if lowered == "/language":
            self._set_stage(user_id, "language")
            language = self._languages.get(user_id, "en")
            return OutgoingMessage(self._say("language_prompt", language), self._language_buttons())

        if lowered == "/start":
            saved = self._profile_store.get(user_id) if self._profile_store else None
            if saved:
                language = str(saved["language"] or "en")
                self._languages[user_id] = language
                if saved["personal_data_consent"]:
                    self._profiles[user_id] = {
                        key: str(saved[key] or "")
                        for key in ("name", "age", "birth_year", "location")
                    }
                    stage = self._current_stage(user_id)
                    if stage in {"language", "method", "manual_consent"}:
                        stage = next(
                            (
                                field
                                for field in ("name", "age", "birth_year", "location")
                                if saved.get(field) is None
                            ),
                            "service",
                        )
                    self._set_stage(user_id, stage)
                    self._audit_log.record(user_id, "saved_profile_reused", True)
                    prompt_key = self._stage_prompt_key(stage)
                    prompt = self._say(prompt_key, language) if prompt_key else self._say("ask_service", language)
                    return OutgoingMessage(prompt, (("/language",), ("/privacy",), self._back_button(language)[0]))
                self._set_stage(user_id, "method")
                return OutgoingMessage(self._say("method_prompt", language), ((TEXT["fayda"][language],), (TEXT["manual"][language],), ("/privacy",)))
            self._profiles.pop(user_id, None)
            self._languages.pop(user_id, None)
            self._set_stage(user_id, "language")
            self._audit_log.record(user_id, "language_menu_shown", False)
            return OutgoingMessage(self._say("language_prompt", "en"), self._language_buttons())

        if lowered in {"/privacy", "/security"}:
            language = self._languages.get(user_id, "en")
            return OutgoingMessage(self._say("privacy", language), (("/forget",),))

        if lowered == "/providers" or lowered.startswith("/providers "):
            language = self._languages.get(user_id, "en")
            query = message.partition(" ")[2].strip()
            if self._provider_directory:
                return OutgoingMessage(self._provider_directory.render(query, language), (("/services",), ("/privacy",)))
            return OutgoingMessage(self._say("ask_service", language))

        if lowered == "/forget":
            language = self._languages.get(user_id, "en")
            self._profiles.pop(user_id, None)
            if self._profile_store:
                self._profile_store.forget_personal_data(user_id)
            self._set_stage(user_id, "method")
            self._audit_log.record(user_id, "personal_profile_forgotten", True)
            return OutgoingMessage(self._say("forget", language) + "\n" + self._say("method_prompt", language), ((TEXT["fayda"][language],), (TEXT["manual"][language],), ("/privacy",)))

        if self._is_back(message):
            current = self._current_stage(user_id)
            previous = {
                "method": "language",
                "manual_consent": "method",
                "name": "method",
                "age": "name",
                "birth_year": "age",
                "location": "birth_year",
                "service": "location",
            }.get(current, "language")
            self._set_stage(user_id, previous)
            language = self._languages.get(user_id, "en")
            if previous == "language":
                return OutgoingMessage(self._say("language_prompt", language), self._language_buttons())
            if previous == "method":
                return OutgoingMessage(self._say("method_prompt", language), ((TEXT["fayda"][language],), (TEXT["manual"][language],), ("/privacy",), self._back_button(language)[0]))
            key = self._stage_prompt_key(previous)
            buttons = ((TEXT["yes"][language],), (TEXT["no"][language],), self._back_button(language)[0]) if previous == "manual_consent" else self._back_button(language)
            return OutgoingMessage(self._say(key, language) if key else self._say("ask_service", language), buttons)

        stage = self._current_stage(user_id)
        if stage == "language":
            language = next((code for code, label in LANGUAGES.items() if message.casefold() == label.casefold()), None)
            if language is None:
                return OutgoingMessage(self._say("language_prompt", "en"), self._language_buttons())
            self._languages[user_id] = language
            if self._profile_store:
                self._profile_store.save_language(user_id, language)
            self._set_stage(user_id, "method")
            self._audit_log.record(user_id, "language_selected", False)
            return OutgoingMessage(
                self._say("method_prompt", language),
                ((TEXT["fayda"][language],), (TEXT["manual"][language],), ("/privacy",), self._back_button(language)[0]),
            )

        language = self._languages.get(user_id, "en")
        if stage == "method":
            picked_language = next(
                (code for code, label in LANGUAGES.items() if message.casefold() == label.casefold()),
                None,
            )
            if picked_language:
                self._languages[user_id] = picked_language
                if self._profile_store:
                    self._profile_store.save_language(user_id, picked_language)
                language = picked_language
                return OutgoingMessage(self._say("method_prompt", language), ((TEXT["fayda"][language],), (TEXT["manual"][language],), ("/privacy",), ("/language",), self._back_button(language)[0]))
            if self._key_for_choice(message, "fayda"):
                return OutgoingMessage(
                    self._say("fayda_unavailable", language),
                    ((TEXT["manual"][language],), ("/language",), self._back_button(language)[0]),
                )
            if self._key_for_choice(message, "manual"):
                saved = self._profile_store.get(user_id) if self._profile_store else None
                if saved and saved["personal_data_consent"]:
                    self._profiles[user_id] = {
                        key: str(saved[key] or "")
                        for key in ("name", "age", "birth_year", "location")
                    }
                    self._set_stage(user_id, "service")
                    return OutgoingMessage(self._say("ask_service", language), (("/privacy",), self._back_button(language)[0]))
                self._set_stage(user_id, "manual_consent")
                self._audit_log.record(user_id, "manual_data_consent_requested", False)
                return OutgoingMessage(
                    self._say("privacy_consent", language),
                    ((TEXT["yes"][language],), (TEXT["no"][language],), self._back_button(language)[0]),
                )
            return OutgoingMessage(self._say("method_prompt", language), ((TEXT["fayda"][language],), (TEXT["manual"][language],), ("/language",), self._back_button(language)[0]))

        if stage == "manual_consent":
            if self._key_for_choice(message, "no"):
                self._set_stage(user_id, "method")
                return OutgoingMessage(self._say("no_consent", language), ((TEXT["manual"][language],), self._back_button(language)[0]))
            if not self._key_for_choice(message, "yes"):
                return OutgoingMessage(self._say("privacy_consent", language), ((TEXT["yes"][language],), (TEXT["no"][language],), self._back_button(language)[0]))
            self._profiles[user_id] = {}
            if self._profile_store:
                self._profile_store.grant_personal_data_consent(user_id, language)
            self._audit_log.record(user_id, "manual_data_consent", True)
            self._set_stage(user_id, "name")
            return OutgoingMessage(self._say("ask_name", language), self._back_button(language))

        if stage in {"name", "age", "birth_year", "location"}:
            stale_language = any(message.casefold() == label.casefold() for label in LANGUAGES.values())
            stale_choice = any(self._key_for_choice(message, key) for key in ("yes", "no", "fayda", "manual"))
            if stale_language or stale_choice:
                prompt_key = self._stage_prompt_key(stage)
                return OutgoingMessage(self._say(prompt_key, language), self._back_button(language))
            value = message.strip()
            if value.casefold() == "skip":
                value = ""
            if stage in {"name", "location"} and re.search(r"\d{8,}", value):
                return OutgoingMessage(self._say("id_warning", language), self._back_button(language))
            if stage == "age" and value and (not value.isdigit() or not 0 <= int(value) <= 120):
                return OutgoingMessage(self._say("bad_age", language), self._back_button(language))
            if stage == "birth_year" and value:
                if not re.fullmatch(r"\d{4}", value) or not 1900 <= int(value) <= date.today().year:
                    return OutgoingMessage(self._say("bad_year", language), self._back_button(language))
            self._profiles.setdefault(user_id, {})[stage] = value
            if self._profile_store:
                self._profile_store.save_personal_fields(user_id, language, self._profiles[user_id])
            next_stage = {"name": "age", "age": "birth_year", "birth_year": "location", "location": "service"}[stage]
            self._set_stage(user_id, next_stage)
            if next_stage == "service":
                return OutgoingMessage(self._say("manual_done", language) + "\n" + self._say("ask_service", language), (("/privacy",), self._back_button(language)[0]))
            return OutgoingMessage(self._say({"age": "ask_age", "birth_year": "ask_birth_year", "location": "ask_location"}.get(next_stage, "ask_name"), language), self._back_button(language))

        if stage == "service":
            selected_language = next(
                (code for code, label in LANGUAGES.items() if message.casefold() == label.casefold()),
                None,
            )
            service_buttons = (("/language",), ("/privacy",), self._back_button(language)[0])
            if selected_language:
                self._languages[user_id] = selected_language
                language = selected_language
                if self._profile_store:
                    self._profile_store.save_language(user_id, language)
                return OutgoingMessage(
                    self._say("ask_service", language),
                    (("/language",), ("/privacy",), self._back_button(language)[0]),
                )
            if self._key_for_choice(message, "fayda"):
                return OutgoingMessage(self._say("fayda_unavailable", language), service_buttons)
            if self._key_for_choice(message, "manual"):
                return OutgoingMessage(self._say("ask_service", language), service_buttons)
            if self._key_for_choice(message, "yes") or self._key_for_choice(message, "no"):
                return OutgoingMessage(self._say("ask_service", language), service_buttons)
            if lowered in {"/services", "services"}:
                services = self._catalog.all()
                if not services:
                    if self._provider_directory:
                        return OutgoingMessage(self._provider_directory.render("", language), (("/providers",), ("/privacy",)))
                    return OutgoingMessage(self._say("ask_service", language))
                return OutgoingMessage(
                    "\n".join(service.name_am for service in services[:10]),
                    tuple((service.name_am,) for service in services[:10]),
                )
            if not self._policy.can_run_automatically("web_search"):
                return OutgoingMessage(self._say("agent_error", language))
            if re.search(r"\d{8,}", message):
                return OutgoingMessage(self._say("id_warning", language))
            if self._agent is None:
                self._audit_log.record(user_id, "agent_not_configured", True)
                return OutgoingMessage(self._say("agent_needed", language))
            self._audit_log.record(user_id, "official_web_search", True)
            try:
                result = await self._agent.answer(message, language, on_progress=on_progress, user_id=user_id)
            except GeminiSearchError as exc:
                self._audit_log.record(user_id, f"gemini_search_failed:{exc.reason}", False)
                localized_failure = GEMINI_FAILURES.get(
                    exc.reason,
                    GEMINI_FAILURES.get(
                        f"searchapi_{exc.reason.removeprefix('searchapi_')}",
                        GEMINI_FAILURES["unavailable"],
                    ),
                )
                return OutgoingMessage(localized_failure.get(language, localized_failure["en"]))
            except Exception as exc:
                # Keep user text and secrets out of logs; report only the error class.
                import logging
                logging.getLogger(__name__).error("Agent run failed (%s)", type(exc).__name__)
                return OutgoingMessage(self._say("agent_error", language))
            self._audit_log.record(user_id, f"research_risk:{result.risk_level}", True)
            return OutgoingMessage(
                self._format_agent_result(result, language),
                (("/services",), ("/privacy",), self._back_button(language)[0]),
            )

        return OutgoingMessage(self._say("language_prompt", "en"), self._language_buttons())
