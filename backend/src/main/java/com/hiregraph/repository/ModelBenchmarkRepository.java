package com.hiregraph.repository;

import com.hiregraph.entity.ModelBenchmark;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ModelBenchmarkRepository extends JpaRepository<ModelBenchmark, Long> {
    Optional<ModelBenchmark> findByModelName(String modelName);
}
