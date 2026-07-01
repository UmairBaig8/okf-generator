Output docs/demo.gif
Set FontSize 16
Set Width 1100
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 20ms

# Activate venv and cd to sample_repo
Hide
Type "source dev_wspace/.venv/bin/activate"
Enter
Type "cd /tmp/sample_repo"
Enter
Type "clear"
Enter
Show
Sleep 400ms

# Scene 1: generate
Type "okf generate . ./okf_bundle"
Sleep 300ms
Enter
Sleep 3s

# Scene 2: lookup a class
Type "clear"
Enter
Sleep 300ms
Type "okf lookup PaymentService"
Sleep 400ms
Enter
Sleep 3s

# Scene 3: lookup dependencies
Type "clear"
Enter
Sleep 300ms
Type "okf lookup --type Dependency --compact"
Sleep 400ms
Enter
Sleep 2.5s

# Scene 4: install for all agents
Type "clear"
Enter
Sleep 300ms
Type "okf install all"
Sleep 400ms
Enter
Sleep 2s
