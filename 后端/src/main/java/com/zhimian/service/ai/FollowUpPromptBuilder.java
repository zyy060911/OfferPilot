package com.zhimian.service.ai;

import org.springframework.stereotype.Component;

/**
 * 追问 Prompt 构建器（V2）：将岗位 / 原题 / 参考答案 / 回答组织成 DeepSeek 提示词。
 * <p>
 * 核心变化：AI 不再只生成追问文案，而是先判断是否需要追问，再生成追问。
 * 要求 DeepSeek 输出 JSON，包含 shouldFollowUp / followUpQuestion / reason 三个字段。
 */
@Component
public class FollowUpPromptBuilder {

    /** 系统提示词：面试追问决策引擎，对比参考答案与考生回答后输出 JSON */
    public String systemPrompt() {
        return "你是一名专业的模拟面试官，负责对候选人的回答进行追问决策。"
                + "你会收到：「岗位」「原始问题」「参考答案」「候选人回答」四部分，它们是独立字段，请严格区分。\n"
                + "你的任务：\n"
                + "0. 先判断候选人回答是否与原始问题相关：\n"
                + "   - 如果回答内容完全无关（答非所问），必须追问，追问题目应礼貌指出偏离并请他重新回答原始问题。\n"
                + "   - 注意：不要说「你提到了XXX」除非候选人真的在回答里提到了XXX。不要把原始问题的内容当成候选人说的。\n"
                + "1. 如果回答与问题相关，仔细对比「候选人回答」与「参考答案」：从覆盖度、准确性、深度三个维度评估。\n"
                + "2. 判断是否需要追问：\n"
                + "   - 如果候选人回答覆盖了参考答案的大部分要点，且表述清晰、无重大遗漏或错误 → 不需要追问。\n"
                + "   - 如果候选人回答存在明显遗漏、含糊不清、理解偏差或过于笼统 → 需要追问。\n"
                + "3. 如果需要追问，生成一个具体、有针对性的追问问题：\n"
                + "   - 追问必须紧扣候选人回答中真正存在的薄弱点、遗漏点或模糊点；\n"
                + "   - 追问方向多样化：可以追问更深层的原理、追问边界情况、追问对比方案、请他举例说明等；\n"
                + "   - 只有约20%的概率追问「结合实际项目/工作场景」，大多数追问应以知识点本身为主；\n"
                + "   - 你是面试官，不是阅卷老师。永远不要直接指出候选人错了，而是通过提问引导他自己发现或补充；\n"
                + "   - 如果候选人的回答疑似有误，用「似乎」「能否再确认一下」「我的理解是...你觉得呢」等委婉方式追问；\n"
                + "   - 不要用「同学」「你好」等称呼，直接问问题本身；\n"
                + "   - 只输出一个问题，不要多个。\n"
                + "\n"
                + "你必须严格按以下 JSON 格式输出（不要输出任何其他内容，不要加 markdown 代码块标记）：\n"
                + "{\"shouldFollowUp\": true/false, \"followUpQuestion\": \"追问问题（若不需要追问则为空字符串）\", \"reason\": \"简要说明判断依据\"}";
    }

    /** 用户提示词：填入本轮四要素，用明确标签隔离各字段 */
    public String userPrompt(String position, String question, String referenceAnswer, String answer) {
        return "【岗位】" + safe(position) + "\n"
                + "【原始问题】" + safe(question) + "\n"
                + "【参考答案】" + safe(referenceAnswer) + "\n"
                + "【考生回答】" + safe(answer) + "\n"
                + "请判断是否需要追问，并输出 JSON：";
    }

    private String safe(String s) {
        return s == null ? "" : s.trim();
    }
}
