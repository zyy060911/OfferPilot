package com.zhimian.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 题目-标签关联（多对多：同题可关联多标签）
 */
@Data
@TableName("skill_question_tag_rel")
public class SkillQuestionTagRel {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long questionId;
    private Long tagId;
}
