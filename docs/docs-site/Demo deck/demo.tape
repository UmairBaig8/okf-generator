Output docs/demo.gif
Set Shell "bash"
Set FontSize 14
Set Width 540
Set Height 960
Set Theme "Dracula"
Set Padding 16
Set TypingSpeed 20ms

# ── Setup ──
Hide
Type "source dev_wspace/.venv/bin/activate && cd /tmp/sample_repo && rm -rf ./okf_bundle && clear"
Enter
Show
Sleep 300ms

# Scene 1: generate
Type "okf generate . ./okf_bundle"
Sleep 300ms
Enter
Sleep 3s

# Scene 2: lookup a class
Type "clear"
Enter
Sleep 200ms
Type "okf lookup WorldBankConnector"
Sleep 300ms
Enter
Sleep 2.5s

# Scene 3: diff two bundles
Type "clear"
Enter
Sleep 200ms
Type "okf diff ./bundle_v1 ./bundle_v2 --compact"
Sleep 300ms
Enter
Sleep 2.5s

# Scene 4: visualize HTML
Type "clear"
Enter
Sleep 200ms
Type "okf visualize ./okf_bundle viz.html"
Sleep 300ms
Enter
Sleep 2s

# Scene 5: mcp server
Type "clear"
Enter
Sleep 200ms
Type "okf mcp ./okf_bundle --port 4567"
Sleep 300ms
Enter
Sleep 2.5s

# Scene 6: export training pairs
Type "clear"
Enter
Sleep 200ms
Type "okf pairs ./okf_bundle ./train.jsonl"
Sleep 300ms
Enter
Sleep 2s

# Scene 7: install agent
Type "clear"
Enter
Sleep 200ms
Type "okf install claude"
Sleep 300ms
Enter
Sleep 2s
