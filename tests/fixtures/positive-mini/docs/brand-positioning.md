# Fixture claim truth

Compact stand-in for the real claim matrix; only the IDs matter to the drift guard.

| ID | Claim under review | Status | Evidence / safe disposition |
| --- | --- | --- | --- |
| U01 | The organization is compliance-grade or certified. | unsupported | No named standard or auditor. Omit. |
| U02 | Every artifact ships SLSA, Sigstore and dual SBOMs. | unsupported | Coverage is uneven. Verify per artifact. |
| U03 | Apache-2.0 + MIT throughout the organization and media. | unsupported | Source roots only. |
| U04 | All macOS binaries are pre-notarized. | unsupported | Signing, notarization and provenance differ. |
| U05 | Chrome automation needs zero configuration and cannot select the wrong account. | unsupported | Requirements and fallbacks exist. |
| U06 | Browser automation creates uniquely trusted first-party events. | unsupported | CDP input is not event trust. |
| U07 | The proxy guarantees a hard spend ceiling or eliminates upstream rate limits. | unsupported | Pacing is not a monetary cap. |
| M01 | Speech starts under 200 ms and the tools are uniformly fast. | needs measurement | Measure audible onset separately. |
| M03 | Star counts demonstrate adoption. | needs measurement | A snapshot is not a trend. |
