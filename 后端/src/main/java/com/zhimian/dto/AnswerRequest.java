package com.zhimian.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 提交回答请求
 */
@Data
public class AnswerRequest {

    /** 题库题目必传；体验题（AI 生成）可传 null 或 0 */
    private Long questionId;

    /** 客户端一次完整回答的稳定标识；旧客户端可不传。 */
    @Size(max = 64)
    private String answerId;

    /** 同一次网络提交的幂等标识；重试时保持不变。 */
    @Size(max = 64)
    private String submissionId;

    @NotBlank(message = "回答内容不能为空")
    private String answer;
}
