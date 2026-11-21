"""Build the A3 demo video from REAL material of run 44902438357 (issue #3 -> PR #11)."""
import json, re, subprocess, textwrap, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

V = Path(__file__).parent
D, SH, OUT = V / "data", V / "shots", V / "out"
OUT.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1920, 1080
F = "/usr/share/fonts/truetype/dejavu/"
font = lambda n, s: ImageFont.truetype(F + n, s)
TITLE, BODY, MONO, SMALL = font("DejaVuSans-Bold.ttf", 46), font("DejaVuSans.ttf", 30), font("DejaVuSansMono.ttf", 22), font("DejaVuSans.ttf", 24)
BG, ACC, FG = (250, 250, 252), (219, 223, 230), (30, 30, 30)  # light header -> dark after the dark-mode filter
RUN = "github.com/Ohshit-ak/tinydb/actions/runs/44902438357"


def frame(title, footer=""):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 100], fill=ACC)
    d.text((50, 25), title, font=TITLE, fill=(15, 15, 20))
    if footer:
        d.rectangle([0, H - 56, W, H], fill=(235, 236, 240))
        d.text((50, H - 44), footer, font=SMALL, fill=(80, 80, 80))
    return im, d


def shot(title, img, footer=""):
    im, d = frame(title, footer)
    s = Image.open(SH / img).convert("RGB")
    box_w, box_h = W - 100, H - 100 - 56 - 40
    s.thumbnail((box_w, box_h))
    x, y = (W - s.width) // 2, 120
    d.rectangle([x - 2, y - 2, x + s.width + 1, y + s.height + 1], outline=(200, 200, 200), width=2)
    im.paste(s, (x, y))
    return im


def text(title, lines, footer="", mono=True, size=None):
    im, d = frame(title, footer)
    f = font("DejaVuSansMono.ttf", size) if (mono and size) else (MONO if mono else BODY)
    y = 130
    for ln in lines:
        color = FG
        if ln.startswith("==>"):
            color = (0, 110, 50)
        elif ln.startswith("[llm]"):
            color = (170, 90, 0)
        elif ln.startswith("#"):
            color, ln = (20, 60, 140), ln.lstrip("# ")
        d.text((60, y), ln, font=f, fill=color)
        y += int(f.size * 1.45)
        if y > H - 90:
            break
    return im


