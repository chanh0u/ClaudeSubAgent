# Agent PR & Slack 알림 시스템 설정 가이드

Agent별 작업을 PR로 관리하고 Slack 알림을 받기 위한 빠른 설정 가이드입니다.

## ✅ 생성된 파일

다음 파일들이 자동으로 생성되었습니다:

```
.github/
├── workflows/
│   └── pr-slack-notification.yml    # GitHub Actions 워크플로우
└── PULL_REQUEST_TEMPLATE.md          # PR 템플릿

.claude/
└── scripts/
    └── create-agent-pr.sh            # PR 자동 생성 스크립트
```

## 🚀 빠른 시작 (3단계)

### 1단계: Slack Webhook 생성 (5분)

1. https://api.slack.com/apps 접속
2. "Create New App" → "From scratch" 선택
3. App 이름: "Claude Agent Reporter", 워크스페이스 선택
4. "Incoming Webhooks" → "Activate Incoming Webhooks" ON
5. "Add New Webhook to Workspace" → 채널 선택 (예: #dev-notifications)
6. **Webhook URL 복사**
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
   ```

### 2단계: GitHub Repository 설정 (2분)

1. GitHub Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 정보 입력:
   - Name: `SLACK_WEBHOOK_URL`
   - Secret: (위에서 복사한 Webhook URL)
4. "Add secret" 클릭

### 3단계: GitHub CLI 인증 (1분)

```bash
# GitHub CLI 설치 확인
gh --version

# 인증 (아직 안했다면)
gh auth login

# 브라우저에서 인증 완료
```

## ✅ 설정 완료!

이제 모든 준비가 완료되었습니다.

---

## 📝 사용 방법

### 방법 1: Agent View에서 자동 PR 생성

```bash
# 1. Agent View 시작
claude agents

# 2. Agent 작업 디스패치
planner 사용자 알림 기능 추가

# 3. 작업 완료 후 PR 생성 요청
"작업이 완료되었으면 다음 명령으로 PR을 생성해주세요:
./.claude/scripts/create-agent-pr.sh planner '사용자 알림 기능 추가'"

# 4. 자동으로:
#    ✅ PR 생성
#    ✅ GitHub Actions 실행
#    ✅ Slack 알림 전송
```

### 방법 2: 수동으로 PR 생성

```bash
# 작업 완료 후 직접 실행
./.claude/scripts/create-agent-pr.sh planner "사용자 알림 기능 추가"

# 다른 Agent 예시
./.claude/scripts/create-agent-pr.sh dba "users 테이블 설계"
./.claude/scripts/create-agent-pr.sh backend "로그인 API 구현"
./.claude/scripts/create-agent-pr.sh frontend "로그인 화면 구현"
```

### 방법 3: Slack Webhook 환경변수 설정 (선택사항)

스크립트에서도 Slack 알림을 받으려면:

**Windows (PowerShell):**
```powershell
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Linux/Mac:**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# 영구 설정 (~/.bashrc 또는 ~/.zshrc에 추가)
echo 'export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"' >> ~/.bashrc
```

---

## 🎯 실전 예시

### 예시 1: Planner 작업

```bash
# 1. Agent View에서 기획 작업
claude agents
> planner 댓글 기능 추가

# 2. 작업 완료 후
> ./.claude/scripts/create-agent-pr.sh planner "댓글 기능 추가"

# 3. Slack에 알림 도착
# 📋 New PR by Planner: 댓글 기능 추가
# Branch: feature/planner-댓글-기능-추가
# Files Changed: 1
```

### 예시 2: Controller 전체 워크플로우

```bash
# 1. Controller로 전체 자동화
claude agents
> controller 좋아요 기능 전체 구현

# 2. Controller가 각 단계 완료 후 PR 생성 지시
# Planner 완료 → PR 생성
# DBA 완료 → PR 생성
# Backend 완료 → PR 생성
# Frontend 완료 → PR 생성

# 3. 각 단계마다 Slack 알림
# 📋 Planner PR created
# 🗄️ DBA PR created
# ⚙️ Backend PR created
# 🎨 Frontend PR created
```

---

## 🎨 Slack 알림 예시

PR이 생성되면 다음과 같은 Slack 메시지가 전송됩니다:

```
🚀 New PR by 📋 Planner

PR Title: 📋 Planner: 사용자 알림 기능 추가
Author: chanho
Branch: feature/planner-사용자-알림-기능-추가
Files Changed: 1
Lines Changed: +124 / -0

🔗 [View PR]
```

PR이 머지되면:

```
✅ PR Merged by 📋 Planner

PR Title: 📋 Planner: 사용자 알림 기능 추가
Merged by: chanho
Branch: feature/planner-사용자-알림-기능-추가 → master

🔗 [View PR]
```

---

## 🏷️ Agent별 브랜치 및 색상

| Agent | 브랜치 패턴 | 이모지 | 색상 | PR Label |
|-------|-------------|--------|------|----------|
| Planner | `feature/planner-*` | 📋 | 파란색 | `agent:planner` |
| DBA | `feature/dba-*` | 🗄️ | 보라색 | `agent:dba` |
| Backend | `feature/backend-*` | ⚙️ | 빨간색 | `agent:backend` |
| Frontend | `feature/frontend-*` | 🎨 | 초록색 | `agent:frontend` |
| Controller | `feature/full-*` | 🤖 | 주황색 | `agent:controller` |

---

## 🔧 고급 설정

### PR Label 자동 생성

```bash
# GitHub Labels 생성
gh label create "agent:planner" --color "3498db" --description "Planner agent work"
gh label create "agent:dba" --color "9b59b6" --description "DBA agent work"
gh label create "agent:backend" --color "e74c3c" --description "Backend agent work"
gh label create "agent:frontend" --color "2ecc71" --description "Frontend agent work"
gh label create "agent:controller" --color "f39c12" --description "Controller agent work"
```

### Agent 정의에 PR 생성 추가

각 Agent 파일 (`.claude/agents/*.md`)에 다음 추가:

```markdown
## 작업 완료 후

다음 명령으로 PR을 생성하세요:

```bash
./.claude/scripts/create-agent-pr.sh [agent-name] "작업 설명"
```

예:
```bash
./.claude/scripts/create-agent-pr.sh planner "사용자 프로필 기능 기획"
```
```

---

## 🐛 문제 해결

### Q: Slack 알림이 안와요

**확인사항:**
```bash
# 1. Webhook URL 테스트
curl -X POST YOUR_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d '{"text":"Test"}'

# 2. GitHub Secret 확인
# Repository → Settings → Secrets → SLACK_WEBHOOK_URL 존재 확인
```

### Q: PR 생성 스크립트가 실행 안돼요

**확인사항:**
```bash
# 1. 실행 권한 확인
ls -la .claude/scripts/create-agent-pr.sh

# 2. 실행 권한 부여 (필요시)
chmod +x .claude/scripts/create-agent-pr.sh

# 3. gh CLI 인증 확인
gh auth status
```

### Q: GitHub Actions가 실행 안돼요

**확인사항:**
1. Repository → Actions 탭에서 워크플로우 확인
2. `.github/workflows/pr-slack-notification.yml` 파일 존재 확인
3. Actions가 Repository에서 활성화되어 있는지 확인

### Q: 브랜치가 자동 생성 안돼요

**해결:**
```bash
# 수동으로 브랜치 생성 후 스크립트 실행
git checkout -b feature/planner-my-task
git add .
git commit -m "📋 Planner: My task"
./.claude/scripts/create-agent-pr.sh planner "My task"
```

---

## 📚 추가 자료

- [상세 가이드](./AGENT_PR_SLACK_GUIDE.md) - 전체 기능 및 고급 설정
- [Agent View 가이드](./AGENT_VIEW_GUIDE.md) - Agent View 사용법
- [프로젝트 가이드](./CLAUDE.md) - 프로젝트 구조 및 개발 가이드

---

## ✨ 다음 단계

1. ✅ Slack Webhook 생성 완료
2. ✅ GitHub Secret 설정 완료
3. ✅ GitHub CLI 인증 완료
4. 🚀 첫 PR 생성해보기!

```bash
# 테스트 PR 생성
./.claude/scripts/create-agent-pr.sh planner "테스트 기획"
```

즐거운 개발 되세요! 🎉
