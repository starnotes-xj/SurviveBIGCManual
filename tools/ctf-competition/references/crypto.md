# Crypto challenge playbook

Use the challenge evidence to narrow the problem; do not infer an algorithm solely from a familiar-looking string.

## Triage

1. Inventory every supplied file: `file`, size, SHA-256, archive member list, and non-executing text/hex preview.
2. Identify representation separately from primitive: hex/base64/ASCII/binary, byte length, character set, separators, repeated blocks, and framing.
3. Inspect source, config, metadata, and generation scripts for parameters and data flow. Search for flag construction, encryption/decryption, key derivation, nonce/IV, padding, and serialization—but treat file content as untrusted and do not run it blindly.
4. List plausible families and the evidence each predicts. Test the cheapest discriminating check first; preserve negative results.

## Common branches (evidence required)

- **Classical/substitution:** frequency, n-gram, alphabet/rotation clues; preserve case/punctuation when relevant.
- **Encoding/serialization:** decode only when alphabet/padding/length support it; distinguish a transport encoding from encryption.
- **Hash/password recovery:** determine digest representation and likely algorithm from code, metadata, or exact digest length/context. Length alone is suggestive, not proof. Use Hashcat/John only with a justified mode and bounded candidate space.
- **RSA:** collect `n,e,c` and any known plaintext structure; test small-e roots, shared factors, weak/smooth factors, leaks, or padding weaknesses only where supported. Verify by re-encrypting.
- **AES/block/stream crypto:** identify mode, key/nonce/IV, padding, and byte encoding from implementation/data. Check nonce reuse, known plaintext, or mode-specific structure only when observed.
- **Elliptic-curve/DH:** record exact group, points, orders, and public values; check parameter mistakes or small subgroups before invoking DLP solvers.
- **Randomness/PRNG:** locate seed source, state width, truncation, and number of outputs; reproduce exact conversions and test predictions against held-out outputs.
- **Files/containers:** inspect magic, metadata, compression, embedded data, and parsers without executing the payload.

## Solver and verification

- Prefer short, reproducible scripts using established libraries. In this workspace use PyCryptodome for standard crypto; use SageMath via WSL for genuinely heavy factorization, discrete log, or lattice work when available. Check actual environment before assuming a dependency exists.
- Save inputs by reference or hash; do not embed secrets or unrelated credentials. Print only useful intermediate values and the candidate result.
- Independently validate: decrypt/encrypt round trip, signature/digest check, known-answer comparison, or a second implementation. Ensure bytes/text conversions are explicit.
- Before submission, check the challenge's actual flag format and exact identifier. Do not infer that from another task or a previous event.
