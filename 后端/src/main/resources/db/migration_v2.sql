-- =====================================================================
-- V2 迁移：时间控制面试 + 体验式题目 + Q&A 历史
-- 执行方式：USE zhimian; source migration_v2.sql;
-- =====================================================================

-- 1. 面试会话表：新增时长字段
ALTER TABLE interview_session
    ADD COLUMN duration_seconds INT DEFAULT 1800 COMMENT '面试时长(秒)，默认30分钟';

-- 2. 面试消息表：新增题目类型和参考答案字段
ALTER TABLE interview_message
    ADD COLUMN question_type VARCHAR(20) DEFAULT 'SKILL' COMMENT '题目类型: SKILL=题库 EXPERIENCE=体验式';

ALTER TABLE interview_message
    ADD COLUMN reference_answer TEXT COMMENT '参考答案(体验式题目专用，供追问对比)';
