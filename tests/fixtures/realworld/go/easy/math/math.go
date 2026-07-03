// Package math provides basic arithmetic and statistical operations.
package math

// Pi is an approximation of pi.
const Pi = 3.14159

// E is the base of natural logarithms.
const E float64 = 2.71828

// DefaultPrecision controls rounding precision across math functions.
var DefaultPrecision = 6

// Min returns the smaller of two integers.
func Min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Max returns the larger of two integers.
func Max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// Clamp restricts a value to the range [low, high].
func Clamp(val, low, high int) int {
	if val < low {
		return low
	}
	if val > high {
		return high
	}
	return val
}

// Abs returns the absolute value of an integer.
func Abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

// Sum returns the sum of a slice of integers.
func Sum(nums []int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

// mean is an unexported helper that computes the arithmetic mean.
func mean(nums []int) float64 {
	if len(nums) == 0 {
		return 0
	}
	return float64(Sum(nums)) / float64(len(nums))
}
