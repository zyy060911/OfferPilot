package com.zhimian.config;

import com.documents4j.api.IConverter;
import com.documents4j.job.LocalConverter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.File;
import java.util.concurrent.TimeUnit;

/**
 * documents4j LocalConverter 配置。
 * <p>
 * 创建并管理 LocalConverter 单例（整个 JVM 只需一个实例，因为它与外部 MS Word 进程通信）。
 * 应用关闭时通过 {@code destroyMethod = "shutDown"} 优雅退出 Word。
 * <p>
 * 前提条件：
 * <ul>
 *   <li>本机需安装 Microsoft Word 2007 或更高版本</li>
 *   <li>启动前确保没有其他 Word 窗口正在运行</li>
 *   <li>仅支持 Windows（VBS 脚本桥接）</li>
 * </ul>
 */
@Slf4j
@Configuration
public class ConverterConfiguration {

    @Value("${export.timeout-seconds:30}")
    private int timeoutSeconds;

    /**
     * 创建 LocalConverter Bean。
     * 单线程 workerPool（演示/学生项目规模足够），
     * destroyMethod 确保 Spring 关闭时自动调用 shutDown 终止 Word 进程。
     */
    @Bean(destroyMethod = "shutDown")
    public IConverter localConverter() {
        File tempDir = new File(System.getProperty("java.io.tmpdir"), "offerpilot-docs4j");
        if (!tempDir.exists()) {
            tempDir.mkdirs();
        }

        IConverter converter = LocalConverter.builder()
                .baseFolder(tempDir)
                .workerPool(1, 1, 1, TimeUnit.MINUTES)
                .processTimeout(timeoutSeconds, TimeUnit.SECONDS)
                .build();

        log.info("documents4j LocalConverter 已启动（临时目录={}, 超时={}s）",
                tempDir.getAbsolutePath(), timeoutSeconds);
        return converter;
    }
}
