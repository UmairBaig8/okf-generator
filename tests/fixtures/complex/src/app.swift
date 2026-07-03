import Foundation

/// Greeting service with user management.
public class Greeter {
    private let greeting: String
    private var names: [String]

    /// Creates a new Greeter instance.
    public init(greeting: String) {
        self.greeting = greeting
        self.names = []
    }

    /// Adds a name to the greeting list.
    public func addName(_ name: String) {
        names.append(name)
    }

    /// Returns a greeting for all added names.
    public func greetAll() -> String {
        names.map { "\(greeting), \($0)!" }.joined(separator: "\n")
    }
}
