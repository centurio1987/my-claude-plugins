#!/usr/bin/env python3
"""Resolve and inspect the per-project diagram profile.

Why this exists: this skill keeps its state (the customized theme + the
design-system binding) *inside the skill/plugin*, not in the user's project, and
it must support many projects each with a different look. So profiles are stored
keyed by project. This script answers three questions the authoring workflow
needs before it can draw anything:

  status  - is this project already set up? (decides setup vs. author)
  path    - where do this project's profile files live? (where to read/write)
  show    - print the resolved theme + binding so the author pass can use them

It deliberately does NOT do the design-system ingestion or theme generation —
that is reasoning work for the model (see references/setup.md and
references/design-system-binding.md). The script only handles the boring,
must-be-deterministic part: turning the current working directory into a stable
profile location.

Usage:
    python3 profile.py status [project_dir]
    python3 profile.py path   [project_dir]
    python3 profile.py show   [project_dir]

project_dir defaults to the current working directory.

State location resolution (first writable wins):
    1. $REACT_MDX_DIAGRAM_HOME                      (explicit override)
    2. <skill_dir>/state/<project-key>/             (self-contained in skill/plugin)
    3. ~/.claude/.react-mdx-diagram/state/<key>/    (fallback when skill dir is read-only,
                                                      e.g. a plugin installed from a cache)

The project key is derived from the git toplevel (preferred — stable across
subdirectories and machines via the remote) or the absolute project path,
hashed so it is filesystem-safe and doesn't leak full paths into filenames.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE_FILES = ("theme.ts", "binding.json", "profile.md")


def _git_toplevel(project_dir: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(project_dir), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def _git_remote(project_dir: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(project_dir), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


def project_identity(project_dir: Path) -> tuple[str, str]:
    """Return (human_label, stable_key) for the project.

    Prefer the git remote (same project on any clone), then the git toplevel
    path, then the absolute directory. The key is a short hash so it is safe as
    a directory name and the same project always maps to the same profile.
    """
    remote = _git_remote(project_dir)
    top = _git_toplevel(project_dir)
    if remote:
        basis, label = remote, remote
    elif top:
        basis, label = top, Path(top).name
    else:
        resolved = str(project_dir.resolve())
        basis, label = resolved, project_dir.resolve().name
    key = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
    return label, key


def _writable(dir_path: Path) -> bool:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        probe = dir_path / ".write-probe"
        probe.write_text("ok")
        probe.unlink()
        return True
    except Exception:
        return False


def state_dir(project_dir: Path) -> Path:
    _, key = project_identity(project_dir)
    override = os.environ.get("REACT_MDX_DIAGRAM_HOME")
    if override:
        return Path(override).expanduser() / key
    in_skill = SKILL_DIR / "state"
    if _writable(in_skill):
        return in_skill / key
    return Path.home() / ".claude" / ".react-mdx-diagram" / "state" / key


def is_set_up(profile_dir: Path) -> bool:
    # A profile counts as established once a theme.ts exists. binding.json and
    # profile.md are optional (a project may never bind a design system).
    return (profile_dir / "theme.ts").exists()


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in {"status", "path", "show"}:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    project_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    label, key = project_identity(project_dir)
    pdir = state_dir(project_dir)

    if cmd == "path":
        print(pdir)
        return 0

    if cmd == "status":
        ready = is_set_up(pdir)
        present = [f for f in PROFILE_FILES if (pdir / f).exists()]
        print(json.dumps({
            "project": label,
            "key": key,
            "profile_dir": str(pdir),
            "set_up": ready,
            "files_present": present,
        }, ensure_ascii=False, indent=2))
        if not ready:
            print("\n# NOT set up — run the setup workflow (references/setup.md) before authoring.",
                  file=sys.stderr)
        return 0

    if cmd == "show":
        if not is_set_up(pdir):
            print(f"# No profile for '{label}'. Run setup first.", file=sys.stderr)
            return 1
        for f in PROFILE_FILES:
            fp = pdir / f
            if fp.exists():
                print(f"\n===== {f} =====")
                print(fp.read_text(encoding="utf-8"))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
