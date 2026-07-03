import Foundation

/// Protocol defining CRUD operations for a generic entity type.
public protocol Repository<T> {
    associatedtype T: Codable & Comparable
    func save(_ entity: T) -> T
    func findById(_ id: String) -> T?
    func findAll() -> [T]
    func deleteById(_ id: String) -> Bool
    func count() -> Int
}

/// Possible states of a user account lifecycle.
public enum AccountStatus: String, Codable {
    case active
    case suspended
    case archived
}

/// In-memory implementation of Repository for User entities.
public class UserRepository: Repository {
    public typealias T = User
    private var store: [String: User] = [:]

    public init() {}

    public func save(_ user: User) -> User {
        store[user.id] = user
        return user
    }

    public func findById(_ id: String) -> User? {
        store[id]
    }

    public func findAll() -> [User] {
        Array(store.values)
    }

    public func deleteById(_ id: String) -> Bool {
        store.removeValue(forKey: id) != nil
    }

    public func count() -> Int {
        store.count
    }

    /// Returns users sorted by creation date with pagination.
    public func listPaginated(page: Int, pageSize: Int) -> Paginated<User> {
        let all = store.values.sorted()
        let total = all.count
        let start = max(0, (page - 1) * pageSize)
        let items = Array(all.dropFirst(start).prefix(pageSize))
        return Paginated(items: items, total: total, page: page, pageSize: pageSize)
    }
}
