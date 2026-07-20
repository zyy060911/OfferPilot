package com.zhimian.export;

import com.documents4j.api.DocumentType;
import com.documents4j.api.IConverter;
import com.zhimian.common.BizException;
import com.zhimian.dto.ReportDetailResponse;
import com.zhimian.dto.ReportDimensionView;
import com.zhimian.service.ReportService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * 报告导出服务：将面试报告渲染为 HTML，再通过 documents4j (MS Word) 转换为 PDF 或 DOCX。
 * <p>
 * 当前使用 programmatic HTML 构建（不依赖外部模板引擎），后续可替换为 Freemarker/Thymeleaf。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ExportService {

    private final ReportService reportService;
    private final IConverter converter;

    private static final DateTimeFormatter DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    // ---------- 公开方法 ----------

    /**
     * 导出报告为 PDF 或 DOCX。
     *
     * @param reportId 报告 ID
     * @param format   "pdf" 或 "docx"
     * @return 生成文件的字节数组
     */
    public byte[] export(Long reportId, String format) {
        // 1. 获取报告数据（含归属校验）
        ReportDetailResponse report = reportService.getDetail(reportId);

        // 2. 渲染 HTML
        String html = renderHtml(report);

        // 3. PDF / DOCX: 写入临时 HTML 文件后通过 documents4j 转换为目标格式
        File htmlFile = writeTempHtml(reportId, html);
        try {
            return convertHtml(htmlFile, format);
        } finally {
            if (!htmlFile.delete()) {
                htmlFile.deleteOnExit();
            }
        }
    }

    // ---------- HTML 渲染 ----------

    /**
     * 将报告数据渲染为完整的 HTML5 文档（内联 CSS，可直接被 Word 打开并转换）。
     */
    String renderHtml(ReportDetailResponse report) {
        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html>\n");
        sb.append("<html lang=\"zh-CN\">\n<head>\n");
        sb.append("<meta charset=\"UTF-8\">\n");
        sb.append("<title>面试能力评估报告</title>\n");
        sb.append("<style>\n");
        sb.append("  * { margin: 0; padding: 0; box-sizing: border-box; }\n");
        sb.append("  body {\n");
        sb.append("    font-family: \"Microsoft YaHei\", \"PingFang SC\", \"SimHei\", sans-serif;\n");
        sb.append("    color: #1e293b; background: #fff; padding: 48px 56px;\n");
        sb.append("    line-height: 1.7; max-width: 800px; margin: 0 auto;\n");
        sb.append("  }\n");
        sb.append("  .header { text-align: center; border-bottom: 3px solid #2563eb; padding-bottom: 22px; margin-bottom: 32px; }\n");
        sb.append("  .header h1 { font-size: 28px; color: #0b1e39; margin-bottom: 8px; }\n");
        sb.append("  .header .meta { font-size: 13px; color: #64748b; }\n");
        sb.append("  .score-card { text-align: center; margin: 28px 0 32px; }\n");
        sb.append("  .score-value { font-size: 56px; font-weight: 900; color: #2563eb; line-height: 1.1; }\n");
        sb.append("  .score-band { display: inline-block; margin-top: 6px; padding: 4px 18px; border-radius: 20px;\n");
        sb.append("    font-size: 14px; font-weight: 700; color: #fff; background: #2563eb; }\n");
        sb.append("  .summary { background: #f8faff; border-left: 4px solid #2563eb; padding: 14px 18px;\n");
        sb.append("    border-radius: 6px; margin-bottom: 30px; font-size: 14px; color: #334155; }\n");
        sb.append("  h2 { font-size: 18px; color: #0f2b5c; margin: 28px 0 12px; padding-bottom: 6px;\n");
        sb.append("    border-bottom: 1px solid #e2e8f0; }\n");
        sb.append("  table.dims { width: 100%; border-collapse: collapse; margin: 12px 0 24px; }\n");
        sb.append("  table.dims th { background: #2563eb; color: #fff; padding: 8px 10px; font-size: 13px; text-align: center; }\n");
        sb.append("  table.dims td { padding: 8px 10px; border: 1px solid #e2e8f0; font-size: 13px; }\n");
        sb.append("  table.dims td.name { font-weight: 700; white-space: nowrap; }\n");
        sb.append("  .bar-wrap { background: #eef2f6; border-radius: 8px; height: 10px; width: 100%; }\n");
        sb.append("  .bar-fill { height: 10px; border-radius: 8px; }\n");
        sb.append("  .bar-excellent { background: #22c55e; }\n");
        sb.append("  .bar-good { background: #3b82f6; }\n");
        sb.append("  .bar-pass { background: #f59e0b; }\n");
        sb.append("  .bar-weak { background: #ef4444; }\n");
        sb.append("  ul { margin-left: 20px; margin-bottom: 16px; }\n");
        sb.append("  ul li { font-size: 14px; margin-bottom: 6px; color: #475569; }\n");
        sb.append("  .footer { margin-top: 44px; padding-top: 14px; border-top: 1px solid #e2e8f0;\n");
        sb.append("    text-align: center; font-size: 12px; color: #94a3b8; }\n");
        sb.append("  @media print { body { padding: 0; } }\n");
        sb.append("</style>\n</head>\n<body>\n");

        // --- 页头 ---
        sb.append("<div class=\"header\">\n");
        sb.append("  <h1>面试能力评估报告</h1>\n");
        sb.append("  <p class=\"meta\">岗位：").append(escape(report.getJobName())).append(" &nbsp;|&nbsp;");
        sb.append("报告编号：").append(report.getReportId()).append(" &nbsp;|&nbsp;");
        sb.append("生成时间：").append(LocalDateTime.now().format(DATE_FMT)).append("</p>\n");
        sb.append("</div>\n");

        // --- 总分 ---
        String band = scoreBand(report.getTotalScore());
        sb.append("<div class=\"score-card\">\n");
        sb.append("  <div class=\"score-value\">").append(report.getTotalScore()).append("</div>\n");
        sb.append("  <div class=\"score-band\">").append(band).append("</div>\n");
        sb.append("</div>\n");

        // --- 综合评价 ---
        if (report.getSummary() != null && !report.getSummary().isEmpty()) {
            sb.append("<div class=\"summary\">").append(escape(report.getSummary())).append("</div>\n");
        }

        // --- 五维能力得分表 ---
        sb.append("<h2>一、五维能力得分</h2>\n");
        sb.append("<table class=\"dims\">\n");
        sb.append("  <tr><th>评估维度</th><th>得分</th><th>等级</th><th>得分条形图</th></tr>\n");
        List<ReportDimensionView> dims = report.getDimensions();
        if (dims != null) {
            for (ReportDimensionView d : dims) {
                double score = d.getScore() != null ? d.getScore().doubleValue() : 0;
                String barClass = barClass(score);
                sb.append("  <tr>");
                sb.append("<td class=\"name\">").append(escape(d.getDimension())).append("</td>");
                sb.append("<td style=\"text-align:center;font-weight:700;\">").append(d.getScore()).append("</td>");
                sb.append("<td style=\"text-align:center;\">").append(escape(d.getLevel())).append("</td>");
                sb.append("<td><div class=\"bar-wrap\"><div class=\"bar-fill ").append(barClass)
                        .append("\" style=\"width:").append((int) score).append("%;\"></div></div></td>");
                sb.append("</tr>\n");
            }
        }
        sb.append("</table>\n");

        // --- 五维解释 ---
        if (dims != null) {
            for (ReportDimensionView d : dims) {
                if (d.getExplanation() != null && !d.getExplanation().isEmpty()) {
                    sb.append("<p style=\"font-size:13px;color:#64748b;margin:2px 0 8px;\">");
                    sb.append("<strong>").append(escape(d.getDimension())).append("：</strong>");
                    sb.append(escape(d.getExplanation())).append("</p>\n");
                }
            }
        }

        // --- 优势 ---
        List<String> strengths = report.getStrengths();
        if (strengths != null && !strengths.isEmpty()) {
            sb.append("<h2>二、表现优势</h2>\n<ul>\n");
            for (String s : strengths) {
                sb.append("  <li>").append(escape(s)).append("</li>\n");
            }
            sb.append("</ul>\n");
        }

        // --- 不足 ---
        List<String> weaknesses = report.getWeaknesses();
        if (weaknesses != null && !weaknesses.isEmpty()) {
            sb.append("<h2>三、待改进项</h2>\n<ul>\n");
            for (String w : weaknesses) {
                sb.append("  <li>").append(escape(w)).append("</li>\n");
            }
            sb.append("</ul>\n");
        }

        // --- 建议 ---
        List<String> suggestions = report.getSuggestions();
        if (suggestions != null && !suggestions.isEmpty()) {
            sb.append("<h2>四、提升建议</h2>\n<ul>\n");
            for (String s : suggestions) {
                sb.append("  <li>").append(escape(s)).append("</li>\n");
            }
            sb.append("</ul>\n");
        }

        // --- 页脚 ---
        sb.append("<div class=\"footer\">由智面幻境 · OfferPilot AI 模拟面试系统自动生成 &nbsp;|&nbsp;");
        sb.append(LocalDateTime.now().format(DATE_FMT)).append("</div>\n");

        sb.append("</body>\n</html>");
        return sb.toString();
    }

    // ---------- 文档转换 ----------

    /**
     * 调用 documents4j 将 HTML 文件转换为目标格式。
     */
    private byte[] convertHtml(File htmlFile, String format) {
        try {
            File tmpDir = htmlFile.getParentFile();
            String ext = "pdf".equals(format) ? ".pdf" : ".docx";
            File targetFile = File.createTempFile("report-", ext, tmpDir);

            DocumentType targetType = "pdf".equals(format) ? DocumentType.PDF : DocumentType.DOCX;

            boolean ok = converter.convert(htmlFile)
                    .as(DocumentType.HTML)
                    .to(targetFile)
                    .as(targetType)
                    .execute();

            if (!ok) {
                throw new ExportException("文档转换失败：documents4j 返回失败状态。" +
                        "请确认本机已安装 Microsoft Word 2007+ 且未在启动前打开 Word。");
            }

            byte[] bytes = Files.readAllBytes(targetFile.toPath());

            // 清理临时目标文件
            if (!targetFile.delete()) {
                targetFile.deleteOnExit();
            }
            return bytes;
        } catch (ExportException e) {
            throw e;
        } catch (Exception e) {
            log.error("文档转换异常 reportId={} format={}", htmlFile.getName(), format, e);
            throw new ExportException("文档转换失败：" + e.getMessage() +
                    "。请确认本机已安装 Microsoft Word 2007+。");
        }
    }

    // ---------- 辅助 ----------

    /** 写入临时 HTML 文件并返回 File 引用 */
    private File writeTempHtml(Long reportId, String html) {
        try {
            File tmpDir = new File(System.getProperty("java.io.tmpdir"), "offerpilot-docs4j");
            if (!tmpDir.exists()) {
                tmpDir.mkdirs();
            }
            File htmlFile = File.createTempFile("report-" + reportId + "-", ".html", tmpDir);
            Files.write(htmlFile.toPath(), html.getBytes(StandardCharsets.UTF_8));
            log.debug("临时 HTML 已写入 {}", htmlFile.getAbsolutePath());
            return htmlFile;
        } catch (IOException e) {
            throw new ExportException("写入临时文件失败：" + e.getMessage());
        }
    }

    /** HTML 文本转义 */
    static String escape(String text) {
        if (text == null) return "";
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace("\"", "&quot;").replace("'", "&#39;");
    }

    /** 分数 → 等级文字 */
    static String scoreBand(BigDecimal score) {
        if (score == null) return "未评估";
        double s = score.doubleValue();
        if (s >= 85) return "优秀";
        if (s >= 70) return "良好";
        if (s >= 60) return "合格";
        return "待提升";
    }

    /** 分数 → 条形图 CSS 类 */
    static String barClass(double score) {
        if (score >= 85) return "bar-excellent";
        if (score >= 70) return "bar-good";
        if (score >= 60) return "bar-pass";
        return "bar-weak";
    }
}
