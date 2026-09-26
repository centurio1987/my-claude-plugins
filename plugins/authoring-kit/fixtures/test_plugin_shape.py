#!/usr/bin/env python3
"""플러그인 구조·컨텍스트 예산 검사.

여기서 잡는 것들은 전부 **에러 없이 흘러가는** 종류다. 스킬이 조용히 안 뜨거나,
메인 스레드 예산을 조용히 잡아먹거나, 이름이 겹쳐 다른 스킬을 가린다.

실행:
    AUTHORING_KIT_HOME=<레지스트리> python3 fixtures/test_plugin_shape.py [project_dir]
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
spec_ = importlib.util.spec_from_file_location("authoring", PLUGIN / "scripts" / "authoring.py")
A = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(A)

FAILS: list[str] = []
PASSES = 0

# 메인 스레드가 읽는 것들의 상한. 넘으면 글 쓸 예산이 남지 않는다.
MAIN_SKILL_MAX_LINES = 130
MAIN_RESOLVE_MAX_LINES = 200


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASSES
    if ok:
        PASSES += 1
        print(f"  ok   {name}")
    else:
        FAILS.append(f"{name}{(' — ' + detail) if detail else ''}")
        print(f"  FAIL {name}{(' — ' + detail) if detail else ''}")


def frontmatter(p: Path) -> dict:
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    body = text[3:end]
    out: dict = {}
    key = None
    for line in body.splitlines():
        m = re.match(r"^([a-zA-Z-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def main() -> int:
    print("플러그인 구조 · 컨텍스트 예산\n")
    skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))

    print("[1] 매니페스트")
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    check("plugin.json 이 name·version·description·author 를 갖는다",
          {"name", "version", "description", "author"} <= set(manifest))
    check("name 이 kebab-case 규칙을 지킨다",
          bool(re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)*", manifest["name"])), manifest["name"])
    check("description 이 50자 이상", len(manifest["description"]) >= 50)

    print("\n[2] 스킬 이름 — 충돌 회피")
    names = []
    for p in skills:
        fm = frontmatter(p)
        names.append(fm.get("name", p.parent.name))
        check(f"{p.parent.name}: frontmatter name 이 디렉토리명과 같다",
              fm.get("name") == p.parent.name, f"{fm.get('name')} vs {p.parent.name}")
    check("모든 스킬이 authoring- 프리픽스를 쓴다",
          all(n.startswith("authoring-") for n in names), str(names))
    check("스킬 이름이 서로 겹치지 않는다", len(names) == len(set(names)))

    print("\n[3] 노출 규칙 — 내부 스킬은 사용자에게 뜨지 않아야 한다")
    for p in skills:
        fm = frontmatter(p)
        internal = p.parent.name == "authoring-method"
        has_flag = fm.get("disable-model-invocation", "").lower() == "true"
        if internal:
            check(f"{p.parent.name}: disable-model-invocation 이 켜져 있다", has_flag)
        else:
            check(f"{p.parent.name}: 사용자에게 노출된다", not has_flag)

    print("\n[4] description — 트리거 문구가 있는가")
    for p in skills:
        fm = frontmatter(p)
        d = fm.get("description", "")
        if p.parent.name == "authoring-method":
            continue           # 내부 스킬은 트리거가 필요 없다
        check(f"{p.parent.name}: description 에 따옴표 트리거 예시가 있다",
              '"' in d or "'" in d, d[:60])

    print(f"\n[5] 컨텍스트 예산 — 메인이 읽는 것은 {MAIN_SKILL_MAX_LINES}줄 이하")
    for p in skills:
        n = len(p.read_text(encoding="utf-8").splitlines())
        # 메인 스레드가 실제로 로드하는 것은 오케스트레이터다. 나머지는 호출될 때만.
        limit = MAIN_SKILL_MAX_LINES if p.parent.name == "authoring-write" else 220
        check(f"{p.parent.name}: {n}줄 ≤ {limit}", n <= limit, f"{n}줄")

    print("\n[6] resolve 프로파일 — main 은 요약, worker 는 전문")
    project = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    try:
        main_doc, main_meta = A.resolve("ppangtolab-teacher", "algo-guide", project, profile="main")
        work_doc, work_meta = A.resolve("ppangtolab-teacher", "algo-guide", project, profile="worker")
    except FileNotFoundError as e:
        print(f"  (건너뜀 — {e})")
        main_doc = work_doc = ""
        main_meta = work_meta = {"hash": "", "conflicts": []}
    if main_doc:
        mn, wn = len(main_doc.splitlines()), len(work_doc.splitlines())
        check(f"main 프로파일 {mn}줄 ≤ {MAIN_RESOLVE_MAX_LINES}", mn <= MAIN_RESOLVE_MAX_LINES, f"{mn}줄")
        check("worker 가 main 보다 충분히 크다(전문을 싣는다)", wn > mn * 3, f"main {mn} / worker {wn}")
        check("main 에 L0 조항 전문이 없다", "## Part A — 패턴 카탈로그" not in main_doc)
        check("worker 에 L0 조항 전문이 있다", "## Part A — 패턴 카탈로그" in work_doc)
        check("main 에도 항목 골격은 있다", "항목 골격" in main_doc)
        check("main 에도 범위 원칙은 있다", "이 글 범위의 원칙" in main_doc)
        check("두 프로파일의 해시가 다르다", main_meta["hash"] != work_meta["hash"])

    print("\n[7] 스크립트가 갖춰져 있는가")
    for s in ("authoring.py", "trace_rules.py", "scan_ai_style.py", "scan_lexicon.py",
              "style_registry.py", "style_server.py", "lint_placeholders.py", "review-external.sh"):
        check(f"scripts/{s} 존재", (PLUGIN / "scripts" / s).exists())
    check("편집기 페이지(ui/style-editor.html) 존재", (PLUGIN / "ui" / "style-editor.html").exists())
    for a in ("lexicon.json", "qualitative.json"):
        check(f"문체 카탈로그 assets/style/{a} 존재",
              (PLUGIN / "skills" / "authoring-method" / "assets" / "style" / a).exists())

    print("\n[8] 스킬이 가리키는 참조가 실재하는가")
    # 스킬 본문에 `assets/…` 라고 적어 놓고 파일을 안 만드는 일이 잦다. 에러가 안 나서
    # 워커가 그 파일을 못 찾은 채 자기 판단으로 진행해 버린다 — 조용한 품질 저하다.
    dangling = []
    for sk in skills:
        text = sk.read_text(encoding="utf-8")
        for m in re.finditer(r"`(\.\./)?(assets/[\w./*-]+)`", text):
            rel, up = m.group(2), m.group(1)
            base = sk.parent.parent if up else sk.parent
            if "*" in rel:
                if not list(base.glob(rel)):
                    dangling.append(f"{sk.parent.name} → {up or ''}{rel}")
            elif not (base / rel).exists():
                dangling.append(f"{sk.parent.name} → {up or ''}{rel}")
    check("끊어진 assets 참조가 없다", not dangling, "; ".join(sorted(set(dangling))))

    print(f"\n{'='*56}")
    print(f"통과 {PASSES} · 실패 {len(FAILS)}")
    if FAILS:
        print("\n실패 목록:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("플러그인 구조 통과.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
