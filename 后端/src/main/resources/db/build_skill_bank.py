#!/usr/bin/env python3
"""读取 questions.json 并生成 seed_skill_bank.sql"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, 'questions_data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

TAGS = data['tags']
QUESTIONS = data['questions']

SQL = os.path.join(HERE, 'seed_skill_bank.sql')

def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")

with open(SQL, 'w', encoding='utf-8') as f:
    f.write("""-- ============================================================
-- 智面幻境 · 技能标签题库
-- {} 标签 × {} 题（含详细参考答案）
-- 用法：mysql -u root -p zhimian < seed_skill_bank.sql
-- Navicat：打开本文件 → 点击"运行" → 完成
-- 幂等：可重复执行（开头 DROP IF EXISTS）
-- ============================================================

USE zhimian;
DROP TABLE IF EXISTS skill_question_tag_rel;
DROP TABLE IF EXISTS skill_question;
DROP TABLE IF EXISTS skill_tag;

CREATE TABLE skill_tag (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名称',
    category VARCHAR(50) COMMENT '所属分类',
    description TEXT COMMENT '标签简介',
    sort_order INT NOT NULL DEFAULT 0,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='技能标签表';

CREATE TABLE skill_question (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '题目ID',
    content TEXT NOT NULL COMMENT '题干',
    reference_answer TEXT NOT NULL COMMENT '参考答案(详细版)',
    answer_keywords TEXT COMMENT '答案关键词',
    difficulty TINYINT NOT NULL DEFAULT 2 COMMENT '1入门 2中等 3困难',
    followup_guide TEXT COMMENT '追问引导',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_difficulty (difficulty)
) ENGINE=InnoDB COMMENT='技能题目表';

CREATE TABLE skill_question_tag_rel (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    question_id BIGINT NOT NULL COMMENT '题目ID',
    tag_id BIGINT NOT NULL COMMENT '标签ID',
    UNIQUE KEY uk_qt (question_id, tag_id),
    KEY idx_tag (tag_id)
) ENGINE=InnoDB COMMENT='题目-标签关联表';

""".format(len(TAGS), len(QUESTIONS)))

    # Insert tags
    for t in TAGS:
        f.write(f"INSERT INTO skill_tag (id, name, category, description, sort_order) VALUES ({t['id']}, '{esc(t['name'])}', '{esc(t['category'])}', '{esc(t['description'])}', {t['sort_order']});\n")

    f.write(f"\n-- ========== {len(QUESTIONS)} 道题目 ==========\n\n")

    # Insert questions
    for i, q in enumerate(QUESTIONS, 1):
        c = esc(q['content'])
        a = esc(q['answer'])
        kw = esc(q.get('keywords', ''))
        fu = esc(q.get('followup', ''))
        d = q.get('difficulty', 2)
        f.write(f"INSERT INTO skill_question (id, content, reference_answer, answer_keywords, difficulty, followup_guide) VALUES ({i}, '{c}', '{a}', '{kw}', {d}, '{fu}');\n")

    f.write(f"\n-- ========== 题目-标签关联 ==========\n\n")

    for i, q in enumerate(QUESTIONS, 1):
        for tid in q.get('tags', []):
            f.write(f"INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES ({i}, {tid});\n")

    f.write("""
-- ============================================================
-- 校验查询（可在 Navicat 中单独执行）
-- ============================================================

-- 每个标签下的题目数：
-- SELECT t.id, t.name, COUNT(r.question_id) AS q_count
-- FROM skill_tag t LEFT JOIN skill_question_tag_rel r ON t.id = r.tag_id
-- GROUP BY t.id, t.name ORDER BY t.sort_order;

-- 总题目数：SELECT COUNT(*) FROM skill_question;
-- 总关联数：SELECT COUNT(*) FROM skill_question_tag_rel;
-- 多标签题目：SELECT COUNT(*) FROM (SELECT question_id FROM skill_question_tag_rel GROUP BY question_id HAVING COUNT(*)>1) t;
""")

print(f"✅ 生成完成！{len(TAGS)} 标签, {len(QUESTIONS)} 题, 文件: {SQL}")
print(f"   大小: {os.path.getsize(SQL)/1024:.1f} KB")

# 统计
from collections import Counter
tc = Counter()
multi = 0
for q in QUESTIONS:
    tags = q.get('tags', [])
    for t in tags: tc[t] += 1
    if len(tags) > 1: multi += 1
print(f"   多标签题: {multi}/{len(QUESTIONS)}")
print("   各标签题数TOP15:")
for tid, cnt in tc.most_common(15):
    tag_name = next((t['name'] for t in TAGS if t['id'] == tid), f'#{tid}')
    print(f"     {tag_name}: {cnt}题")
