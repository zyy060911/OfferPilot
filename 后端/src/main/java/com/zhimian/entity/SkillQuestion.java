package com.zhimian.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 技能标签题目（含详细参考答案，按标签组织的通用题库）
 */
@Data
@TableName("skill_question")
public class SkillQuestion {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 题干 */
    private String content;
    /** 参考答案（详细版，用于评分参考） */
    private String referenceAnswer;
    /** 答案关键词（、分隔，供规则引擎匹配） */
    private String answerKeywords;
    /** 难度: 1入门 2中等 3困难 */
    private Integer difficulty;
    /** 追问引导（面试官可选的追问方向） */
    private String followupGuide;
    private LocalDateTime createTime;
}
