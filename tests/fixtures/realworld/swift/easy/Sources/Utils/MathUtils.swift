import Foundation

/// Returns the smaller of two integers.
public func min(_ a: Int, _ b: Int) -> Int {
    a < b ? a : b
}

/// Returns the larger of two integers.
public func max(_ a: Int, _ b: Int) -> Int {
    a > b ? a : b
}

/// Clamps a value between a minimum and maximum.
public func clamp<T: Comparable>(_ value: T, low: T, high: T) -> T {
    if value < low { return low }
    if value > high { return high }
    return value
}

/// Represents a 2D coordinate.
public struct Point {
    public var x: Double
    public var y: Double

    public init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }

    /// Computes Euclidean distance to another point.
    public func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return sqrt(dx * dx + dy * dy)
    }
}
