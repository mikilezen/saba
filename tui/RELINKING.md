# Relinking OpenTUI

Saba TUI includes OpenTUI 0.5.11, an MIT-licensed terminal UI library. The package source is available from <https://www.npmjs.com/package/@opentui/core/v/0.5.11> and the [OpenTUI repository](https://github.com/anomalyco/opentui).

The release archive contains the complete corresponding Saba TUI source, including its dependency manifest and lockfile. To relink the application with a modified OpenTUI build, check out that source, point the `@opentui/core` dependency in `package.json` to the modified package, install dependencies with Bun, and rebuild with `bun run build`. The upstream package is distributed under the MIT License; its copyright and license text are included in `THIRD_PARTY_NOTICES.txt`.