def clip(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


log = [clip(l.rstrip(), 118) for l in (D / "agents.log").read_text().splitlines()]
keep = [l for l in log if l.startswith("==>") or "submit(" in l or "[llm]" in l or "run_tests" in l or "replace_in_file" in l or "check_build" in l]
spec = (D / "autose-issue-3-r1/spec.md").read_text()
acs = re.search(r"## 5\. Acceptance criteria(.*?)## 6", spec, re.S).group(1).strip().splitlines()
design = (D / "autose-issue-3-r1/design.md").read_text()
files = re.search(r"## Files to change(.*?)## Public", design, re.S).group(1).strip().splitlines()
report = (D / "autose-issue-3-r1/test_report.md").read_text()
cov = re.search(r"## Acceptance-criterion coverage(.*?)## Check", report, re.S).group(1).strip().splitlines()
rev = (D / "review-3-r1-independent/review.md").read_text()
rv = json.loads((D / "review-3-r1-independent/verdict.json").read_text())

slides = [
    (text("AutoSE — issue in, reviewed pull request out", [
        "", "# Automated Software Engineering — Assignment 3 (roll no. 2024111004)", "",
        "One complete, real run on our tinydb fork:",
        "  issue #3  ->  6 stages  ->  PR #11  ->  independent review  ->  human decides", "",
        f"Run: {RUN}", "PR:  github.com/Ohshit-ak/tinydb/pull/11", "",
        "Models: Gemini free tier (workers 3.5-flash-lite pool, reviewer 3.1-flash-lite pool)"], mono=False),
     "This is AutoSE, a GitHub Actions workflow in which agents turn a GitHub issue into a tested and "
     "independently reviewed pull request. I will walk through one complete real run on our tinydb fork, "
     "from the issue to the posted review."),
    (shot("1. The issue (written like a real user)", "issue.png", "github.com/Ohshit-ak/tinydb/issues/3"),
     "Issue three asks for count to work without a query. A maintainer starts the workflow by adding the "
     "autose label, or with a slash autose comment. Only users with write access can start a run. The gate "
     "job checks the sender's permission and never puts issue text into a shell command."),
    (shot("2. Architecture: who knows what, who may do what", "arch.png", "architecture/views/component.md · ADR-001, 005, 008"),
     "Five agents, each a separate model session with its own prompt and tools: analyst, architect, builder, "
     "tester and reviewer. A deterministic controller makes every pass or fail decision. The jobs are split by "
     "permission. The agents job has the model key but a read only token. Release has the write token but "
     "never runs a model."),
    (shot("3. The real run: job graph", "run.png", RUN),
     "This is the real run. Gate, agents, release, continuous integration, review and post review. The agents "
     "job took about thirty two minutes on free tier models. The release job was re-run once, which I will "
     "explain in a moment. Every job finished green."),
    (text("4. Inside the agents job: the Controller's state machine", keep, "agents job log (real, abridged) · ADR-002, ADR-007"),
     "Inside the agents job, the controller drives the stages. Each green arrow is a check decided by code: a "
     "spec lint plus an LLM testability judge, an abstract syntax tree check of the design, a sandboxed build "
     "check, and the full test suite. The orange line shows the worker moving to the next free model when one "
     "model's daily quota ran out."),
    (text("5. Stage 1 artifact: spec.md (Analyst, reusing the A1 skill)", [clip(a, 120) for a in acs if a.strip()][:16], "artifact autose-issue-3-r1/spec.md", size=21),
     "The analyst reuses our assignment one requirements skill in unattended mode. It writes acceptance "
     "criteria in given, when, then form, each with a concrete observable result, so that every criterion is "
     "testable."),
    (text("6. Stage 2 artifact: design.md (Architect, using ARCHITECTURE.md)", files + ["", "Check: every path exists or is NEW; every function found by AST; every AC mapped."], "artifact autose-issue-3-r1/design.md"),
     "The architect reads our assignment two architecture document and names the exact files and functions to "
     "change. The controller verifies each name against the real code before any code is written."),
    (text("7. Stage 3 + 4: tests from the spec, not from the code", [clip(c, 120) for c in cov] + ["", "New tests: 4 passed · Full suite: 231 passed"], "artifact autose-issue-3-r1/test_report.md", size=19),
     "The builder changed table dot py. The tester wrote one test per acceptance criterion while reading only "
     "the old code, so the tests come from the spec and not from the implementation. Red on base shows that "
     "the two new-behaviour tests failed on the old code. All new and existing tests pass."),
    (text("8. A lesson from this run (ADR-012)", [
        "# First release attempt: push rejected.",
        "main moved during the 30-minute run; the bot's branch carried an older",
        ".github/workflows file, and GITHUB_TOKEN may never push workflow changes.", "",
        "# Fix: release re-applies the bot's commit onto the current main,",
        "re-checks the path allowlist, then pushes. CI runs on the rebased head.", "",
        "# Recovery: re-ran only the failed release job.",
        "Per-run artifacts + git bundle meant stages 1-4 were not repeated."], mono=False),
     "The first release attempt failed. Main had moved during the run, and GitHub refuses token pushes that "
     "change workflow files. We recorded this in a new decision record: release now re-applies the bot's "
     "commit onto the current main. Because every stage keeps its artifacts, only the release job had to be "
     "re-run."),
    (shot("9. Stage 5: the pull request, with CI on the PR head", "files.png", "github.com/Ohshit-ak/tinydb/pull/11/files"),
     "Release opened pull request eleven with the code change and the new test file. Continuous integration "
     "ran on the pull request head and posted its result as a commit status."),
    (text("10. Stage 6: the independent review (separate job, model, key)", ["# Verdict: " + rv["verdict"] + " (round 1)", ""] + textwrap.wrap(rv.get("summary", ""), 100) + [""] +
          [clip(f"{r['id']}: {r['text']}  [{r['status']}]", 125) for r in rv.get("requirements", [])] +
          ["", f"Evidence guard: ran_tests = {rv.get('ran_tests')} · model {rv.get('model')} · posted as COMMENT (never APPROVE)"],
          "artifact review-3-r1-independent · ADR-007, ADR-008", mono=False),
     "The reviewer runs in its own job, with a different model, its own key and a read only token. It saw only "
     "the issue, the diff and the repository. It wrote its own requirements from the issue, ran the test "
     "suite, and approved. An approval without a real test run in the harness log is rejected automatically. "
     "The review is posted as a comment, never as an approval."),
    (text("11. Result: a human decides", [
        "# Labels: autose:reviewer-approved, autose:ready-for-human", "",
        "# Hidden acceptance tests (kept outside the fork): 4 / 4 pass on PR #11", "",
        "# Cost of this run: 27 worker calls (178k tokens) + 10 reviewer calls", "",
        "# The workflow never merges. The maintainer merges or closes.", "",
        "Design, ADRs and all runs: github.com/Ohshit-ak/autose-a3"], mono=False),
     "Our hidden acceptance tests, kept outside the repository, pass four out of four on this pull request. "
     "The pull request is labelled ready for human. The workflow never merges. A person makes the final "
     "decision. Thank you."),
]

segs = []
for i, (img, narration) in enumerate(slides, 1):
    png, wav, mp4 = OUT / f"s{i:02d}.png", OUT / f"s{i:02d}.wav", OUT / f"s{i:02d}.mp4"
    img.save(png)
    subprocess.run([str(V.parent / "venv/bin/piper"), "-m", str(V / "voice/en_US-lessac-medium.onnx"), "-f", str(wav)],
                   input=narration.encode(), check=True, capture_output=True)
    with wave.open(str(wav)) as w:
        dur = w.getnframes() / w.getframerate() + 1.2
    subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-i", str(wav),
                    "-t", f"{dur:.2f}", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-r", "15", "-c:a", "aac", "-b:a", "128k", "-af", "apad", str(mp4)], check=True)
    segs.append((mp4, dur))
    print(f"slide {i}: {dur:.1f}s")
(OUT / "list.txt").write_text("".join(f"file '{p}'\n" for p, _ in segs))
subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(OUT / "list.txt"),
                "-c", "copy", str(OUT / "demo.mp4")], check=True)
print("total", round(sum(d for _, d in segs), 1), "s ->", OUT / "demo.mp4")

# Dark mode (applied to the rendered video):
#   ffmpeg -i demo.mp4 -vf "negate,hue=h=180" -c:a copy demo_dark.mp4
