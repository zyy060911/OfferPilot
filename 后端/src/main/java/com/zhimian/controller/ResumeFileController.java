package com.zhimian.controller;

import com.zhimian.common.Result;
import com.zhimian.dto.ResumeFileProfileResponse;
import com.zhimian.service.ResumeFileService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/resume")
@RequiredArgsConstructor
public class ResumeFileController {

    private final ResumeFileService resumeFileService;

    @PostMapping("/upload")
    public Result<ResumeFileProfileResponse> upload(@RequestParam("file") MultipartFile file) {
        return Result.success(resumeFileService.uploadAndAnalyze(file));
    }

    @GetMapping("/file-profile")
    public Result<ResumeFileProfileResponse> fileProfile() {
        return Result.success(resumeFileService.getFileProfile());
    }
}
