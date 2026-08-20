package com.zhimian.common;

import org.junit.jupiter.api.Test;
import org.springframework.dao.DuplicateKeyException;

import static org.junit.jupiter.api.Assertions.assertEquals;

class GlobalExceptionHandlerTest {

    @Test
    void duplicateKeyReturnsStableConflictInsteadOf500() {
        Result<Void> result = new GlobalExceptionHandler()
                .handleDuplicateKey(new DuplicateKeyException("sensitive database detail"));
        assertEquals(409, result.getCode());
        assertEquals("请求已处理或正在处理中，请勿重复提交", result.getMessage());
    }
}
