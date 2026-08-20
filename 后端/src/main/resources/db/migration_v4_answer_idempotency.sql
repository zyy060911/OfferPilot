-- V4：回答自动提交幂等。
-- 本项目采用手动 SQL 迁移；应用启动不会自动执行本文件。
-- 执行前必须先在目标测试库运行 precheck_v4_answer_idempotency.sql，并确认无冲突。
-- 建议：mysql -u <user> -p <database> < migration_v4_answer_idempotency.sql
-- ALTER TABLE 会获取 metadata lock，并需扫描/构建唯一索引；大表请安排维护窗口并先评估耗时。
-- 本脚本是一次性版本迁移，重复执行会明确报“列/索引已存在”，不要忽略错误继续执行。
-- 新增列均可空，因此兼容历史记录和不携带幂等键的旧客户端。
ALTER TABLE interview_message
    ADD COLUMN answer_id VARCHAR(64) NULL COMMENT '客户端完整回答ID(仅考生回答)' AFTER question_id,
    ADD COLUMN submission_id VARCHAR(64) NULL COMMENT '客户端提交幂等ID(仅考生回答)' AFTER answer_id;

ALTER TABLE interview_message
    ADD UNIQUE KEY uk_session_answer (session_id, answer_id),
    ADD UNIQUE KEY uk_session_submission (session_id, submission_id);
