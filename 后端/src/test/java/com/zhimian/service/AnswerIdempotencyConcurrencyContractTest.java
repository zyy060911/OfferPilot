package com.zhimian.service;

import com.zhimian.mapper.InterviewSessionMapper;
import org.apache.ibatis.annotations.Select;
import org.junit.jupiter.api.Test;
import org.springframework.transaction.annotation.Transactional;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * 多实例正确性契约的静态测试。真实 InnoDB 并发/锁等待仍需在隔离测试库验证。
 */
class AnswerIdempotencyConcurrencyContractTest {

    @Test
    void answerProcessingHasTransactionBoundary() throws Exception {
        Method method = InterviewFlowService.class.getMethod("answer", Long.class, com.zhimian.dto.AnswerRequest.class);
        assertNotNull(method.getAnnotation(Transactional.class));
    }

    @Test
    void sessionMapperUsesDatabaseRowLock() throws Exception {
        Method method = InterviewSessionMapper.class.getMethod("selectByIdForUpdate", Long.class);
        Select select = method.getAnnotation(Select.class);
        assertNotNull(select);
        assertTrue(String.join(" ", select.value()).toUpperCase().contains("FOR UPDATE"));
    }
}
