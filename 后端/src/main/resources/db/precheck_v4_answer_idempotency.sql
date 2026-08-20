-- V4 回答幂等迁移只读预检查（不修改业务表）。
-- 用法：mysql -u <user> -p <database> < precheck_v4_answer_idempotency.sql
-- 必须在与 migration_v4_answer_idempotency.sql 相同的目标 schema 中执行。

SELECT DATABASE() AS target_schema, VERSION() AS mysql_version;

-- 1. 目标列是否已经存在，并报告类型、字符集和排序规则。
SELECT column_name, column_type, is_nullable, character_set_name, collation_name
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND table_name = 'interview_message'
  AND column_name IN ('answer_id', 'submission_id')
ORDER BY ordinal_position;

-- 2. 目标索引是否已经存在及其实际列顺序。
SELECT index_name, non_unique, seq_in_index, column_name
FROM information_schema.statistics
WHERE table_schema = DATABASE()
  AND table_name = 'interview_message'
  AND index_name IN ('uk_session_answer', 'uk_session_submission')
ORDER BY index_name, seq_in_index;

-- 3. answer_id 数据质量；列尚不存在时返回 NOT_PRESENT，不会导致脚本中断。
SET @has_answer_id = (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE() AND table_name = 'interview_message' AND column_name = 'answer_id'
);
SET @answer_stats_sql = IF(
  @has_answer_id = 1,
  'SELECT COUNT(*) AS total_rows, SUM(answer_id IS NULL) AS null_count, COALESCE(SUM(answer_id = ''''), 0) AS empty_string_count FROM interview_message',
  'SELECT ''answer_id'' AS column_name, ''NOT_PRESENT'' AS status'
);
PREPARE answer_stats FROM @answer_stats_sql;
EXECUTE answer_stats;
DEALLOCATE PREPARE answer_stats;

SET @answer_duplicates_sql = IF(
  @has_answer_id = 1,
  'SELECT session_id, answer_id, COUNT(*) AS duplicate_count FROM interview_message WHERE answer_id IS NOT NULL GROUP BY session_id, answer_id HAVING COUNT(*) > 1 ORDER BY duplicate_count DESC, session_id',
  'SELECT ''answer_id'' AS column_name, ''NOT_PRESENT_NO_DUPLICATE_SCAN'' AS status'
);
PREPARE answer_duplicates FROM @answer_duplicates_sql;
EXECUTE answer_duplicates;
DEALLOCATE PREPARE answer_duplicates;

-- 4. submission_id 数据质量与重复组合。
SET @has_submission_id = (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE() AND table_name = 'interview_message' AND column_name = 'submission_id'
);
SET @submission_stats_sql = IF(
  @has_submission_id = 1,
  'SELECT COUNT(*) AS total_rows, SUM(submission_id IS NULL) AS null_count, COALESCE(SUM(submission_id = ''''), 0) AS empty_string_count FROM interview_message',
  'SELECT ''submission_id'' AS column_name, ''NOT_PRESENT'' AS status'
);
PREPARE submission_stats FROM @submission_stats_sql;
EXECUTE submission_stats;
DEALLOCATE PREPARE submission_stats;

SET @submission_duplicates_sql = IF(
  @has_submission_id = 1,
  'SELECT session_id, submission_id, COUNT(*) AS duplicate_count FROM interview_message WHERE submission_id IS NOT NULL GROUP BY session_id, submission_id HAVING COUNT(*) > 1 ORDER BY duplicate_count DESC, session_id',
  'SELECT ''submission_id'' AS column_name, ''NOT_PRESENT_NO_DUPLICATE_SCAN'' AS status'
);
PREPARE submission_duplicates FROM @submission_duplicates_sql;
EXECUTE submission_duplicates;
DEALLOCATE PREPARE submission_duplicates;

-- 判读规则：任何 duplicate_count 结果或 empty_string_count > 0 都应先停止迁移并人工处理。
-- MySQL UNIQUE 允许多个 NULL；旧客户端被规范化为 NULL，不会互相冲突。
