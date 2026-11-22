---
name: ebc-news
description: Find and summarize current Ethiopian Broadcasting Corporation (EBC) news. Use when the user asks for EBC headlines, Ethiopian news from EBC, or a current EBC report in English, Amharic, or Afaan Oromo.
---

# EBC News

Use Saba's existing `web_search` and `web_fetch` tools to find current stories on the official EBC website. EBC's official news pages are `https://www.ebc.et/english` (English), `https://www.ebc.et/` (Amharic), and `https://www.ebc.et/afanoromo` (Afaan Oromo).

No documented public EBC news API or RSS feed was found while preparing this skill. Do not invent or reverse engineer an undocumented API. Search the official site with a language-appropriate query, then fetch the specific EBC article page when more detail is needed.

Return a short summary with the headline, publication date when available, and a direct link to each EBC story. Attribute claims to EBC, especially for political or developing stories; do not present one report as independently verified fact. Summarize in your own words and link to the original instead of reproducing full articles.

Use the language the user requested. If no language is clear and the choice affects the results, ask whether they prefer English, Amharic, or Afaan Oromo. If current official results are unavailable, say so and link to the relevant EBC news page.
