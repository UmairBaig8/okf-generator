package com.okfgen

class Greeter(private val greeting: String) {
    private val names = mutableListOf<String>()

    fun addName(name: String) {
        names.add(name)
    }

    fun greetAll(): String =
        names.joinToString("\n") { "$greeting, $it!" }
}
