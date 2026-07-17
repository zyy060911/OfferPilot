package com.zhimian.dto;

import lombok.Data;

import java.util.List;

@Data
public class ResumeFileProfileResponse {

    private String rawText;
    private List<String> skills;
    private List<String> projects;
    private String filename;
    private Long fileId;
}
