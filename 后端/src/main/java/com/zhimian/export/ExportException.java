package com.zhimian.export;

/**
 * 报告导出异常（非受检），用于在导出流程中传递明确的业务错误信息。
 * 被 ExportController 捕获后转为 JSON 错误响应，避免触发全局异常处理器。
 */
public class ExportException extends RuntimeException {

    private final int code;

    public ExportException(int code, String message) {
        super(message);
        this.code = code;
    }

    public ExportException(String message) {
        this(500, message);
    }

    public int getCode() {
        return code;
    }
}
