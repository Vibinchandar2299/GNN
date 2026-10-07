package com.hiregraph.service;

import com.hiregraph.dto.response.HiringTrendResponse;
import com.hiregraph.repository.ApplicationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class AnalyticsService {

    private final ApplicationRepository applicationRepository;

    public AnalyticsService(ApplicationRepository applicationRepository) {
        this.applicationRepository = applicationRepository;
    }

    public List<HiringTrendResponse> getTrends() {
        List<Integer> cycles = applicationRepository.findDistinctCycles();
        List<HiringTrendResponse> trends = new ArrayList<>();

        for (Integer cycle : cycles) {
            long total = applicationRepository.countByCycle(cycle);
            long selected = applicationRepository.countByCycleAndFinalStatus(cycle, 1);
            long rejected = applicationRepository.countByCycleAndFinalStatus(cycle, 0);
            double rate = total > 0 ? (double) selected / total : 0.0;

            trends.add(new HiringTrendResponse(
                    cycle,
                    total,
                    selected,
                    rejected,
                    Math.round(rate * 10000.0) / 10000.0
            ));
        }

        return trends;
    }
}
