package com.zhimian.db;

import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DatabaseMigrationConventionTest {

    @Test
    void v4ManualMigrationAndPrecheckArePackaged() throws Exception {
        ClassPathResource migration = new ClassPathResource("db/migration_v4_answer_idempotency.sql");
        ClassPathResource precheck = new ClassPathResource("db/precheck_v4_answer_idempotency.sql");
        assertTrue(migration.exists());
        assertTrue(precheck.exists());
        String sql = migration.getContentAsString(StandardCharsets.UTF_8);
        assertTrue(sql.contains("ADD COLUMN answer_id VARCHAR(64) NULL"));
        assertTrue(sql.contains("UNIQUE KEY uk_session_answer (session_id, answer_id)"));
        assertTrue(sql.contains("UNIQUE KEY uk_session_submission (session_id, submission_id)"));
    }

    @Test
    void projectDoesNotPretendManualScriptsAreAutoDiscovered() throws Exception {
        String pom = Files.readString(Path.of("pom.xml"), StandardCharsets.UTF_8).toLowerCase();
        String application = new ClassPathResource("application.yml")
                .getContentAsString(StandardCharsets.UTF_8).toLowerCase();
        assertFalse(application.contains("sql:\n    init:"));
        assertFalse(application.contains("flyway:"));
        assertFalse(application.contains("liquibase:"));
        assertFalse(pom.contains("flyway-core"));
        assertFalse(pom.contains("liquibase-core"));
    }

    @Test
    void cleanSchemaMatchesV4EntityColumnsAndIndexes() throws Exception {
        String schema = new ClassPathResource("db/schema.sql").getContentAsString(StandardCharsets.UTF_8);
        assertTrue(schema.contains("answer_id     VARCHAR(64)"));
        assertTrue(schema.contains("submission_id VARCHAR(64)"));
        assertTrue(schema.contains("UNIQUE KEY uk_session_answer (session_id, answer_id)"));
        assertTrue(schema.contains("UNIQUE KEY uk_session_submission (session_id, submission_id)"));
    }
}
