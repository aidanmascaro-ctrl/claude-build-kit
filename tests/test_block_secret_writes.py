#!/usr/bin/env python3
"""Self-check for block-secret-writes.py. Run: python3 tests/test_block_secret_writes.py

Every secret-shaped fixture is ASSEMBLED FROM FRAGMENTS rather than written as a
literal. The guard scans the content of every file being written, including this
one: a literal key here would make this file uneditable by the very tool it
tests. Concatenation keeps the on-disk bytes clean while the assembled string
still exercises the real pattern. All values are made up.

Keep it that way: if you add a fixture, split it so no complete secret-shaped
token appears on any single source line.
"""
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location(
    "guard", pathlib.Path(__file__).parent.parent / "hooks" / "block-secret-writes.py"
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

HANDOFF = "/Users/a/my-app/.claude/hub/handoffs/2026-01-01-1200.md"

# Assembled so no secret-shaped literal exists in this file. See docstring.
ANTHROPIC = "sk-" + "ant-api03-" + "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789"
STRIPE = "sk_" + "live_" + "AbC123dEf456GhI789jKl012MnO"
GH_PAT = "github_" + "pat_" + "11ABCDEFG0abcdefghijklmnopqrstuvwxyz123456"
HEX = "0123456789abcdef" * 2 + "fedcba9876543210" * 2
GOOGLE = "ya29." + "a0AbCdEfGhIjKlMnOpQrStUvWxYz012345"
PG_URL = "postgres://admin:hunter" + "2pass@db.local.test:5432/app"
PRIVKEY = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"

MUST_BLOCK = [
    (HANDOFF, f"Verify with: curl -u '{STRIPE}:' https://api.stripe.com/v1/charges"),
    (HANDOFF, f"ANTHROPIC_API_KEY={ANTHROPIC}"),
    (HANDOFF, f"token: {GH_PAT}"),
    (HANDOFF, f"API_KEY_SECRET={HEX}"),
    (HANDOFF, f"db url: {PG_URL}"),
    ("/Users/a/my-app/docs/NOTES.md", PRIVKEY),
    ("/Users/a/my-app/lib/x.ts", f'const t = "{GOOGLE}"'),
]

MUST_ALLOW = [
    (HANDOFF, 'Verify: curl -u "$STRIPE_SECRET_KEY:" https://api.stripe.com/v1/charges'),
    (HANDOFF, "Rotated STRIPE_SECRET_KEY; new value written to .env (not shown)."),
    (HANDOFF, "Old token id tok_00000000-1111-2222-3333-444444444444 revoked."),
    (HANDOFF, "commit aab3fb3f2c1e4d5a6b7c8d9e0f1a2b3c4d5e6f70: fix the date maths"),
    (HANDOFF, "ANTHROPIC_API_KEY=<redacted>"),
    (HANDOFF, "Set ANTHROPIC_API_KEY=your-key-here in .env.local"),
    # Reading a secret from the environment is the pattern we want, not a leak.
    ("/Users/a/my-app/e2e/auth.setup.ts", "const password = process.env.APP_PASSWORD;"),
    ("/Users/a/my-app/lib/x.ts", 'const apiKey = process.env.ANTHROPIC_API_KEY ?? "";'),
    ("/Users/a/my-app/scripts/y.py", 'token = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]'),
    # A credentials file is the right home for a credential.
    ("/Users/a/.secrets.env", f"export STRIPE_SECRET_KEY={STRIPE}"),
    ("/Users/a/my-app/.env.local", f"ANTHROPIC_API_KEY={ANTHROPIC}"),
]

failures = []
for path, content in MUST_BLOCK:
    if guard.SECRET_STORE.search(path) or guard.find(content) is None:
        failures.append(f"  LEAKED THROUGH: {path} :: {content[:60]}")
for path, content in MUST_ALLOW:
    if not guard.SECRET_STORE.search(path) and (hit := guard.find(content)) is not None:
        failures.append(f"  FALSE POSITIVE ({hit[0]}): {content[:60]}")

total = len(MUST_BLOCK) + len(MUST_ALLOW)
if failures:
    print(f"FAIL: {len(failures)}/{total} wrong:")
    print("\n".join(failures))
    sys.exit(1)
print(f"PASS: {len(MUST_BLOCK)} blocked, {len(MUST_ALLOW)} allowed, {total}/{total} correct")
