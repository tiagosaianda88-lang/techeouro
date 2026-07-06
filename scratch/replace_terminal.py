import re

with open('scratch/terminal_rtf.txt', 'r', encoding='utf-8') as f:
    rtf_content = f.read()

# Extract the widget
# Looking for <!-- TECH & OURO PÁGINA PULSE FINANCE --> to the end of the script before </body>
widget_match = re.search(r'(<div id="terminal-page".*?</script>)', rtf_content, re.DOTALL)
if not widget_match:
    print("Widget not found in RTF.")
    exit(1)

widget_html = widget_match.group(1)

# Now read terminal.html
with open('terminal.html', 'r', encoding='utf-8') as f:
    term_content = f.read()

# Replace <div id="term" ...> ... </script> with the new widget
# Be careful to replace everything up to the </script> tag before </main> or </body>
term_match = re.search(r'(<div id="term".*?</script>)', term_content, re.DOTALL)
if not term_match:
    print("Old widget not found in terminal.html")
    exit(1)

new_content = term_content.replace(term_match.group(1), widget_html)

with open('terminal.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement successful.")
