package com.okfgen.utils

/**
 * Checks whether the given string is a valid email address.
 */
fun isValidEmail(email: String): Boolean {
    val pattern = Regex("""^[^\s@]+@[^\s@]+\.[^\s@]+$""")
    return pattern.matches(email)
}

/**
 * Truncates a string to the specified maximum length.
 */
fun truncate(text: String, maxLen: Int): String {
    if (text.length <= maxLen) return text
    return text.take(maxOf(0, maxLen - 3)) + "..."
}

/**
 * Converts a CamelCase string to snake_case.
 */
fun toSnakeCase(camel: String): String {
    val sb = StringBuilder()
    for ((i, char) in camel.withIndex()) {
        if (char.isUpperCase()) {
            if (i > 0) sb.append('_')
            sb.append(char.lowercaseChar())
        } else {
            sb.append(char)
        }
    }
    return sb.toString()
}
