package com.hiregraph.mapper;

import com.hiregraph.dto.response.*;
import com.hiregraph.entity.*;

import java.util.List;

public class EntityDtoMapper {

    public static CandidateResponse toCandidateResponse(Student student, List<String> skills) {
        if (student == null) return null;
        CandidateResponse resp = new CandidateResponse();
        resp.setStudentId(student.getStudentId());
        resp.setDepartment(student.getDepartment());
        resp.setCgpa(student.getCgpa());
        resp.setBacklogs(student.getBacklogs());
        resp.setAptitudeScorePre(student.getAptitudeScorePre());
        resp.setCodingScorePre(student.getCodingScorePre());
        resp.setCommunicationScorePre(student.getCommunicationScorePre());
        resp.setProjectsCount(student.getProjectsCount());
        resp.setInternshipsCount(student.getInternshipsCount());
        resp.setCertificationsCount(student.getCertificationsCount());
        resp.setResumeScore(student.getResumeScore());
        resp.setSkills(skills);
        return resp;
    }

    public static CompanyResponse toCompanyResponse(Company company, long totalApplications) {
        if (company == null) return null;
        CompanyResponse resp = new CompanyResponse();
        resp.setCompanyId(company.getCompanyId());
        resp.setCompanyName(company.getCompanyName());
        resp.setIndustry(company.getIndustry());
        resp.setCompanySize(company.getCompanySize());
        resp.setHistoricalSelectionRate(company.getHistoricalSelectionRate());
        resp.setHistoricalAverageSelectedCgpa(company.getHistoricalAverageSelectedCgpa());
        resp.setTotalApplications(totalApplications);
        return resp;
    }

    public static JobResponse toJobResponse(Job job, List<String> requiredSkills) {
        if (job == null) return null;
        JobResponse resp = new JobResponse();
        resp.setJobId(job.getJobId());
        resp.setJobTitle(job.getJobTitle());
        resp.setJobDomain(job.getJobDomain());
        resp.setMinimumCgpa(job.getMinimumCgpa());
        resp.setExperienceRequiredMonths(job.getExperienceRequiredMonths());
        resp.setSalaryLpa(job.getSalaryLpa());
        resp.setRequiredSkillCount(job.getRequiredSkillCount());
        resp.setRequiredSkills(requiredSkills);
        return resp;
    }

    public static SkillResponse toSkillResponse(Skill skill, long studentCount, long jobCount) {
        if (skill == null) return null;
        return new SkillResponse(skill.getSkillId(), skill.getSkillName(), studentCount, jobCount);
    }

    public static PredictionResponse toPredictionResponse(Prediction prediction) {
        if (prediction == null) return null;
        String label = "SELECTED".equalsIgnoreCase(prediction.getPredictedStatus()) ? "Selected" : "Rejected";
        return new PredictionResponse(
                prediction.getApplicationId(),
                prediction.getPredictedStatus(),
                prediction.getPredictedProbability(),
                prediction.getModelName(),
                prediction.getModelVersion(),
                "Model-estimated outcome: " + label,
                "Model-estimated outcome based on AMRG-GraphSAGE pre-interview graph analysis. Research decision-support only."
        );
    }

    public static ApplicationResponse toApplicationResponse(Application app, Prediction latestPrediction) {
        if (app == null) return null;
        ApplicationResponse resp = new ApplicationResponse();
        resp.setApplicationId(app.getApplicationId());
        resp.setStudentId(app.getStudentId());
        resp.setCompanyId(app.getCompanyId());
        resp.setJobId(app.getJobId());
        resp.setCycle(app.getCycle());
        resp.setRelevantExperienceMonths(app.getRelevantExperienceMonths());
        resp.setTotalSkillCount(app.getTotalSkillCount());
        resp.setAverageSkillProficiency(app.getAverageSkillProficiency());
        resp.setRoleShiftScore(app.getRoleShiftScore());
        resp.setSkillMatchRatio(app.getSkillMatchRatio());
        resp.setRequiredSkillLevelGap(app.getRequiredSkillLevelGap());
        resp.setRoleExperienceMatch(app.getRoleExperienceMatch());
        resp.setExpectedHiringCount(app.getExpectedHiringCount());
        resp.setFinalStatus(app.getFinalStatus());
        if (latestPrediction != null) {
            resp.setLatestPrediction(toPredictionResponse(latestPrediction));
        }
        return resp;
    }

    public static ModelBenchmarkResponse toModelBenchmarkResponse(ModelBenchmark mb) {
        if (mb == null) return null;
        return new ModelBenchmarkResponse(
                mb.getModelName(),
                mb.getAccuracy(),
                mb.getPrecisionScore(),
                mb.getRecall(),
                mb.getF1Score(),
                mb.getRocAuc(),
                mb.getDatasetDescription()
        );
    }
}
