Output docs/demo.gif
Set Shell "bash"
Set FontSize 16
Set Width 1100
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 25ms

# ── Setup: activate venv, cd to sample repo, clean old bundle ──
Hide
Type "source dev_wspace/.venv/bin/activate && cd /tmp/sample_repo && rm -rf ./okf_bundle && clear"
Enter
Show
Sleep 500ms

# Scene 1: generate the bundle
Type "okf generate . ./okf_bundle"
Sleep 400ms
Enter
Sleep 3s

# Scene 2: look up a class
Type "clear"
Enter
Sleep 400ms
Type "okf lookup PaymentService"
Sleep 400ms
Enter
Sleep 3s

# Scene 3: list dependencies
Type "clear"
Enter
Sleep 400ms
Type "okf lookup --type Dependency --compact"
Sleep 400ms
Enter
Sleep 2.5s

# Scene 4: install for agents
Type "clear"
Enter
Sleep 400ms
Type "okf install all"
Sleep 400ms
Enter
Sleep 2s
