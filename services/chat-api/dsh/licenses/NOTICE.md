# DSH dependency evidence

- Upstream: <https://github.com/deepseek-ai/deepseek-harness>
- Reviewed source commit: `5badb15009ae1756c3afe0ae0cef1faafc290ccc`
- Reviewed source root version: `0.2.1-alpha.1`
- Approved npm release train: `0.2.1-alpha.1`
- License: MIT; vendored text is in `DEEPSEEK-HARNESS-MIT.txt`
- Upstream `THIRD_PARTY_NOTICES.md` SHA256 at the reviewed commit:
  `a8879c4c694423f0837acc8234150b286643ad3112a792448a1448ce21a12d64`

The exact direct artifacts, registry integrity values and license evidence are
recorded in `../versions.lock`. The complete installed `pnpm-lock.yaml`
dependency graph is represented by the checked-in CycloneDX inventory at
`../sbom.cdx.json`.

The npm `0.2.1-alpha.1` metadata does not publish a verified source mapping.
MOVO therefore treats the npm integrity hash as the deployable artifact
identity and the Git commit as a separate reviewed-source baseline. They must
not be claimed as a verified source/binary correspondence without new upstream
evidence.
