Output docs/demo-short.gif
Set Shell "bash"
Set FontSize 32
Set Width 1080
Set Height 1920
Set Theme "Dracula"
Set Padding 100
Set TypingSpeed 15ms

# ── YouTube Short — Branded, mobile-safe ──

# Scene 1: Brand splash (safe zone: ~rows 4-12)
Type "clear"
Enter
Sleep 100ms
Type "                               OKF Generator"
Sleep 400ms
Enter
Sleep 100ms
Type "                     The knowledge layer for AI coding agents"
Sleep 300ms
Enter
Sleep 200ms
Type ""
Enter
Sleep 100ms
Type "                    17 languages  |  Zero LLM  |  Offline"
Sleep 400ms
Enter
Sleep 800ms
Type "clear"
Enter
Sleep 100ms

# Scene 2: generate
Type "okf generate . ./okf_bundle"
Sleep 150ms
Enter
Sleep 2.5s

# Scene 3: lookup
Type "clear"
Enter
Sleep 80ms
Type "okf lookup WorldBankConnector"
Sleep 150ms
Enter
Sleep 2s

# Scene 4: diff
Type "clear"
Enter
Sleep 80ms
Type "okf diff ./v1 ./v2 --compact"
Sleep 150ms
Enter
Sleep 2s

# Scene 5: visualize + mcp
Type "clear"
Enter
Sleep 80ms
Type "okf visualize ./okf_bundle viz.html"
Sleep 150ms
Enter
Sleep 1.5s
Type "okf mcp ./okf_bundle --port 4567"
Sleep 100ms
Enter
Sleep 1.8s

# Scene 6: install agent + exit
Type "clear"
Enter
Sleep 80ms
Type "okf install claude"
Sleep 150ms
Enter
Sleep 1.2s
Type "pip install okf-generator"
Sleep 200ms
Enter
Sleep 1.5s
