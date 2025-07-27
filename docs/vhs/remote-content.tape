Output docs/vhs/remote-content.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create structure using remote content" Enter
Type "cat > remote-demo.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - .gitignore:" Enter
Type "      file: github://github/gitignore/main/Python.gitignore" Enter
Type "  - LICENSE:" Enter
Type "      file: https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt" Enter
Type "  - README.md:" Enter
Type "      content: |" Enter
Type "        # {{@ project_name @}}" Enter
Type "        " Enter
Type "        This project uses remote content from GitHub." Enter
Type "variables:" Enter
Type "  - project_name:" Enter
Type "      description: 'Project name'" Enter
Type "      default: 'RemoteDemo'" Enter
Type "EOF" Enter
Sleep 3
Type "" Enter
Type "# Generate project with remote content" Enter
Type "struct generate remote-demo.yaml ./remote-project" Enter
Sleep 8
Type "" Enter
Type "# Check downloaded content" Enter
Type "echo 'Generated files:' && ls -la remote-project/" Enter
Type "echo && echo 'First few lines of .gitignore:' && head -10 remote-project/.gitignore" Enter
Sleep 5
