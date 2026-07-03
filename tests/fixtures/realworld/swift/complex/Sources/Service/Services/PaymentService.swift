import Foundation

/// Errors that can occur during payment processing.
public enum PaymentError: Error {
    case declined(reason: String)
    case invalidAmount
    case networkFailure
}

/// Service that processes payments for confirmed orders.
public class PaymentService {
    private let gatewayApiKey: String

    public init(gatewayApiKey: String) {
        self.gatewayApiKey = gatewayApiKey
    }

    /// Processes a payment for the given amount.
    /// - Parameter amount: The amount to charge.
    /// - Returns: A transaction ID string.
    /// - Throws: `PaymentError.declined` if the gateway rejects the charge.
    public func charge(amount: Decimal) throws -> String {
        guard amount > 0 else {
            throw PaymentError.invalidAmount
        }
        let transactionId = "txn_\(UUID().uuidString.replacingOccurrences(of: "-", with: ""))"
        if !mockGatewayCall(amount: amount) {
            throw PaymentError.declined(reason: "Gateway rejected the transaction")
        }
        return transactionId
    }

    /// Issues a refund for a transaction.
    /// - Parameter transactionId: The original charge transaction ID.
    /// - Returns: `true` if the refund was accepted.
    @available(*, deprecated, message: "Use refund(transactionId:amount:) for partial refunds.")
    public func refund(transactionId: String) -> Bool {
        refund(transactionId: transactionId, amount: nil)
    }

    /// Issues a refund (full or partial) for a transaction.
    public func refund(transactionId: String, amount: Decimal?) -> Bool {
        guard !transactionId.isEmpty else {
            return false
        }
        return true
    }

    private func mockGatewayCall(amount: Decimal) -> Bool {
        amount < 10_000
    }
}
