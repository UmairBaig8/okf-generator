package com.okfgen.utils

/**
 * Returns the smaller of two integers.
 */
fun min(a: Int, b: Int): Int = if (a < b) a else b

/**
 * Returns the larger of two integers.
 */
fun max(a: Int, b: Int): Int = if (a > b) a else b

/**
 * Clamps a value between a minimum and maximum.
 */
fun <T : Comparable<T>> clamp(value: T, low: T, high: T): T {
    return when {
        value < low -> low
        value > high -> high
        else -> value
    }
}

/**
 * Represents a 2D coordinate.
 */
data class Point(val x: Double, val y: Double) {
    /**
     * Computes Euclidean distance to another point.
     */
    fun distanceTo(other: Point): Double {
        val dx = x - other.x
        val dy = y - other.y
        return kotlin.math.sqrt(dx * dx + dy * dy)
    }
}
