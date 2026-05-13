# Agent 작업 PR 관리 및 Slack 알림 가이드

각 Agent의 작업 내역을 Pull Request로 관리하고 Slack으로 알림받는 방법을 안내합니다.

## 목차

1. [시스템 개요](#시스템-개요)
2. [사전 준비](#사전-준비)
3. [방법 1: GitHub Actions + Slack](#방법-1-github-actions--slack)
4. [방법 2: Claude Code Hooks + Slack](#방법-2-claude-code-hooks--slack)
5. [방법 3: Agent별 자동 PR 생성](#방법-3-agent별-자동-pr-생성)
6. [Slack 메시지 커스터마이징](#slack-메시지-커스터마이징)
7. [문제 해결](#문제-해결)

---

## 시스템 개요

### 워크플로우

```
Agent 작업 완료
    ↓
브랜치 생성 및 커밋
    ↓
PR 생성 (자동/수동)
    ↓
GitHub Actions 트리거
    ↓
Slack 알림 전송
```

### Agent별 브랜치 전략

```
feature/planner-<task-name>      # Planner 작업
feature/dba-<task-name>          # DBA 작업
feature/backend-<task-name>      # Backend 작업
feature/frontend-<task-name>     # Frontend 작업
feature/full-<task-name>         # Controller 작업
```

---

## 사전 준비

### 1. Slack Webhook 생성

1. Slack 워크스페이스에서 App 생성
   - https://api.slack.com/apps 접속
   - "Create New App" 클릭
   - "From scratch" 선택
   - App 이름: "Claude Agent Reporter"

2. Incoming Webhook 활성화
   - "Incoming Webhooks" 메뉴 선택
   - "Activate Incoming Webhooks" 토글 ON
   - "Add New Webhook to Workspace" 클릭
   - 알림 받을 채널 선택 (예: #dev-notifications)

3. Webhook URL 복사
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
   ```

### 2. GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions:

```
SLACK_WEBHOOK_URL: <위에서 복사한 Webhook URL>
```

### 3. GitHub CLI 설치 확인

```bash
gh --version
# GitHub CLI 2.x 이상
```

---

## 방법 1: GitHub Actions + Slack

### 1-1. GitHub Actions 워크플로우 생성

`.github/workflows/pr-slack-notification.yml` 파일 생성:

```yaml
name: PR Slack Notification

on:
  pull_request:
    types: [opened, closed, reopened]
    branches:
      - master
      - main

jobs:
  notify-slack:
    runs-on: ubuntu-latest
    steps:
      - name: Extract Agent Info
        id: agent
        run: |
          BRANCH="${{ github.head_ref }}"

          # Extract agent name from branch
          if [[ $BRANCH == feature/planner-* ]]; then
            AGENT="📋 Planner"
            COLOR="#3498db"
          elif [[ $BRANCH == feature/dba-* ]]; then
            AGENT="🗄️ DBA"
            COLOR="#9b59b6"
          elif [[ $BRANCH == feature/backend-* ]]; then
            AGENT="⚙️ Backend"
            COLOR="#e74c3c"
          elif [[ $BRANCH == feature/frontend-* ]]; then
            AGENT="🎨 Frontend"
            COLOR="#2ecc71"
          elif [[ $BRANCH == feature/full-* ]]; then
            AGENT="🤖 Controller"
            COLOR="#f39c12"
          else
            AGENT="🔧 Manual"
            COLOR="#95a5a6"
          fi

          echo "agent=$AGENT" >> $GITHUB_OUTPUT
          echo "color=$COLOR" >> $GITHUB_OUTPUT

      - name: Send Slack Notification (PR Opened)
        if: github.event.action == 'opened'
        uses: slackapi/slack-github-action@v1.24.0
        with:
          payload: |
            {
              "attachments": [
                {
                  "color": "${{ steps.agent.outputs.color }}",
                  "title": "🚀 New PR by ${{ steps.agent.outputs.agent }}",
                  "title_link": "${{ github.event.pull_request.html_url }}",
                  "fields": [
                    {
                      "title": "PR Title",
                      "value": "${{ github.event.pull_request.title }}",
                      "short": false
                    },
                    {
                      "title": "Author",
                      "value": "${{ github.event.pull_request.user.login }}",
                      "short": true
                    },
                    {
                      "title": "Branch",
                      "value": "${{ github.head_ref }}",
                      "short": true
                    },
                    {
                      "title": "Files Changed",
                      "value": "${{ github.event.pull_request.changed_files }}",
                      "short": true
                    },
                    {
                      "title": "Lines Changed",
                      "value": "+${{ github.event.pull_request.additions }} / -${{ github.event.pull_request.deletions }}",
                      "short": true
                    }
                  ],
                  "footer": "Claude Agent System",
                  "footer_icon": "https://avatars.githubusercontent.com/u/12345",
                  "ts": "${{ github.event.pull_request.created_at }}"
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK

      - name: Send Slack Notification (PR Merged)
        if: github.event.action == 'closed' && github.event.pull_request.merged == true
        uses: slackapi/slack-github-action@v1.24.0
        with:
          payload: |
            {
              "attachments": [
                {
                  "color": "good",
                  "title": "✅ PR Merged by ${{ steps.agent.outputs.agent }}",
                  "title_link": "${{ github.event.pull_request.html_url }}",
                  "fields": [
                    {
                      "title": "PR Title",
                      "value": "${{ github.event.pull_request.title }}",
                      "short": false
                    },
                    {
                      "title": "Merged by",
                      "value": "${{ github.event.pull_request.merged_by.login }}",
                      "short": true
                    },
                    {
                      "title": "Branch",
                      "value": "${{ github.head_ref }} → ${{ github.base_ref }}",
                      "short": true
                    }
                  ],
                  "footer": "Claude Agent System"
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

---

## 방법 2: Claude Code Hooks + Slack

### 2-1. Claude Code Settings 설정

`~/.claude/settings.json` 또는 프로젝트 `.claude/settings.json`:

```json
{
  "hooks": {
    "afterToolCall": "bash ~/.claude/hooks/after-tool-call.sh"
  }
}
```

### 2-2. Hook 스크립트 생성

`~/.claude/hooks/after-tool-call.sh`:

```bash
#!/bin/bash

# Slack Webhook URL
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Tool call 정보 파싱
TOOL_NAME="$1"
AGENT_NAME="$2"
RESULT="$3"

# Git 작업 감지
if [[ "$TOOL_NAME" == "Bash" ]] && [[ "$RESULT" == *"git commit"* ]]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    COMMIT_MSG=$(git log -1 --pretty=%B)
    AUTHOR=$(git config user.name)

    # Agent 감지
    if [[ "$BRANCH" == feature/planner-* ]]; then
        EMOJI="📋"
        AGENT="Planner"
    elif [[ "$BRANCH" == feature/dba-* ]]; then
        EMOJI="🗄️"
        AGENT="DBA"
    elif [[ "$BRANCH" == feature/backend-* ]]; then
        EMOJI="⚙️"
        AGENT="Backend"
    elif [[ "$BRANCH" == feature/frontend-* ]]; then
        EMOJI="🎨"
        AGENT="Frontend"
    else
        EMOJI="🔧"
        AGENT="Manual"
    fi

    # Slack 메시지 전송
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{
            \"text\": \"$EMOJI *$AGENT* committed changes\",
            \"attachments\": [{
                \"color\": \"#36a64f\",
                \"fields\": [
                    {\"title\": \"Branch\", \"value\": \"$BRANCH\", \"short\": true},
                    {\"title\": \"Author\", \"value\": \"$AUTHOR\", \"short\": true},
                    {\"title\": \"Commit Message\", \"value\": \"$COMMIT_MSG\", \"short\": false}
                ]
            }]
        }"
fi
```

실행 권한 부여:

```bash
chmod +x ~/.claude/hooks/after-tool-call.sh
```

---

## 방법 3: Agent별 자동 PR 생성

### 3-1. Agent 완료 시 자동 PR 생성 스크립트

`.claude/scripts/create-agent-pr.sh`:

```bash
#!/bin/bash

# 사용법: ./create-agent-pr.sh <agent-name> <task-description>
# 예: ./create-agent-pr.sh planner "사용자 프로필 기능 기획"

AGENT=$1
TASK=$2
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Agent별 이모지 및 색상
case $AGENT in
    planner)
        EMOJI="📋"
        COLOR="#3498db"
        ;;
    dba)
        EMOJI="🗄️"
        COLOR="#9b59b6"
        ;;
    backend)
        EMOJI="⚙️"
        COLOR="#e74c3c"
        ;;
    frontend)
        EMOJI="🎨"
        COLOR="#2ecc71"
        ;;
    controller)
        EMOJI="🤖"
        COLOR="#f39c12"
        ;;
    *)
        EMOJI="🔧"
        COLOR="#95a5a6"
        ;;
esac

# 브랜치 이름 생성
BRANCH_NAME="feature/${AGENT}-$(echo $TASK | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

# 현재 브랜치 확인
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# 이미 feature 브랜치라면 그대로 사용, 아니면 새 브랜치 생성
if [[ "$CURRENT_BRANCH" != feature/* ]]; then
    git checkout -b "$BRANCH_NAME"
fi

# 변경사항 확인
CHANGED_FILES=$(git diff --name-only)
if [ -z "$CHANGED_FILES" ]; then
    echo "No changes to commit"
    exit 0
fi

# 커밋 (이미 agent에서 했다면 스킵)
# git add .
# git commit -m "$EMOJI $AGENT: $TASK"

# Push
git push -u origin "$BRANCH_NAME"

# PR 생성
PR_BODY="## $EMOJI Agent: $AGENT

### Task
$TASK

### Changes
$(git diff --stat master..HEAD)

### Files Modified
\`\`\`
$CHANGED_FILES
\`\`\`

---
🤖 Generated by Claude Agent System
"

PR_URL=$(gh pr create \
    --title "$EMOJI $AGENT: $TASK" \
    --body "$PR_BODY" \
    --base master \
    --head "$BRANCH_NAME" \
    --label "agent:$AGENT" \
    | tail -1)

echo "PR created: $PR_URL"

# Slack 알림
curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "{
        \"attachments\": [{
            \"color\": \"$COLOR\",
            \"title\": \"$EMOJI New PR by $AGENT\",
            \"title_link\": \"$PR_URL\",
            \"fields\": [
                {\"title\": \"Task\", \"value\": \"$TASK\", \"short\": false},
                {\"title\": \"Branch\", \"value\": \"$BRANCH_NAME\", \"short\": true},
                {\"title\": \"Files Changed\", \"value\": \"$(echo '$CHANGED_FILES' | wc -l)\", \"short\": true}
            ],
            \"footer\": \"Claude Agent System\"
        }]
    }"
```

실행 권한:

```bash
chmod +x .claude/scripts/create-agent-pr.sh
```

### 3-2. Agent 정의에 PR 생성 추가

각 agent 파일 (예: `.claude/agents/planner.md`)에 추가:

```markdown
## 작업 완료 후

작업 완료 시 다음 명령 실행:

```bash
./.claude/scripts/create-agent-pr.sh planner "작업 설명"
```
```

---

## Slack 메시지 커스터마이징

### 상세 정보 포함 예시

```json
{
  "text": "🎨 Frontend Agent completed work",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🎨 Frontend: User Profile Page"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*PR:*\n<https://github.com/user/repo/pull/123|#123>"
        },
        {
          "type": "mrkdwn",
          "text": "*Status:*\nReady for Review"
        },
        {
          "type": "mrkdwn",
          "text": "*Files:*\n12 changed"
        },
        {
          "type": "mrkdwn",
          "text": "*Lines:*\n+245 / -87"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Changes:*\n• Added profile component\n• Updated API integration\n• Added unit tests"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View PR"
          },
          "url": "https://github.com/user/repo/pull/123",
          "style": "primary"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Review Changes"
          },
          "url": "https://github.com/user/repo/pull/123/files"
        }
      ]
    }
  ]
}
```

### Agent별 스레드 생성

같은 작업의 진행 상황을 스레드로 관리:

```bash
# 첫 메시지 전송 후 thread_ts 저장
THREAD_TS=$(curl -X POST "$SLACK_WEBHOOK" ... | jq -r '.ts')

# 후속 메시지는 thread_ts 포함
curl -X POST "$SLACK_WEBHOOK" \
    -d "{
        \"thread_ts\": \"$THREAD_TS\",
        \"text\": \"Backend work completed\"
    }"
```

---

## 통합 워크플로우 예시

### Agent View에서 작업 → PR 생성 → Slack 알림

```bash
# 1. Agent View에서 작업 디스패치
claude agents
> planner 사용자 프로필 기능 추가

# 2. 작업 완료 후 Agent에 지시
"작업이 완료되었으면 feature/planner-user-profile 브랜치를 생성하고
 커밋한 후 .claude/scripts/create-agent-pr.sh를 실행해주세요"

# 3. 자동으로:
#    - PR 생성
#    - GitHub Actions 트리거
#    - Slack 알림 전송
```

### Controller 사용 시 전체 프로세스 자동화

`.claude/agents/controller.md`에 추가:

```markdown
## 각 단계 완료 후

1. Planner 완료 → PR 생성 (feature/planner-*)
2. DBA 완료 → PR 생성 (feature/dba-*)
3. Backend 완료 → PR 생성 (feature/backend-*)
4. Frontend 완료 → PR 생성 (feature/frontend-*)
5. 모든 PR merge → 최종 PR 생성 (feature/full-*)

각 단계마다 Slack 알림 전송
```

---

## 실전 사용 예시

### 예시 1: 개별 Agent 작업

```bash
# 1. Agent View에서
planner 알림 기능 추가

# 2. 완료 후 (Agent가 자동으로 또는 수동으로)
./.claude/scripts/create-agent-pr.sh planner "알림 기능 추가"

# 3. Slack에 알림 도착
# "📋 New PR by Planner: 알림 기능 추가"
```

### 예시 2: Controller 전체 자동화

```bash
# 1. Agent View에서
controller 알림 기능 전체 구현

# 2. Controller가 각 단계마다:
#    - Planner 완료 → PR + Slack 알림
#    - DBA 완료 → PR + Slack 알림
#    - Backend 완료 → PR + Slack 알림
#    - Frontend 완료 → PR + Slack 알림
#    - Reviewer 검증 → Slack 알림

# 3. Slack 스레드에서 전체 진행 상황 확인
```

---

## PR 레이블 전략

### GitHub Labels 사전 생성

```bash
gh label create "agent:planner" --color "3498db" --description "Planner agent work"
gh label create "agent:dba" --color "9b59b6" --description "DBA agent work"
gh label create "agent:backend" --color "e74c3c" --description "Backend agent work"
gh label create "agent:frontend" --color "2ecc71" --description "Frontend agent work"
gh label create "agent:controller" --color "f39c12" --description "Controller agent work"
gh label create "status:review-needed" --color "fbca04" --description "Needs review"
gh label create "status:auto-generated" --color "d4c5f9" --description "Auto-generated by AI"
```

### PR 템플릿

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## 🤖 AI Agent Information

**Agent:** <!-- planner / dba / backend / frontend / controller -->
**Task:** <!-- Task description -->

---

## 📋 Changes

<!-- Auto-generated or manual description -->

### Files Modified
<!-- List of modified files -->

### Key Changes
-
-
-

---

## ✅ Checklist

- [ ] Code follows project standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Ready for review

---

## 🔗 Related

- Related Issue: #
- Related PRs: #

---

🤖 Generated by Claude Agent System
```

---

## 문제 해결

### Q1: Slack 알림이 전송되지 않아요

**확인사항:**
```bash
# Webhook URL 테스트
curl -X POST YOUR_SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d '{"text":"Test message"}'
```

**해결:**
- Webhook URL이 올바른지 확인
- GitHub Secrets에 정확히 등록되었는지 확인
- Slack App 권한 확인

### Q2: GitHub Actions가 실행되지 않아요

**확인:**
```bash
# Workflow 파일 문법 검사
yamllint .github/workflows/pr-slack-notification.yml

# Actions 탭에서 오류 확인
```

### Q3: PR이 자동 생성되지 않아요

**확인:**
```bash
# gh CLI 인증 확인
gh auth status

# 스크립트 실행 권한 확인
ls -la .claude/scripts/create-agent-pr.sh

# 수동 실행 테스트
./.claude/scripts/create-agent-pr.sh planner "test"
```

### Q4: 브랜치 충돌이 발생해요

**해결:**
```bash
# Master에서 최신 코드 pull
git checkout master
git pull

# Feature 브랜치 rebase
git checkout feature/planner-task
git rebase master
```

---

## 고급 기능

### 1. PR 자동 머지 조건

`.github/workflows/auto-merge.yml`:

```yaml
name: Auto Merge

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  auto-approve:
    runs-on: ubuntu-latest
    if: startsWith(github.head_ref, 'feature/planner-')
    steps:
      - name: Auto Approve
        run: gh pr review --approve "${{ github.event.pull_request.number }}"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Agent별 Review 요청

```bash
# Backend PR은 자동으로 backend 팀에 리뷰 요청
gh pr create ... --reviewer backend-team
```

### 3. Slack 대화형 알림

```json
{
  "blocks": [
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "Approve"},
          "style": "primary",
          "action_id": "approve_pr"
        },
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "Request Changes"},
          "style": "danger",
          "action_id": "request_changes"
        }
      ]
    }
  ]
}
```

---

## 참고 자료

- [GitHub Actions - Slack Integration](https://github.com/slackapi/slack-github-action)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [GitHub CLI - PR Commands](https://cli.github.com/manual/gh_pr)
- [Claude Code Hooks](https://code.claude.com/docs/hooks)

---

이제 각 Agent의 작업을 체계적으로 PR로 관리하고 팀원들에게 실시간으로 알림을 보낼 수 있습니다! 🚀
