package com.zhimian.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.google.common.util.concurrent.Striped;
import com.zhimian.dto.AnswerRequest;
import com.zhimian.entity.InterviewMessage;
import com.zhimian.mapper.InterviewMessageMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.concurrent.locks.Lock;

/**
 * 回答持久化幂等边界。进程内条带锁避免同实例竞争，数据库唯一索引负责跨实例兜底。
 */
@Component
@RequiredArgsConstructor
public class AnswerSubmissionGuard {
    private static final Striped<Lock> LOCKS = Striped.lock(256);
    private final InterviewMessageMapper messageMapper;

    public boolean saveCandidateAnswer(Long sessionId, int round, AnswerRequest req, String abilityTag) {
        String key = idempotencyKey(req);
        if (key == null) {
            messageMapper.insert(buildMessage(sessionId, round, req, abilityTag));
            return true;
        }
        Lock lock = LOCKS.get(sessionId + ":" + key);
        lock.lock();
        try {
            if (findExisting(sessionId, req) != null) return false;
            // 数据库唯一键仍是最终保障。异常不在事务内部吞掉，避免 rollback-only 后伪装成功。
            messageMapper.insert(buildMessage(sessionId, round, req, abilityTag));
            return true;
        } finally {
            lock.unlock();
        }
    }

    public InterviewMessage findExisting(Long sessionId, AnswerRequest req) {
        if (idempotencyKey(req) == null) return null;
        LambdaQueryWrapper<InterviewMessage> query = new LambdaQueryWrapper<InterviewMessage>()
                .eq(InterviewMessage::getSessionId, sessionId)
                .eq(InterviewMessage::getRole, "CANDIDATE")
                .eq(InterviewMessage::getMsgType, "ANSWER")
                .and(wrapper -> {
                    boolean hasAnswerId = notBlank(req.getAnswerId());
                    if (hasAnswerId) wrapper.eq(InterviewMessage::getAnswerId, req.getAnswerId());
                    if (notBlank(req.getSubmissionId())) {
                        if (hasAnswerId) wrapper.or();
                        wrapper.eq(InterviewMessage::getSubmissionId, req.getSubmissionId());
                    }
                })
                .last("LIMIT 1");
        return messageMapper.selectOne(query);
    }

    private InterviewMessage buildMessage(Long sessionId, int round, AnswerRequest req, String abilityTag) {
        InterviewMessage msg = new InterviewMessage();
        msg.setSessionId(sessionId);
        msg.setQuestionId(req.getQuestionId());
        msg.setRoundNo(round);
        msg.setRole("CANDIDATE");
        msg.setMsgType("ANSWER");
        msg.setContent(req.getAnswer());
        msg.setAbilityTag(abilityTag);
        msg.setAnswerId(trimToNull(req.getAnswerId()));
        msg.setSubmissionId(trimToNull(req.getSubmissionId()));
        return msg;
    }

    private String idempotencyKey(AnswerRequest req) {
        String answerId = trimToNull(req.getAnswerId());
        return answerId != null ? answerId : trimToNull(req.getSubmissionId());
    }

    private boolean notBlank(String value) { return value != null && !value.isBlank(); }
    private String trimToNull(String value) { return notBlank(value) ? value.trim() : null; }
}
