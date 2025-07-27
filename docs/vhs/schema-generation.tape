Output docs/vhs/schema-generation.gif

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

Type "# Generate JSON schema for available structures" Enter
Type "struct generate-schema" Enter
Sleep 5
Type "" Enter
Type "# Save schema to file for IDE integration" Enter
Type "struct generate-schema -o struct-schema.json" Enter
Sleep 3
Type "" Enter
Type "# Check the generated schema" Enter
Type "echo 'Schema file created:' && ls -la struct-schema.json" Enter
Type "echo && echo 'Available structures in schema:' && jq -r '.definitions.PluginList.enum[]' struct-schema.json | head -10" Enter
Sleep 5
Type "" Enter
Type "# Schema can be used in VS Code for autocompletion" Enter
Type "echo 'Add to your .struct.yaml files for IDE support:'" Enter
Type "echo '# yaml-language-server: \$schema=./struct-schema.json'" Enter
Sleep 3
