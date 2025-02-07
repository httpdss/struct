
Output docs/vhs/usage.gif

Set Theme "Monokai Vivid"
Set FontFamily "FiraCode Nerd Font"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create python virtual environment and install struct" Enter
Type "python3 -m venv .venv" Enter
Sleep 5
Type "source .venv/bin/activate" Enter
Sleep 5
Type "pip install git+https://github.com/httpdss/struct.git" Enter
Wait+Screen /Successfully/
Sleep 2
Type "# STRUCT is now installed and ready to use" Enter
Type "struct list" Enter
Sleep 10
