package com.hiregraph.service;

import com.hiregraph.dto.response.ApplicationResponse;
import com.hiregraph.entity.Application;
import com.hiregraph.entity.Prediction;
import com.hiregraph.exception.ResourceNotFoundException;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.ApplicationRepository;
import com.hiregraph.repository.PredictionRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class ApplicationService {

    private final ApplicationRepository applicationRepository;
    private final PredictionRepository predictionRepository;

    public ApplicationService(ApplicationRepository applicationRepository,
                              PredictionRepository predictionRepository) {
        this.applicationRepository = applicationRepository;
        this.predictionRepository = predictionRepository;
    }

    public Page<ApplicationResponse> getApplications(Integer cycle, Integer finalStatus, Pageable pageable) {
        Page<Application> page;
        if (cycle != null && finalStatus != null) {
            page = applicationRepository.findByCycleAndFinalStatus(cycle, finalStatus, pageable);
        } else if (cycle != null) {
            page = applicationRepository.findByCycle(cycle, pageable);
        } else if (finalStatus != null) {
            page = applicationRepository.findByFinalStatus(finalStatus, pageable);
        } else {
            page = applicationRepository.findAll(pageable);
        }

        return page.map(app -> {
            Prediction pred = predictionRepository.findTopByApplicationIdOrderByCreatedAtDesc(app.getApplicationId()).orElse(null);
            return EntityDtoMapper.toApplicationResponse(app, pred);
        });
    }

    public ApplicationResponse getApplicationById(String applicationId) {
        Application app = applicationRepository.findByApplicationId(applicationId.trim())
                .orElseThrow(() -> new ResourceNotFoundException("Application with ID '" + applicationId + "' not found."));

        Prediction pred = predictionRepository.findTopByApplicationIdOrderByCreatedAtDesc(app.getApplicationId()).orElse(null);
        return EntityDtoMapper.toApplicationResponse(app, pred);
    }
}
