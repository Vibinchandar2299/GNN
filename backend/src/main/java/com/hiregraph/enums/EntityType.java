package com.hiregraph.enums;

public enum EntityType {
    APPLICATION,
    STUDENT,
    COMPANY,
    JOB,
    SKILL;

    public static EntityType fromString(String val) {
        if (val == null) return null;
        return EntityType.valueOf(val.trim().toUpperCase());
    }
}
