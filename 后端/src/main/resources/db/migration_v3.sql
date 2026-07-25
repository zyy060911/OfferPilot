-- =====================================================================
-- V3 迁移：文件简历上传、段落分析与技能提取
-- 可重复执行，不会删除或覆盖已有数据。
-- =====================================================================

USE zhimian;

CREATE TABLE IF NOT EXISTS resume_file (
    id           BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '文件ID',
    user_id      BIGINT       NOT NULL                    COMMENT '用户ID',
    filename     VARCHAR(255)  NOT NULL                    COMMENT '原始文件名',
    file_size    BIGINT                                   COMMENT '文件大小(字节)',
    content_type VARCHAR(100)                             COMMENT 'MIME类型',
    file_data    LONGBLOB      NOT NULL                    COMMENT '文件内容',
    create_time  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_user (user_id)
) ENGINE=InnoDB COMMENT='上传的简历文件';

CREATE TABLE IF NOT EXISTS resume_paragraph (
    id             BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '段落ID',
    user_id        BIGINT       NOT NULL                    COMMENT '用户ID',
    file_id        BIGINT       NOT NULL                    COMMENT '文件ID',
    seq_no         INT          NOT NULL                    COMMENT '段落顺序',
    content        TEXT         NOT NULL                    COMMENT '段落内容',
    paragraph_type VARCHAR(20)  NOT NULL DEFAULT 'GENERAL' COMMENT '段落类型: GENERAL/PROJECT',
    create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_user (user_id),
    KEY idx_file (file_id)
) ENGINE=InnoDB COMMENT='简历段落分析结果';

CREATE TABLE IF NOT EXISTS resume_skill (
    id           BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '技能ID',
    user_id      BIGINT       NOT NULL                    COMMENT '用户ID',
    file_id      BIGINT       NOT NULL                    COMMENT '文件ID',
    skill_name   VARCHAR(100) NOT NULL                    COMMENT '技能名称',
    create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_skill (user_id, skill_name),
    KEY idx_file (file_id)
) ENGINE=InnoDB COMMENT='简历技能提取结果';
