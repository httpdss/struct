Output docs/vhs/mappings-demo.gif

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

Type "# Create mappings file for environment variables" Enter
Type "cat > mappings.yaml << 'EOF'" Enter
Type "mappings:" Enter
Type "  environments:" Enter
Type "    dev:" Enter
Type "      database_url: 'postgres://localhost:5432/myapp_dev'" Enter
Type "      debug: true" Enter
Type "    prod:" Enter
Type "      database_url: 'postgres://prod-server:5432/myapp'" Enter
Type "      debug: false" Enter
Type "  teams:" Enter
Type "    devops: 'devops-team@company.com'" Enter
Type "    frontend: 'frontend-team@company.com'" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Create structure that uses mappings" Enter
Type "cat > app-config.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - config/{{@ env @}}.json:" Enter
Type "      content: |" Enter
Type "        {" Enter
Type "          \"database_url\": \"{{@ mappings.environments[env].database_url @}}\"," Enter
Type "          \"debug\": {{@ mappings.environments[env].debug @}}," Enter
Type "          \"contact\": \"{{@ mappings.teams.devops @}}\"" Enter
Type "        }" Enter
Type "variables:" Enter
Type "  - env:" Enter
Type "      description: 'Environment (dev/prod)'" Enter
Type "      type: string" Enter
Type "      default: 'dev'" Enter
Type "EOF" Enter
Sleep 3
Type "" Enter
Type "# Generate with mappings file" Enter
Type "struct generate --mappings-file mappings.yaml app-config.yaml ./config-output" Enter
Sleep 5
Type "" Enter
Type "# Check generated configuration" Enter
Type "cat config-output/config/dev.json" Enter
Sleep 3
