# centurio87-plugins

김윤덕의 개인 Claude 플러그인 **마켓플레이스**입니다. 개인 작업과 여러 프로젝트에 흩어져 있는 스킬·MCP 서버·커맨드·훅·에이전트를 플러그인으로 모아 한곳에서 배포·관리합니다.

## 구조

```
my-claude-plugin/
├── .claude-plugin/
│   └── marketplace.json      # 마켓 매니페스트 (플러그인 목록)
├── plugins/                  # 각 플러그인이 하위 디렉터리로 존재
│   └── hello-marketplace/    # 예시(템플릿) 플러그인
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── greeting/
│               └── SKILL.md
└── README.md
```

`marketplace.json`의 각 플러그인 엔트리는 `name`, `description`, `version`, `source`(이 레포 기준 상대 경로)를 가집니다. `source`는 `./plugins/<이름>` 처럼 로컬 경로이거나, GitHub/Git URL 같은 원격 소스일 수 있습니다.

## 마켓 추가하기

이 레포를 GitHub에 올린 뒤 Claude Code에서:

```
/plugin marketplace add <github-사용자명>/my-claude-plugin
/plugin install hello-marketplace@centurio87-plugins
```

로컬 경로로도 추가할 수 있습니다:

```
/plugin marketplace add /Users/centurio/my-claude-plugin
```

## 새 플러그인 추가하기

직접 만들 수도 있고, **`publish-to-marketplace` 스킬**(개인 스코프로 설치)을 사용해 자동화할 수 있습니다. 그 스킬은 기존 스킬/MCP/커맨드/훅/에이전트를 받아 플러그인 디렉터리로 패키징하고 이 `marketplace.json`에 엔트리를 등록합니다.

자세한 구성 요소 스키마(plugin.json, SKILL.md, .mcp.json, hooks.json, agents)는 `publish-to-marketplace` 스킬의 `references/component-schemas.md`를 참고하세요.
