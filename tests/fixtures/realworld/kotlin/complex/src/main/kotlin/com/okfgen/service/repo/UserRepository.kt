package com.okfgen.service.repo

import com.okfgen.service.model.Paginated
import com.okfgen.service.model.User

/**
 * Generic repository interface for CRUD operations.
 */
interface Repository<T : Comparable<T>> {
    fun save(entity: T): T
    fun findById(id: String): T?
    fun findAll(): List<T>
    fun deleteById(id: String): Boolean
    fun count(): Int
}

/**
 * In-memory implementation of Repository for User entities.
 */
class UserRepository : Repository<User> {
    private val store = mutableMapOf<String, User>()

    override fun save(user: User): User {
        store[user.id] = user
        return user
    }

    override fun findById(id: String): User? = store[id]

    override fun findAll(): List<User> = store.values.toList()

    override fun deleteById(id: String): Boolean = store.remove(id) != null

    override fun count(): Int = store.size

    /**
     * Returns users sorted by creation date with pagination.
     */
    fun listPaginated(page: Int, pageSize: Int): Paginated<User> {
        val all = store.values.sorted()
        val total = all.size
        val start = maxOf(0, (page - 1) * pageSize)
        val items = all.drop(start).take(pageSize)
        return Paginated(items = items, total = total, page = page, pageSize = pageSize)
    }

    /**
     * Finds users by a predicate.
     */
    inline fun findBy(predicate: (User) -> Boolean): List<User> =
        store.values.filter(predicate)
}
