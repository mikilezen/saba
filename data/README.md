# Application data resources

The JSON files in this directory provide data used by the application's
Ethiopian service integrations and discovery features.

- [`providers.json`](providers.json) lists service providers, URLs, categories,
  portal status, and search terms.
- [`services.json`](services.json) contains the supported service definitions.
- [`source_snapshots.json`](source_snapshots.json) records captured source data
  for reproducible updates.
- [`voice_contacts.json`](voice_contacts.json) contains voice-contact metadata
  used by calling workflows.

Keep these files valid JSON and preserve stable IDs when updating existing
records.
