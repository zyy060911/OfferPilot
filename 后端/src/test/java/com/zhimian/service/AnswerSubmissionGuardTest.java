package com.zhimian.service;

import com.zhimian.dto.AnswerRequest;
import com.zhimian.entity.InterviewMessage;
import com.zhimian.mapper.InterviewMessageMapper;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DuplicateKeyException;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class AnswerSubmissionGuardTest {

    @Test
    void duplicateAnswerIdDoesNotInsertAnotherCandidateMessage() {
        InterviewMessageMapper mapper = mock(InterviewMessageMapper.class);
        AnswerSubmissionGuard guard = new AnswerSubmissionGuard(mapper);
        AnswerRequest request = request("answer-1", "submission-1");
        when(mapper.selectOne(any())).thenReturn(new InterviewMessage());

        assertFalse(guard.saveCandidateAnswer(3L, 1, request, "Java"));
        verify(mapper, never()).insert(any(InterviewMessage.class));
    }

    @Test
    void databaseUniqueConstraintProtectsCrossInstanceRace() {
        InterviewMessageMapper mapper = mock(InterviewMessageMapper.class);
        AnswerSubmissionGuard guard = new AnswerSubmissionGuard(mapper);
        AnswerRequest request = request("answer-2", "submission-2");
        when(mapper.selectOne(any())).thenReturn(null);
        when(mapper.insert(any(InterviewMessage.class))).thenThrow(new DuplicateKeyException("duplicate"));

        assertThrows(DuplicateKeyException.class,
                () -> guard.saveCandidateAnswer(3L, 1, request, "Java"));
    }

    @Test
    void legacyRequestWithoutIdempotencyKeyRemainsCompatible() {
        InterviewMessageMapper mapper = mock(InterviewMessageMapper.class);
        AnswerSubmissionGuard guard = new AnswerSubmissionGuard(mapper);
        AnswerRequest request = request(null, null);

        assertTrue(guard.saveCandidateAnswer(3L, 1, request, "Java"));
        verify(mapper).insert(any(InterviewMessage.class));
    }

    @Test
    void blankKeysAreNormalizedToNullForLegacyClients() {
        InterviewMessageMapper mapper = mock(InterviewMessageMapper.class);
        AnswerSubmissionGuard guard = new AnswerSubmissionGuard(mapper);
        AnswerRequest request = request("  ", "");

        assertTrue(guard.saveCandidateAnswer(3L, 1, request, "Java"));
        verify(mapper).insert(org.mockito.ArgumentMatchers.<InterviewMessage>argThat(message ->
                message.getAnswerId() == null && message.getSubmissionId() == null));
    }

    private AnswerRequest request(String answerId, String submissionId) {
        AnswerRequest request = new AnswerRequest();
        request.setQuestionId(8L);
        request.setAnswer("是");
        request.setAnswerId(answerId);
        request.setSubmissionId(submissionId);
        return request;
    }
}
