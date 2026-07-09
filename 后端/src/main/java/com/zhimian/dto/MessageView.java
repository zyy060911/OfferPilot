package com.zhimian.dto;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 消息视图：用于返回会话问答历史。
 */
@Data
public class MessageView {

    private Long id;
    private Long sessionId;
    private Long questionId;
    private Integer roundNo;
    private String role;
    private String msgType;
    private String questionType;
    private String content;
    private String abilityTag;
    private LocalDateTime createTime;
}
