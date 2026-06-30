# demo.tape — records docs/demo.gif
#
# Prerequisites before running:
#   1. Install vhs: https://github.com/charmbracelet/vhs#installation
#   2. Install okf-generator: pip install okf-generator
#   3. Have a small sample project to scan — e.g. create ./demo_project/
#      with a couple of .py files containing a class or two. Keep it
#      small (3-5 files) so the output fits on screen without scrolling.
#
# Run with:
#   vhs demo.tape
#
# Output: docs/demo.gif (auto-created relative to where you run vhs)

Output docs/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1100
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 60ms

# Make sure we start clean
Hide
Type "source dev_wspace/.venv/bin/activate"
Enter
Type "cd /tmp/okf_demo"
Enter
Type "clear"
Enter
Show

# Step 1: generate the bundle
Type "okf generate . ./okf_bundle"
Sleep 500ms
Enter
Sleep 2s

# Step 2: look up a concept
Type "okf lookup APIClient"
Sleep 500ms
Enter
Sleep 2.5s

# Step 3: filter by dependency
Type "okf lookup --type Dependency --compact"
Sleep 500ms
Enter
Sleep 2.5s

# Hold the final frame before looping
Sleep 2s
