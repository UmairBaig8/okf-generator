// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "OKFGenSwiftService",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor", from: "4.89.0"),
    ],
    targets: [
        .target(
            name: "Service",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
            ]
        ),
    ]
)
