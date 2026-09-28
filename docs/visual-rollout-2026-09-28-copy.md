# Visual rollout — copy and claim evidence

**28/09/2026 · copy seat · home-projects w8:p8**

Coordinator: **w8:p6**. Consumers: **w8:p2, w8:pA, w8:pB**.
This report is the durable coordination surface; no sibling seat was interrupted.

## Spec

Deliver one concise organization positioning sentence, six source-supported value
propositions with non-optional caveats, a supported/unsupported/needs-measurement
claim matrix, and a provenance/usage contract separating vector identity, GPT
exploration and editorial art. Generator: **OpenAI/GPT**. No new workers.

Owned files, and no others:

- `docs/brand-positioning.md` — proposed copy, claims, pinned public evidence and usage contract.
- `docs/visual-rollout-2026-09-28-copy.md` — this spec, plan, executable check and delivery receipt.

No profile README/artwork edits, GPT image calls, publication, org-setting/CI or
security-PR changes, deployment, credentials, billing or canonical-vault edits.
An accepted copy proposition does not approve an image or authorize publication.

## Plan and tasks

Use existing public READMEs, source and releases rather than commissioning new
research or artwork. A stdlib check embedded here is sufficient for a two-file
documentation slice; no dependency, test framework or extra owned file is needed.

- [x] Read applicable workspace instructions, browser index/cookbook and actual prior GPT workflow references.
- [x] Inspect remote effects, authenticated identity, repository permission and effective main protection.
- [x] Create `../github-profile-012-brand-copy`, branch `012-brand-copy`, from fresh `origin/main`.
- [x] Pin six public main revisions; inspect READMEs, implementation, LICENSE text and non-draft release listings.
- [x] Inspect Lectrice/Proso's actual GPT path and published brand contracts; keep private source/receipts out of this public packet.
- [x] Draft positioning, six qualified propositions, 15 claim rows and a three-class asset contract.
- [x] Run offline/online acceptance and negative controls; check Markdown and diff scope.
- [ ] Commit, open a PR assigned to the verified personal account, and record exact delivery state.
- [ ] Merge only after a fresh protection check and real repository gates allow it; otherwise preserve the held proposal.

## Evidence and decisions

