import Foundation

/// Represents a user in the system.
public struct User: Identifiable, Comparable {
    public let id: String
    public var email: String
    public var displayName: String?
    public var isActive: Bool
    public let createdAt: Date

    public init(id: String, email: String, displayName: String? = nil) {
        self.id = id
        self.email = email
        self.displayName = displayName
        self.isActive = true
        self.createdAt = Date()
    }

    /// Deactivates the user account.
    public mutating func deactivate() {
        isActive = false
    }

    public static func < (lhs: User, rhs: User) -> Bool {
        lhs.createdAt < rhs.createdAt
    }
}
