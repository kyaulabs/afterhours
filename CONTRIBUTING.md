# Contributing

Start from `develop`. Use a conventional commit type, your username, six random hex digits from `openssl rand -hex 3`, and a short description in the branch name. Follow the repository's commit types, sign commits with GPG, and include a body explaining the change. Enable the supplied hooks with `git config core.hooksPath .github/hooks`. They require Gitleaks and commitlint with the conventional preset. [Maintainer instructions](AGENTS.md)

## Test a pack change

1. Update the pinned entry in `pack/modrinth.index.json` and edit any affected client overrides. Keep saves, launcher identities, generated caches, and third-party archives outside the source tree.
2. Run `python scripts/build.py --verify-downloads` with Python 3.11 or newer. The builder checks both upstream hashes and the byte count before creating the archive and checksum.
3. For gameplay or rendering changes, run `python scripts/smoke_prism.py "<Prism instance directory>" --size 3440x1440` on the reference PC. The Windows runner uses the instance's cached jars and Prism Java 25 JDK. It opens a temporary single-player world, samples the spawn in clear weather and rain, then closes the game. Results and startup diagnostics are in `dist/smoke.log`. To check a different display, pass its resolution.
4. Open a PR into `develop` with the supplied template. Record the build result, the settings the game actually loaded, and the outcome of the affected gameplay check.

## Cut a prerelease

Set `versionId` in the pack manifest to the next prerelease, such as `0.1.0-alpha.2`. Use a release PR from `develop` or a `release/<version>` branch into `main`. Finish the test plan, have `kyau` approve, and merge as `kyaulabs-bot`. Each promotion to `main` needs its own pack version.

After the merge, Actions builds and verifies the pack, tags the merged commit as `v<versionId>`, and publishes the archive and SHA-256 file as a GitHub prerelease. The workflow can resume a draft or verify an existing release on a rerun. It rejects a tag already assigned to a different commit.

The organization’s `BOT_TOKEN` opens a PR from `main` back into `develop`. After `kyau` approves that PR, Actions tests the proposed merge and `kyaulabs-bot` merges the reviewed commit. If the branches conflict, resolve the conflict through review before promoting another release.

## Report an issue

Include the AfterHours version, the steps that reproduce the problem, and the relevant lines from `latest.log`. For graphical problems, include the GPU, resolution, shader profile, and whether the issue persists with shaders disabled. [Open an issue](https://github.com/kyaulabs/afterhours/issues/new/choose)
