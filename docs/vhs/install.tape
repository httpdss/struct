
Output docs/vhs/install.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# STRUCT Installation Demo"
Enter
Sleep 1s

Type "# Create python virtual environment and install struct"
Enter
Type "python3 -m venv .venv"
Enter
Sleep 2s

Type "source .venv/bin/activate"
Enter
Sleep 1s

Type "# Install STRUCT from GitHub"
Enter
Type "pip install git+https://github.com/httpdss/struct.git"
Enter
Sleep 5s

Type "# Verify installation"
Enter
Type "struct --help"
Enter
Sleep 2s

Type "# Check available structures"
Enter
Type "struct list"
Enter
Sleep 3s

Type "# STRUCT is now installed and ready to use!"
Enter
Sleep 2s
