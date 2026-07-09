package com.zhimian.service;

import com.zhimian.dto.FollowUpResponse;
import org.springframework.stereotype.Component;

/**
 * 规则化追问生成器（V2 精简版）。
 * <p>
 * V2 将 >= 15 字的追问决策权移交给 DeepSeek，本类只负责两件事：
 * <ol>
 *   <li>回答过短 → 提示展开回答</li>
 *   <li>AI 不可用/调用失败 → 生成一个通用追问兜底</li>
 * </ol>
 */
@Component
public class RuleBasedFollowUpGenerator {

    /** 回答（去空白后）短于该长度视为过短 */
    public static final int MIN_ANSWER_LENGTH = 15;

    private static final String SOURCE_RULE = "RULE";

    /** 回答过短时的追问 */
    public FollowUpResponse tooShortResponse() {
        return FollowUpResponse.of(
                "你的回答比较简短，能否详细说说你的思路或做法？",
                SOURCE_RULE,
                "回答过于简短，缺少具体细节");
    }

    /** AI 不可用或调用失败时的通用兜底追问 */
    public FollowUpResponse defaultResponse() {
        return FollowUpResponse.of(
                "针对刚才的回答，能否进一步说明你在实现过程中遇到的难点以及是如何解决的？",
                SOURCE_RULE,
                "AI 不可用或调用失败，使用规则兜底追问");
    }
}
