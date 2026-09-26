#!/usr/bin/env python3
"""문체 설정 편집기 서버 — 로컬에서 띄우고 브라우저로 편집한다.

    python3 style_server.py [--port 8765] [--host 127.0.0.1] [--open]
    (또는) authoring.py style serve --open

편집기(`ui/style-editor.html`)가 부르는 API:

    GET  /api/state                  분류 체계 · 기능 태그 · 가중치 눈금 · voice 목록 · 레지스트리 위치
    GET  /api/layer?scope=S          S 층의 저장 파일(차분). S = global | voice:<id>
    POST /api/effective              {scope, layer?} → 저장 전 미리보기 포함 유효값 + 검증 결과
    PUT  /api/layer?scope=S          저장. **검증을 통과해야만 쓴다** — 실패면 422 와 문제 목록.
                                     전역 저장은 voice 층이 쓰던 전역 범주를 지우는지도 본다
    POST /api/render                 {scope, layer?, profile} → 모델이 읽게 될 지시문
    POST /api/scan                   {scope, layer?, text} → 가중치 어휘 스캔 + L0 문체 등급

안전장치:
- 기본으로 127.0.0.1 에만 붙는다. 다른 호스트에 열려면 `--host` 를 명시해야 한다.
- 쓰기 요청은 `X-Authoring-Kit: 1` 헤더가 있어야 받는다. 브라우저가 다른 사이트에서 이 헤더를
  붙여 보내려면 사전 요청(preflight)을 거쳐야 하는데 이 서버는 CORS 를 허용하지 않으므로,
  외부 페이지가 사용자 몰래 설정을 바꾸지 못한다.
- 저장은 원자적으로 한다(임시 파일 → rename).

표준 라이브러리만 쓴다.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_registry as SR  # noqa: E402

UI_FILE = SR.PLUGIN_ROOT / "ui" / "style-editor.html"
WRITE_HEADER = "X-Authoring-Kit"
MAX_BODY = 2 * 1024 * 1024
_lock = threading.Lock()


def _scope_ok(scope: str) -> str | None:
    try:
        SR.layer_path(scope)
    except ValueError as e:
        return str(e)
    if scope.startswith("voice:") and not SR.voice_exists(scope.split(":", 1)[1]):
        return f"voice 가 레지스트리에 없다: {scope.split(':', 1)[1]} — 먼저 `authoring-voice` 로 등록한다"
    return None


def _layers_for(scope: str, draft: dict | None) -> tuple[dict, str | None]:
    """미리보기용 레이어 묶음. draft 가 있으면 그 층을 디스크 대신 draft 로 본다."""
    layers = {"global": SR.load_layer("global")}
    vid = None
    if scope.startswith("voice:"):
        vid = scope.split(":", 1)[1]
        layers[scope] = SR.load_layer(scope)
    if draft is not None:
        layers[scope] = draft
    return layers, vid


def _validate(scope: str, layers: dict) -> list[str]:
    problems = SR.validate_catalog()
    if problems:
        return problems
    if scope == "global":
        return SR.validate_layer("global", layers["global"]) + _voices_broken_by(layers["global"])
    return (SR.validate_layer("global", layers["global"])
            + SR.validate_layer(scope, layers[scope], base_layers={"global": layers["global"]}))


def _voices_broken_by(new_global: dict) -> list[str]:
    """전역을 바꾸면 그 위에 선 voice 층이 깨질 수 있다 — voice 가 쓰던 전역 범주를 지운 경우.

    전역만 검사하면 저장은 통과하고 voice 는 다음 해석에서야 깨진다. 그래서 전역 저장 전에
    voice 층마다 옛 전역과 새 전역 위에서 각각 검사해, **새로 생기는 문제만** 돌려준다.
    voice 에 원래 있던 문제로 전역 저장까지 막지는 않는다.
    """
    old_global = SR.load_layer("global")
    out: list[str] = []
    for v in SR.list_voices():
        if not v.get("has_style"):
            continue
        scope = f"voice:{v['id']}"
        layer = SR.load_layer(scope)
        before = set(SR.validate_layer(scope, layer, base_layers={"global": old_global}))
        for p in SR.validate_layer(scope, layer, base_layers={"global": new_global}):
            if p not in before:
                out.append(f"{p} — 이 전역 변경이 voice '{v['id']}' 를 깨뜨린다")
    return out


def state() -> dict:
    cat = SR.load_catalog()
    return {
        "registry_home": str(SR.registry_home()),
        "global_path": str(SR.global_path()),
        "weight_bands": {str(k): v for k, v in SR.WEIGHT_BANDS.items()},
        "check_modes": list(SR.CHECK_MODES),
        "gate_levels": list(SR.GATE_LEVELS),
        "l1_axes": list(SR.L1_AXES),
        "categories": cat.get("categories", []),
        "functions": cat.get("functions", []),
        "taxonomy": SR.load_taxonomy(),
        "voices": SR.list_voices(),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "authoring-kit-style/1"

    def log_message(self, fmt, *args):  # 조용히 — 편집기가 자주 부른다
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    # ── 응답 ──
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("요청이 너무 크다")
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _query(self) -> dict:
        return {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}

    def _guard_write(self) -> bool:
        if self.headers.get(WRITE_HEADER) != "1":
            self._json(403, {"error": f"쓰기 요청에는 {WRITE_HEADER}: 1 헤더가 필요하다"})
            return False
        return True

    # ── 라우팅 ──
    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path in ("/", "/index.html"):
                self._send(200, UI_FILE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/state":
                self._json(200, state())
            elif path == "/api/layer":
                scope = self._query().get("scope", "global")
                err = _scope_ok(scope)
                if err:
                    return self._json(400, {"error": err})
                self._json(200, {"scope": scope, "path": str(SR.layer_path(scope)),
                                 "exists": SR.layer_path(scope).exists(), "layer": SR.load_layer(scope)})
            else:
                self._json(404, {"error": "없는 경로"})
        except Exception as e:  # 편집기에 원인을 보인다 — 조용히 삼키지 않는다
            self._json(500, {"error": f"{type(e).__name__}: {e}"})

    def do_POST(self):
        path = urlparse(self.path).path
        if not self._guard_write():
            return
        try:
            body = self._body()
            scope = body.get("scope", "global")
            err = _scope_ok(scope)
            if err:
                return self._json(400, {"error": err})
            layers, vid = _layers_for(scope, body.get("layer"))
            if path == "/api/effective":
                eff = SR.effective(vid, layers=layers)
                self._json(200, {"effective": eff, "problems": _validate(scope, layers)})
            elif path == "/api/render":
                eff = SR.effective(vid, layers=layers)
                usage = "generate"
                if vid:
                    vj = json.loads((SR.registry_home() / "voices" / vid / "voice.json").read_text(encoding="utf-8"))
                    usage = vj.get("usage", "generate")
                self._json(200, {"markdown": SR.render(eff, profile=body.get("profile", "worker"), usage=usage)})
            elif path == "/api/scan":
                import scan_ai_style as SCAN  # noqa: E402
                import scan_lexicon as LEXSCAN  # noqa: E402
                text = body.get("text", "")
                eff = SR.effective(vid, layers=layers)
                lex = LEXSCAN.run(text, vid, eff=eff)
                # L0 등급도 같은 설정으로 — 항목 단위 면제가 반영된 목록을 스캐너에 끼운다.
                with _lock:
                    saved = SCAN.LEX
                    try:
                        SCAN.LEX = SR.l0_lists(eff)
                        waived = set()
                        if vid:
                            vj = json.loads((SR.registry_home() / "voices" / vid / "voice.json")
                                            .read_text(encoding="utf-8"))
                            waived = {w["code"] for w in vj.get("waivers", []) if w.get("code")}
                        l0 = SCAN.scan(text, waived)
                    finally:
                        SCAN.LEX = saved
                self._json(200, {"lexicon": lex, "l0": l0})
            else:
                self._json(404, {"error": "없는 경로"})
        except (ValueError, json.JSONDecodeError) as e:
            self._json(400, {"error": str(e)})
        except Exception as e:
            self._json(500, {"error": f"{type(e).__name__}: {e}"})

    def do_PUT(self):
        path = urlparse(self.path).path
        if path != "/api/layer":
            return self._json(404, {"error": "없는 경로"})
        if not self._guard_write():
            return
        try:
            scope = self._query().get("scope", "global")
            err = _scope_ok(scope)
            if err:
                return self._json(400, {"error": err})
            layer = self._body().get("layer")
            if not isinstance(layer, dict):
                return self._json(400, {"error": "layer 객체가 필요하다"})
            with _lock:
                layers, _ = _layers_for(scope, layer)
                problems = _validate(scope, layers)
                if problems:
                    # 조용히 고쳐 저장하지 않는다. 사용자가 보고 고치게 되돌려 보낸다.
                    return self._json(422, {"saved": False, "problems": problems})
                p = SR.save_layer(scope, layer)
            self._json(200, {"saved": True, "path": str(p), "layer": SR.load_layer(scope)})
        except (ValueError, json.JSONDecodeError) as e:
            self._json(400, {"error": str(e)})
        except Exception as e:
            self._json(500, {"error": f"{type(e).__name__}: {e}"})


def make_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8765, *, open_browser: bool = False) -> int:
    problems = SR.validate_catalog()
    if problems:
        print("기본 카탈로그가 깨져 있어 편집기를 띄우지 않는다:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    srv = make_server(host, port)
    url = f"http://{host}:{srv.server_address[1]}/"
    print(f"문체 설정 편집기 — {url}")
    print(f"  레지스트리: {SR.registry_home()}")
    print("  끝내려면 Ctrl+C")
    if host not in ("127.0.0.1", "localhost", "::1"):
        print(f"  ! {host} 에 열었다. 같은 네트워크의 누구나 설정을 바꿀 수 있다.", file=sys.stderr)
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="브라우저를 연다")
    a = ap.parse_args()
    return serve(a.host, a.port, open_browser=a.open)


if __name__ == "__main__":
    raise SystemExit(main())
