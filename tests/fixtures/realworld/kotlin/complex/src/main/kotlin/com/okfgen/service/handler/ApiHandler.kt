package com.okfgen.service.handler

import com.okfgen.service.model.User
import com.okfgen.service.repo.UserRepository

/**
 * Handles API requests for user operations.
 */
class ApiHandler(private val repo: UserRepository) {

    /**
     * Registers a new user.
     * @throws IllegalArgumentException if the email is already taken.
     */
    fun registerUser(email: String, displayName: String?): User {
        require(email.isNotBlank()) { "Email is required" }
        val existing = repo.findAll().firstOrNull { it.email == email }
        if (existing != null) {
            throw IllegalArgumentException("Email already registered")
        }
        val user = User(email = email, displayName = displayName)
        return repo.save(user)
    }

    /**
     * Retrieves a user by ID.
     * @return the user, or null if not found.
     */
    fun getUser(id: String): User? = repo.findById(id)

    /**
     * Lists all active users.
     */
    fun listActiveUsers(): List<User> =
        repo.findBy { it.isActive }

    /**
     * Deactivates a user account.
     */
    fun deactivateUser(id: String): User? {
        val user = repo.findById(id) ?: return null
        val updated = user.deactivate()
        repo.save(updated)
        return updated
    }
}
