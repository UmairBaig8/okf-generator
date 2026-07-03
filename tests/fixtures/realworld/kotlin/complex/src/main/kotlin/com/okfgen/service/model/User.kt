package com.okfgen.service.model

import java.time.Instant
import java.util.UUID

/**
 * Represents a user in the system.
 */
data class User(
    val id: String = UUID.randomUUID().toString(),
    val email: String,
    val displayName: String? = null,
    val isActive: Boolean = true,
    val createdAt: Instant = Instant.now()
) : Comparable<User> {
    /**
     * Deactivates the user account.
     */
    fun deactivate(): User = copy(isActive = false)

    override fun compareTo(other: User): Int =
        this.createdAt.compareTo(other.createdAt)
}

/**
 * Possible account status values.
 */
enum class AccountStatus {
    ACTIVE,
    SUSPENDED,
    ARCHIVED
}
