package com.zhimian.service.ai;

import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 体验式题目 Prompt 构建器。
 * 根据简历画像和岗位，让 DeepSeek 生成一个情景化面试题 + 参考答案。
 */
@Component
public class ExperienceQuestionPromptBuilder {

    public String systemPrompt() {
        return "你是一名资深技术面试官，擅长根据候选人的简历背景和目标岗位设计情景化面试题目。\n"
                + "你的任务：\n"
                + "1. 仔细分析候选人的技能标签、项目经历和关键词。\n"
                + "2. 结合目标岗位要求，设计一个具体的情景化/经历式面试题。\n"
                + "   - 题目应让候选人结合自己的项目经验或假设的工作场景来回答。\n"
                + "   - 题目应有足够深度，能考察候选人的实际工程能力。\n"
                + "   - 避免泛泛的「请介绍一个项目」，要具体到技术决策、架构权衡、难点攻克等。\n"
                + "3. 同一场面试中，每次出题必须换个角度，不要反复问同一个技术点。\n"
                + "   - 如果候选人简历里有多个项目或多个技能，优先选之前没问过的。\n"
                + "   - 即使是同一个项目，也要从不同的技术维度切入（上次问故障处理，这次就问架构设计或性能优化）。\n"
                + "4. 同时生成该题目的参考答案（简练要点即可，2-4句话）。\n"
                + "5. 确定该题目考察的能力标签（如：系统设计、问题排查、性能优化、团队协作等）。\n"
                + "\n"
                + "你必须严格按以下 JSON 格式输出（不要加 markdown 代码块标记）：\n"
                + "{\"question\": \"题目内容\", \"referenceAnswer\": \"参考答案\", \"abilityTag\": \"能力标签\"}";
    }

    /**
     * 生成体验题（无已问题目上下文）
     */
    public String userPrompt(String position, String skills, String keywords, String projects) {
        return userPrompt(position, skills, keywords, projects, List.of());
    }

    /**
     * 生成体验题（带上已问过的题目，避免重复）
     */
    public String userPrompt(String position, String skills, String keywords, String projects,
                             List<String> askedQuestions) {
        StringBuilder sb = new StringBuilder();
        sb.append("【目标岗位】").append(safe(position)).append("\n");
        sb.append("【候选人技能】").append(safe(skills)).append("\n");
        sb.append("【候选人关键词】").append(safe(keywords)).append("\n");
        sb.append("【候选人项目经历】").append(safe(projects)).append("\n");

        if (askedQuestions != null && !askedQuestions.isEmpty()) {
            sb.append("【本次面试已问过的题目（严禁出类似的题）】\n");
            for (int i = 0; i < askedQuestions.size(); i++) {
                sb.append("  ").append(i + 1).append(". ").append(askedQuestions.get(i)).append("\n");
            }
            sb.append("注意：上面这些题目已经问过了，你必须换一个全新的角度或技术点，不得重复。\n");
        }

        sb.append("请生成一个情景化面试题目并输出 JSON：");
        return sb.toString();
    }

    private String safe(String s) {
        return s == null || s.isBlank() ? "未提供" : s.trim();
    }
}
