import Foundation

/// Validates email addresses using a basic pattern.
public func isValidEmail(_ email: String) -> Bool {
    let pattern = #"^[^\s@]+@[^\s@]+\.[^\s@]+$"#
    return email.range(of: pattern, options: .regularExpression) != nil
}

/// Truncates a string to the specified maximum length, appending "..." if shortened.
public func truncate(_ text: String, maxLen: Int) -> String {
    if text.count <= maxLen {
        return text
    }
    return String(text.prefix(max(0, maxLen - 3))) + "..."
}

/// Converts a CamelCase string to snake_case.
public func toSnakeCase(_ camel: String) -> String {
    var result = ""
    for (i, char) in camel.enumerated() {
        if char.isUppercase {
            if i > 0 {
                result.append("_")
            }
            result.append(char.lowercased())
        } else {
            result.append(char)
        }
    }
    return result
}
