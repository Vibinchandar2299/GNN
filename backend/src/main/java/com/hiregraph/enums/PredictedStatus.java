package com.hiregraph.enums;

public enum PredictedStatus {
    SELECTED,
    REJECTED;

    public static PredictedStatus fromInt(int status) {
        return status == 1 ? SELECTED : REJECTED;
    }

    public int toInt() {
        return this == SELECTED ? 1 : 0;
    }
}
