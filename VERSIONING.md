# Versioning Policy

This document provides a detailed explanation of the versioning and release strategy for the ZITADEL SDKs. Its goal is to provide a clear and predictable versioning scheme.

## Versioning at a Glance

| Version Change                   | ZITADEL Compatibility                               | Type of Change                    | Example              |
|:---------------------------------|:----------------------------------------------------|:----------------------------------|:---------------------|
| **MAJOR** (e.g., 3.x -> 4.x)     | Aligned with ZITADEL Core. Requires server upgrade. | Contains breaking changes.        | `v3.5.1` -> `v4.0.0` |
| **MINOR** (e.g., 3.1 -> 3.2)     | Compatible with the same ZITADEL major version.     | New, non-breaking features added. | `v3.1.4` -> `v3.2.0` |
| **PATCH** (e.g., 3.1.0 -> 3.1.1) | Compatible with the same ZITADEL major version.     | Backwards-compatible bug fixes.   | `v3.1.0` -> `v3.1.1` |

---

## 1. Version Alignment with ZITADEL Core

Our SDKs follow a version alignment policy to ensure seamless compatibility with the ZITADEL core application. The `MAJOR` version number of the SDK directly corresponds to the `MAJOR` version of the ZITADEL instance it is designed to work with.

For example:
- Any SDK release in the `3.x.x` series is built for and tested against ZITADEL `v3`.
- When ZITADEL `v4` is released, a corresponding `4.0.0` version of the SDK will be released.

This strategy prevents compatibility issues arising from breaking changes in the ZITADEL API.

## 2. Release Cadence

The core ZITADEL project operates on a scheduled release cycle, with new major versions released quarterly. Our SDKs follow the same cadence for major releases.

- **Major Releases:** A new major version of the SDK is released in lock-step with each new major version of ZITADEL. This typically occurs at the end of each quarter.
- **Minor and Patch Releases:** Minor (`3.1.0`) and patch (`3.1.1`) releases for the SDKs may occur at any time between major releases. These will include new non-breaking features and bug fixes for the SDK itself and will always maintain compatibility with the corresponding major version of ZITADEL.

## 3. Support and Deprecation Policy

To allow users time for upgrades, we provide support for the two most recent major versions of the SDK. This is often referred to as the "N-1" policy.

- **Supported Versions:** The current major release (`N`) and the immediately preceding major release (`N-1`) are officially supported.
- **Unsupported Versions:** Any version prior to `N-1` is considered deprecated and unsupported.

For example, when SDK `v4.x.x` is released:
- `v4.x.x` becomes the current, fully supported version.
- `v3.x.x` becomes the previous (`N-1`) version and will continue to receive critical backported fixes.
- `v2.x.x` and older versions become unsupported.

We strongly encourage users to stay on a supported version to ensure they have the latest security and stability fixes.

## 4. Pre-Releases

To facilitate testing before a final release, we may publish pre-release versions of the SDK, especially in advance of a new major version. These will be marked with standard SemVer suffixes like `-alpha`, `-beta`, or `-rc` (Release Candidate).

- **Example:** `4.0.0-rc.1` would be the first release candidate for version `4.0.0`.

Pre-release versions are not intended for production use but are made available for early integration testing and feedback.

## 5. Backporting Policy

While new features are only added to the current major release line, we may backport critical fixes to a previous, still-supported major version.

- **What gets backported:** Critical security vulnerabilities and significant stability bugs.
- **What does not get backported:** New features, minor bug fixes, or performance improvements that are not critical.

This ensures that users who cannot immediately upgrade from a supported `N-1` version can still receive the most important fixes.

## 6. Changelog

All changes, including features, bug fixes, and breaking changes for every release, are documented in the `CHANGELOG.md` file at the root of the repository. We encourage you to review the changelog before upgrading.

## 7. Upgrading

When your organization plans to upgrade its ZITADEL instance across a major version (e.g., from v3 to v4), you must also update your application's dependencies to use the corresponding major version of this SDK. Attempting to use a `v3` SDK with a `v4` ZITADEL instance is unsupported and will likely result in errors.
