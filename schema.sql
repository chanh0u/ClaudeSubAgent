-- To-Do 앱 데이터베이스 스키마

-- 할 일 테이블
CREATE TABLE todos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0,
  deadline DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 제목 검색을 위한 인덱스
CREATE INDEX idx_todos_title ON todos(title);

-- 완료 상태 필터링을 위한 인덱스
CREATE INDEX idx_todos_completed ON todos(completed);

-- 마감일 정렬을 위한 인덱스
CREATE INDEX idx_todos_deadline ON todos(deadline);

-- 생성일 정렬을 위한 인덱스
CREATE INDEX idx_todos_created_at ON todos(created_at);
