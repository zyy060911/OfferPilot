package com.zhimian.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 技能标签（面试画像标签化出题用）
 */
@Data
@TableName("skill_tag")
public class SkillTag {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;
    private String category;
    private String description;
    private Integer sortOrder;
    private LocalDateTime createTime;
}
