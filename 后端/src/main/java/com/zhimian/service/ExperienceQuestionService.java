package com.zhimian.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.zhimian.config.AiProperties;
import com.zhimian.entity.Resume;
import com.zhimian.service.ai.DeepSeekClient;
import com.zhimian.service.ai.ExperienceQuestionPromptBuilder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 体验式题目服务：调用 DeepSeek 根据简历画像 + 岗位生成情景化面试题。
 * AI 调用失败时回退到简单模板题目。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ExperienceQuestionService {

    private final AiProperties aiProps;
    private final DeepSeekClient deepSeekClient;
    private final ExperienceQuestionPromptBuilder promptBuilder;

    /**
     * 生成一道体验式情景题 + 参考答案。
     *
     * @param position       目标岗位名
     * @param resume         候选人简历画像
     * @param askedQuestions 本场面试已问过的题目内容（用于避免重复）
     * @return 题目结果；AI 不可用时回退模板
     */
    public ExperienceQuestionResult generate(String position, Resume resume, List<String> askedQuestions) {
        if (aiProps.isUsable()) {
            JsonNode result = deepSeekClient.chatJson(
                    promptBuilder.systemPrompt(),
                    promptBuilder.userPrompt(
                            position,
                            resume != null ? resume.getSkills() : "",
                            resume != null ? resume.getKeywords() : "",
                            resume != null ? resume.getProjects() : "",
                            askedQuestions));
            if (result != null) {
                try {
                    String question = result.path("question").asText("");
                    String refAnswer = result.path("referenceAnswer").asText("");
                    String abilityTag = result.path("abilityTag").asText("综合能力");
                    if (!question.isBlank()) {
                        log.info("[体验题] DeepSeek生成成功, abilityTag={}", abilityTag);
                        return new ExperienceQuestionResult(question, refAnswer, abilityTag);
                    }
                } catch (Exception e) {
                    log.warn("[体验题] JSON解析失败: {}", e.getMessage());
                }
            }
        }
        // 回退到模板题目
        log.info("[体验题] AI不可用，回退模板");
        return fallbackQuestion(position, resume);
    }

    private ExperienceQuestionResult fallbackQuestion(String position, Resume resume) {
        String skills = (resume != null && resume.getSkills() != null) ? resume.getSkills() : "相关技术栈";
        String question = "请结合你在" + skills + "方面的实际项目经验，"
                + "谈一谈在「" + position + "」岗位上，你曾经遇到过的最大技术挑战是什么？"
                + "你是如何分析、设计并最终解决它的？请详细说明你的思考过程和技术方案。";
        String refAnswer = "候选人应能描述：1) 具体的项目背景和挑战；2) 分析过程和技术选型；"
                + "3) 实施方案和关键决策；4) 最终成果和量化效果。";
        return new ExperienceQuestionResult(question, refAnswer, "综合能力");
    }

    @Data
    public static class ExperienceQuestionResult {
        private final String question;
        private final String referenceAnswer;
        private final String abilityTag;
    }
}
