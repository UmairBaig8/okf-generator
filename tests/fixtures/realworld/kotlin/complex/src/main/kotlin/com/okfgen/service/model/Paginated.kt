package com.okfgen.service.model

/**
 * Generic paginated wrapper for list responses.
 */
data class Paginated<T>(
    val items: List<T>,
    val total: Int,
    val page: Int,
    val pageSize: Int
)
