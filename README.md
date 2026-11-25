# 📘 AfterHours

<img src=".github/media/afterhours.png" alt="AfterHours" width="160" />

[https://kyaulabs.com/](https://kyaulabs.com/)

[![Contributor Covenant](https://img.shields.io/badge/contributor%20covenant-2.1-4baaaa.svg?logo=open-source-initiative&logoColor=4baaaa)](CODE_OF_CONDUCT.md) &nbsp; [![Conventional Commits](https://img.shields.io/badge/conventional%20commits-1.0.0-fe5196?style=flat&logo=conventionalcommits)](https://www.conventionalcommits.org/en/v1.0.0/) &nbsp; [![GitHub](https://img.shields.io/github/license/kyaulabs/afterhours?logo=creativecommons)](LICENSE) &nbsp; [![Gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-blue?logo=git&logoColor=seagreen&color=seagreen)](https://github.com/zricethezav/gitleaks)<br>
[![Semantic Versioning](https://img.shields.io/github/v/release/kyaulabs/afterhours?include_prereleases&logo=semver&sort=semver)](https://semver.org) &nbsp; [![Discord](https://img.shields.io/discord/88713030895943680?logo=discord&color=blue&logoColor=white)](https://discord.gg/DSvUNYm)

## About

AfterHours is a Fabric modpack for Minecraft Java 26.3. Explore Dungeons and Taverns structures with Complementary Unbound skies, biome ambience, and a visible first-person body. Crafting, combat, and progression follow vanilla survival.

## Play

Download the `.mrpack` from the latest AfterHours prerelease. In Prism Launcher, choose **Add Instance → Import**, select the file, and launch with Java 25. Prism downloads the 24 mods and the shader from their pinned Modrinth files. [GitHub releases](https://github.com/kyaulabs/afterhours/releases)

The starting profile uses Complementary Unbound High through Iris and OpenGL, with a 90 FPS cap, 16 chunks of render distance, and 8 chunks of simulation distance. On the reference PC, set the instance memory to 2048 MiB minimum and 6144 MiB maximum. Prism manages memory separately from the pack archive. [Pack settings and proposed additions](docs/vanilla-plus.md)

## Build

Run `python scripts/build.py --verify-downloads` with Python 3.11 or newer. The importable pack and its SHA-256 checksum appear in `dist/`. The manifest pins Minecraft, Fabric Loader, and each upstream download. Client settings live in `pack/client-overrides/`.

Pull requests build the archive. Merging a release into `main` creates the version tag, publishes a GitHub prerelease, and opens a back-merge PR into `develop`. [Development and release instructions](CONTRIBUTING.md)

## Attribution

KYAU Labs maintains the pack and created the AfterHours artwork. The repository license covers the pack's original files. Each mod and shader retains its upstream license.
