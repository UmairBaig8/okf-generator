Output docs/demo-short.gif
Set Shell "bash"
Set FontSize 18
Set Width 1080
Set Height 1920
Set Theme "Dracula"
Set Padding 24
Set TypingSpeed 18ms

# ── YouTube Short — no setup, straight to action ──

# Scene 1: generate (hook — show the CLI in action immediately)
Type "okf generate . ./okf_bundle"
Sleep 200ms
Enter
Sleep 2.5s

# Scene 2: lookup a class
Type "clear"
Enter
Sleep 100ms
Type "okf lookup WorldBankConnector"
Sleep 200ms
Enter
Sleep 2s

# Scene 3: diff
Type "clear"
Enter
Sleep 100ms
Type "okf diff ./v1 ./v2 --compact"
Sleep 200ms
Enter
Sleep 2s

# Scene 4: visualize
Type "clear"
Enter
Sleep 100ms
Type "okf visualize ./okf_bundle viz.html"
Sleep 200ms
Enter
Sleep 1.5s

# Scene 5: mcp server
Type "clear"
Enter
Sleep 100ms
Type "okf mcp ./okf_bundle --port 4567"
Sleep 200ms
Enter
Sleep 2s

# Scene 6: install agent
Type "clear"
Enter
Sleep 100ms
Type "okf install claude"
Sleep 200ms
Enter
Sleep 1.5s
