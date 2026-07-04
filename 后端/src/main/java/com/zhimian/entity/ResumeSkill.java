package com.zhimian.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("resume_skill")
public class ResumeSkill {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;
    private Long fileId;
    private String skillName;
    private LocalDateTime createTime;
}
