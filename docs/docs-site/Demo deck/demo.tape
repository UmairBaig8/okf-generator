Output docs/demo.gif
Set Shell "bash"
Set FontSize 16
Set Width 1100
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 25ms

# ── Setup ──
Hide
Type "source dev_wspace/.venv/bin/activate && cd /tmp/sample_repo && rm -rf ./okf_bundle && clear"
Enter
Show
Sleep 500ms

# Scene 1: generate
Type "okf generate . ./okf_bundle"
Sleep 400ms
Enter
Sleep 2.5s

# Scene 2: lookup a class
Type "clear"
Enter
Sleep 300ms
Type "okf lookup PaymentService"
Sleep 400ms
Enter
Sleep 2.5s

# Scene 3: list dependencies
Type "clear"
Enter
Sleep 300ms
Type "okf lookup --deps"
Sleep 400ms
Enter
Sleep 2s

# Scene 4: --version with banner
Type "clear"
Enter
Sleep 300ms
Type "okf --version"
Sleep 300ms
Enter
Sleep 1.5s

# Scene 5: visualize + serve
Type "clear"
Enter
Sleep 300ms
Type "okf visualize ./okf_bundle viz.html"
Sleep 400ms
Enter
Sleep 2s