- Base: `64880882f235922007dd22a0cdb22c7ea5f09f83` from `origin/main`.
  The base already includes the programming gremlin (#8); its presence is not
  approval for new generated poses. Existing YL geometry and gremlin grammar
  are linked, not reinterpreted or changed.
- [brand-positioning.md](brand-positioning.md) contains full commit IDs and
  file/release URLs for all six flagships. All six repository metadata responses
  reported public visibility. Licenses were checked against the text: wa is
  Apache-2.0; the other five are MIT at those source revisions.
- Authenticated `gh api user`: `phsb5321`, Pedro Balbino, ID `30302237`.
  Repository assignees endpoint includes `phsb5321`; repository permission
  reports push/admin. Admin capability is not permission to bypass a gate.
- Main protection readback at **19:45 BRT**: `protected=false`,
  `protection.enabled=false`, required-status contexts/checks empty.
  `GET repos/yolo-labz/.github/rules/branches/main` returned `[]`.
  **Self-merge is not eligible.** No settings were changed.
- [.github#7](https://github.com/yolo-labz/.github/pull/7) was OPEN/unmerged,
  head `9bfcb26b4fb0690ce101fda9836caf9461d88012`. It remains a held proposal,
  not authority for copy or release claims; neither its branch nor security work
  was changed.
- Current profile still contains organization-wide compliance, supply-chain,
  licensing, notarization and speed statements. They are evaluated, not silently
  endorsed. Correcting the actual profile is outside this seat's two-file scope.
- Latest published GitHub Release listings were filtered for non-draft,
  non-prerelease entries: wa v2.3.0, fand v0.3.4, claude-mac-chrome v1.1.1,
  chrome-bridge v0.1.0, kokoro-speakd v0.3.0; proxy returned none. An authenticated
  draft is not a public release. No artifact signature verification was performed.

### Prior GPT workflow: what was actually checked

Read the installed gpt-image shim and its vendor generator, not only a remembered
recipe: a shared-composer lock precedes the authenticated server-fleet path;
reference uploads are checked; outputs are selected from the reply to the actual
prompt and saved as image bytes. Proso's public editorial-art wrapper documents
sidecar provenance. No tool was invoked to generate, attach, warm or change a
session, and no model identity was guessed from a UI label.

The public source contracts in `brand-positioning.md` provide the consumer-facing
record: Lectrice distinguishes its GPT-origin frozen trace from generated raster
directions; Proso's family amendment is an explicit, narrow reuse exception.
Product UI tokens remain distinct from identity. The private exploration history
was used only to avoid mistaking successful generation for acceptance; no private
vault text, prompts, chat URLs or account identifiers are copied here or sent to
a reviewer. The same discipline applies to yolo-labz, not the same bird or palette.

### Consumer handoff

- **p2:** use the three asset classes and attribution fields; keep exploratory
  images labelled. The copy seat has not inspected or approved your art.
- **pA:** use the exact proposed sentences with their qualifiers and linked
  evidence. Do not convert a source capability into an adoption or compliance badge.
- **pB:** the copy is input to a separate authorized draft, not permission to
  publish a blog/social post. Keep historical illustrations distinct from real demos.
- **p6:** owns synthesis and canonical save-state. This PR must remain held while
  main is unprotected. No message or repeated prompt was injected into any pane.

## Executable acceptance

Run from the feature worktree root. Default is offline; `BRAND_REMOTE=1` also
checks the pinned public GitHub file URLs and published release references with
read-only REST requests. The check validates scope, structure, key caveats and
source availability; **it cannot prove semantic truth, compliance, performance,
art quality or publishing authorization**. Three negative controls must fail.

```python
from pathlib import Path
import base64
import concurrent.futures
import json
import os
import re
import subprocess

base = "64880882f235922007dd22a0cdb22c7ea5f09f83"
paths = {"docs/brand-positioning.md", "docs/visual-rollout-2026-09-28-copy.md"}
text = Path("docs/brand-positioning.md").read_text()
projects = ("wa", "fand", "anthropic-throttle-proxy", "claude-mac-chrome",
            "chrome-bridge", "kokoro-speakd")
limits = ("unofficial", "forced minimum or auto", "off", "macOS only",
          "chrome.debugger/CDP", "Queued is not audible")
policy = {**{f"S{i:02}": "supported" for i in range(1, 4)},
          **{f"U{i:02}": "unsupported" for i in range(1, 9)},
          **{f"M{i:02}": "needs measurement" for i in range(1, 5)}}

def validate(s):
    rows = re.findall(r"^\| \[([^]]+)\]\[([^]]+)\] \| ([^|]+) \| (.+) \|$", s, re.M)
    assert tuple(r[0] for r in rows) == projects, "six scoped propositions required"
    headline = re.search(r"^> (.+)$", s, re.M).group(1)
    copy = headline + " ".join(r[2] for r in rows)
    assert not re.search(r"compliance|SLSA|Sigstore|sub-200|guarantee|zero depend", copy, re.I)
    for row, limit in zip(rows, limits):
        assert limit in row[3], f"missing caveat: {row[0]}"
    claims = re.findall(r"^\| ([SUM]\d{2}) \| [^|]+ \| ([^|]+) \|", s, re.M)
    assert len(claims) == len(policy) and dict(claims) == policy, "claim status drift"
    refs = dict(re.findall(r"^\[([^]]+)\]: (https://\S+)$", s, re.M))
    used = re.findall(r"\[[^]\n]+\]\[([^]]+)\]", s)
    assert set(used) == set(refs), "missing or unused evidence reference"
    assert len(refs) == 31
    for url in refs.values():
        if "/blob/" in url:
            assert re.search(r"/blob/[0-9a-f]{40}/", url), "unpinned source"
    for term in ("exploration", "Editorial art", "not a new copyright license"):
        assert term in s, f"asset usage boundary missing: {term}"
    assert Path("docs/visual-rollout-2026-09-28-copy.md").is_file()
    return refs

refs = validate(text)
for old, new in (("forced minimum or auto", "unlimited RPM"),
                 ("| unsupported |", "| supported |"),
                 ("Automate personal WhatsApp", "Guarantee safe WhatsApp")):
    assert old in text
    try:
        validate(text.replace(old, new, 1))
    except AssertionError:
        continue
    raise AssertionError(f"negative control escaped: {old}")

def git(*args):
    return subprocess.check_output(["git", *args], text=True).splitlines()

changed = set(git("diff", "--name-only", base))
changed.update(git("ls-files", "--others", "--exclude-standard"))
assert changed == paths, f"out-of-scope or missing files: {changed}"
for path in paths:
    assert all(line == line.rstrip() for line in Path(path).read_text().splitlines()), path
subprocess.run(["git", "diff", "--check", base], check=True)
print("PASS: 6 propositions, 15 claims, 31 references, 3 negative controls, 2-file scope")

if os.environ.get("BRAND_REMOTE") == "1":
    def verify(item):
        key, url = item
        owner, repo, kind, *tail = url.removeprefix("https://github.com/").split("/")
        endpoint = f"repos/{owner}/{repo}/"
        if kind == "blob":
            sha, *parts = tail
            file = "/".join(parts).split("#")[0]
            endpoint += f"contents/{file}?ref={sha}"
        else:
            assert kind == "releases" and (not tail or tail[0] == "tag"), key
            endpoint += "releases/tags/" + "/".join(tail[1:]) if tail else "releases?per_page=100"
        raw = subprocess.check_output(["gh", "api", endpoint], text=True, timeout=45)
        data = json.loads(raw)
        if kind == "blob":
            assert data["type"] == "file" and data["size"] > 0, key
            content = base64.b64decode(data["content"]).decode()
            if key.endswith("-L"):
                assert ("Apache License" if key == "WA-L" else "MIT License") in content
            span = re.search(r"#L(\d+)-L(\d+)$", url)
            if span:
                assert 1 <= int(span[1]) <= int(span[2]) <= len(content.splitlines()), key
        elif tail:
            assert not data["draft"] and not data["prerelease"] and data["published_at"], key
        else:
            assert not data, "release inventory changed; re-audit proxy claim"
        return key
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        verified = list(pool.map(verify, refs.items()))
    print(f"PASS: {len(verified)} public source/release URLs; license texts and line spans checked")
```

To execute the embedded check without creating another repository file:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('docs/visual-rollout-2026-09-28-copy.md').read_text()
exec(compile(p.split('```python\n', 1)[1].split('\n```', 1)[0], '<copy-check>', 'exec'))
PY
```

Prefix that command with `BRAND_REMOTE=1` for the online checks. Markdown parsing
can be checked with `pandoc --from=gfm --to=html docs/brand-positioning.md -o /dev/null`
and the same command for this report. No browser/artwork render applies to this
text-only slice; no render inspection or image-quality pass is claimed.

## Delivery receipt and pending gates

- Content commit / PR: pending creation after acceptance.
- Acceptance passed: 6 propositions, 15 claim rows, 31 references, all three
  negative controls rejected, and exactly the two owned files changed.
- Online acceptance passed: all 31 public file/release URLs resolve; pinned
  source line spans and the six LICENSE texts checked. The first run exposed
  a checker URL-mapping error (web `/releases/tag/` versus REST `/releases/tags/`);
  the mapping was corrected and the full online check rerun successfully.
- Both files parsed as GFM with Pandoc; the positioning quote and all four
  evidence/contract tables render structurally. `git diff --check` passed;
  private source/account/chat-path guard passed. No product tests or visual
  artwork-quality test were run or claimed.
- Advisory model review: not requested; no new reviewer worker launched.
- **[pending] Pedro/repository owner:** establish an effective protected-main
  gate through the normal authorized repository process. This seat will not
  change protection or use admin merge to land its own work.
- Profile adoption, new art approval, real render checks, external asset rights
  and any publication remain separate surface-owner decisions.
- Adjacent debt logged, not changed: this metadata repository has no root
  LICENSE or checked-in build/test configuration at the base. These two docs do
  not remedy that or make organization-wide licensing/CI claims true.
- Reversal before merge: close this proposal and leave main unchanged. After any
  later authorized squash merge: a normal PR containing `git revert <merge-sha>`.
