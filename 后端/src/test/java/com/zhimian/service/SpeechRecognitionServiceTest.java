package com.zhimian.service;

import com.zhimian.common.BizException;
import com.zhimian.config.AsrProperties;
import com.zhimian.config.UserContext;
import com.zhimian.dto.SpeechTranscriptResponse;
import com.zhimian.entity.InterviewSession;
import com.zhimian.mapper.InterviewSessionMapper;
import com.zhimian.service.ai.ZhipuAsrClient;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class SpeechRecognitionServiceTest {

    @AfterEach
    void clearUserContext() {
        UserContext.clear();
    }

    @Test
    void validatesWavAndTranscribesOwnedOngoingSession() {
        InterviewSessionMapper mapper = mock(InterviewSessionMapper.class);
        ZhipuAsrClient client = mock(ZhipuAsrClient.class);
        AsrProperties properties = properties();
        SpeechRecognitionService service = new SpeechRecognitionService(mapper, client, properties);

        InterviewSession session = new InterviewSession();
        session.setId(7L);
        session.setUserId(12L);
        session.setStatus("ONGOING");
        when(mapper.selectById(7L)).thenReturn(session);
        UserContext.set(12L, "STUDENT");

        byte[] wav = wav(16000);
        MockMultipartFile file = new MockMultipartFile(
                "file", "answer.wav", "audio/wav", wav);
        SpeechTranscriptResponse expected =
                new SpeechTranscriptResponse("测试回答", "request-1", "glm-asr-2512", 1.0);
        when(client.transcribe(any(byte[].class), eq("interview-7.wav"), eq(1.0)))
                .thenReturn(expected);

        SpeechTranscriptResponse actual = service.transcribe(7L, file);

        assertEquals("测试回答", actual.getText());
        verify(client).transcribe(any(byte[].class), eq("interview-7.wav"), eq(1.0));
    }

    @Test
    void rejectsSessionOwnedByAnotherUser() {
        InterviewSessionMapper mapper = mock(InterviewSessionMapper.class);
        ZhipuAsrClient client = mock(ZhipuAsrClient.class);
        SpeechRecognitionService service =
                new SpeechRecognitionService(mapper, client, properties());

        InterviewSession session = new InterviewSession();
        session.setId(7L);
        session.setUserId(99L);
        session.setStatus("ONGOING");
        when(mapper.selectById(7L)).thenReturn(session);
        UserContext.set(12L, "STUDENT");

        MockMultipartFile file = new MockMultipartFile(
                "file", "answer.wav", "audio/wav", wav(16000));

        assertThrows(BizException.class, () -> service.transcribe(7L, file));
    }

    private static AsrProperties properties() {
        AsrProperties properties = new AsrProperties();
        properties.setMaxFileSize(10 * 1024 * 1024);
        properties.setMaxDurationSeconds(30);
        return properties;
    }

    private static byte[] wav(int sampleCount) {
        byte[] bytes = new byte[44 + sampleCount * 2];
        writeAscii(bytes, 0, "RIFF");
        write32(bytes, 4, 36 + sampleCount * 2);
        writeAscii(bytes, 8, "WAVE");
        writeAscii(bytes, 12, "fmt ");
        write32(bytes, 16, 16);
        write16(bytes, 20, 1);
        write16(bytes, 22, 1);
        write32(bytes, 24, 16000);
        write32(bytes, 28, 32000);
        write16(bytes, 32, 2);
        write16(bytes, 34, 16);
        writeAscii(bytes, 36, "data");
        write32(bytes, 40, sampleCount * 2);
        return bytes;
    }

    private static void writeAscii(byte[] bytes, int offset, String text) {
        for (int i = 0; i < text.length(); i++) {
            bytes[offset + i] = (byte) text.charAt(i);
        }
    }

    private static void write16(byte[] bytes, int offset, int value) {
        bytes[offset] = (byte) value;
        bytes[offset + 1] = (byte) (value >> 8);
    }

    private static void write32(byte[] bytes, int offset, int value) {
        bytes[offset] = (byte) value;
        bytes[offset + 1] = (byte) (value >> 8);
        bytes[offset + 2] = (byte) (value >> 16);
        bytes[offset + 3] = (byte) (value >> 24);
    }
}
