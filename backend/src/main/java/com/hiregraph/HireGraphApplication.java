package com.hiregraph;

import com.hiregraph.service.DataIngestionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class HireGraphApplication {

    private static final Logger log = LoggerFactory.getLogger(HireGraphApplication.class);

    public static void main(String[] args) {
        SpringApplication.run(HireGraphApplication.class, args);
    }

    @Bean
    public CommandLineRunner ingestionRunner(
            DataIngestionService ingestionService,
            @Value("${hiregraph.ingestion.auto-import:false}") boolean autoImport) {
        return args -> {
            boolean cliFlag = false;
            for (String arg : args) {
                if ("--ingest".equalsIgnoreCase(arg) || "--hiregraph.ingest=true".equalsIgnoreCase(arg)) {
                    cliFlag = true;
                    break;
                }
            }
            if (autoImport || cliFlag) {
                log.info("Automatic data ingestion triggered on startup...");
                ingestionService.ingestData(false);
            } else {
                log.info("HireGraph AI Backend ready. Data ingestion available via CLI flag (--ingest) or POST /api/v1/admin/ingest.");
            }
        };
    }
}
