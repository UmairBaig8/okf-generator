plugins {
    kotlin("jvm") version "1.9.22"
}

group = "com.okfgen.service"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("com.google.code.gson:gson:2.10.1")
}
