// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "OKFGenSwiftUtils",
    platforms: [.macOS(.v14)],
    products: [
        .library(name: "Utils", targets: ["Utils"]),
    ],
    targets: [
        .target(name: "Utils"),
    ]
)
