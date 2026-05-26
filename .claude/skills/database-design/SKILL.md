---
name: database-design
description: "DB 스키마 설계 및 마이그레이션 스크립트 작성. PostgreSQL/MySQL 등 RDBMS 지원. workspace-map의 owns 경로만 수정. 정규화, 인덱스, 외래키 제약조건 적용."
---

# Database Design Skill

데이터베이스 스키마를 설계하고 마이그레이션 스크립트를 작성하는 스킬. AI Agent Company 워크플로우의 Phase 3에서 database-engineer 에이전트가 사용한다.

## 핵심 역할

1. **스키마 설계**: 테이블, 컬럼, 데이터 타입 정의
2. **정규화**: 데이터 중복 제거, 무결성 보장
3. **마이그레이션 스크립트**: SQL 파일 생성
4. **인덱스 최적화**: 조회 성능 향상
5. **파일 소유권 준수**: workspace-map의 owns 경로만 수정

## 기술 스택

- **RDBMS**: PostgreSQL (기본), MySQL, SQLite
- **Migration Tool**: SQL 파일 직접 작성

## 작업 원칙

### 원칙 1: workspace-map 준수

**필수**: `_workspace/02_workspace-map.json` 읽기

```sql
-- owns 경로만 수정
-- 예: ["migrations/**", "src/db/**"]

-- forbidden 경로는 절대 수정 금지
-- 예: ["src/api/**", "src/components/**"]
```

### 원칙 2: 네이밍 규칙

- 테이블명: 복수형, snake_case (예: `todos`, `user_profiles`)
- 컬럼명: snake_case (예: `user_id`, `created_at`)
- 외래키: `{테이블명}_id` (예: `user_id`)
- 인덱스: `idx_{테이블명}_{컬럼명}` (예: `idx_todos_user_id`)

### 원칙 3: 필수 컬럼

모든 테이블에 포함:
- `id`: Primary Key (SERIAL 또는 UUID)
- `created_at`: 생성 시각 (TIMESTAMP)
- `updated_at`: 수정 시각 (TIMESTAMP, 선택)

### 원칙 4: 외래키 제약조건

```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

## 출력 구조

```
workspace/{project_id}/
├── migrations/
│   ├── 001_create_users.sql
│   ├── 002_create_todos.sql
│   └── 003_add_indexes.sql
└── src/db/
    └── schema.md  # 스키마 문서 (선택)
```

## 스키마 설계 패턴

### 패턴 1: 기본 테이블

```sql
-- migrations/001_create_todos.sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 패턴 2: 외래키

```sql
-- migrations/002_create_users_and_todos.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 패턴 3: 인덱스

```sql
-- migrations/003_add_indexes.sql
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
CREATE INDEX idx_users_email ON users(email);  -- UNIQUE이면 자동 인덱스지만 명시적 추가 가능
```

> 상세: [references/schema-patterns.md](references/schema-patterns.md)

## 데이터 타입 선택

### PostgreSQL

| 용도 | 타입 | 예시 |
|------|------|------|
| 정수 (ID) | SERIAL, INTEGER | `id SERIAL PRIMARY KEY` |
| 짧은 문자열 | VARCHAR(N) | `title VARCHAR(200)` |
| 긴 문자열 | TEXT | `description TEXT` |
| 불리언 | BOOLEAN | `completed BOOLEAN` |
| 날짜/시간 | TIMESTAMP | `created_at TIMESTAMP` |
| JSON | JSONB | `metadata JSONB` |
| UUID | UUID | `id UUID DEFAULT gen_random_uuid()` |

## 마이그레이션 스크립트 작성

### 규칙 1: 파일명 규칙

```
{순서}_{설명}.sql

예:
001_create_users.sql
002_create_todos.sql
003_add_user_id_to_todos.sql
004_add_indexes.sql
```

### 규칙 2: 멱등성

스크립트는 여러 번 실행해도 안전해야 함:

```sql
-- 테이블이 없을 때만 생성
CREATE TABLE IF NOT EXISTS todos (
    ...
);

-- 컬럼이 없을 때만 추가
ALTER TABLE todos ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 인덱스가 없을 때만 생성
CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id);
```

### 규칙 3: 롤백 스크립트

각 마이그레이션에 롤백 스크립트 포함 (주석):

```sql
-- migrations/002_create_todos.sql

-- Forward migration
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rollback (주석으로 포함)
-- DROP TABLE IF EXISTS todos;
```

## 협업 프로토콜 (Phase 3)

### backend-dev와 협업

**스키마 공유**:

```
[db-engineer → backend-dev]
"todos 테이블 스키마 완성.
컬럼: id (SERIAL), title (VARCHAR), description (TEXT), completed (BOOLEAN), created_at (TIMESTAMP)
migrations/001_todos.sql 확인하세요."

[backend-dev → db-engineer]
"확인했습니다. user_id 외래키도 필요합니다."

[db-engineer → backend-dev]
"user_id 추가 완료. migrations/002_add_user_id.sql"
```

## 절대 금지

- ❌ forbidden 경로 수정 금지 (src/api/**, src/components/**)
- ❌ CASCADE 없이 외래키 삭제
- ❌ 인덱스 없이 대용량 테이블 조회
- ❌ NOT NULL 없이 필수 컬럼 정의

## 핵심 규칙

**Rule 1**: 모든 테이블에 id, created_at 포함

**Rule 2**: 외래키는 ON DELETE CASCADE 명시

**Rule 3**: workspace-map의 `owns` 경로만 수정

**Rule 4**: 파일명은 `{순서}_{설명}.sql`

**Rule 5**: 작업 완료 시 리더에게 보고

## 검증

구현 완료 후 확인:

- [ ] `migrations/` 디렉토리에 최소 1개 파일
- [ ] 모든 테이블에 PRIMARY KEY
- [ ] 외래키에 ON DELETE CASCADE
- [ ] 네이밍 규칙 준수 (snake_case)
- [ ] workspace-map의 `owns` 경로만 수정
- [ ] `forbidden` 경로 미수정

## 참조

- 스키마 패턴: [references/schema-patterns.md](references/schema-patterns.md)
