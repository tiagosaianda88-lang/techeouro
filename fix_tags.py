import os
import glob
import re

global_tag = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18279595532"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'AW-18279595532');
  </script>"""

event_snippet = """  <!-- Event snippet for Visualização de página conversion page -->
  <script>
    gtag('event', 'conversion', {
        'send_to': 'AW-18279595532/dWcQCpqB-cYcFTz8sYxE',
        'value': 1.0,
        'currency': 'EUR'
    });
  </script>"""

full_snippet = f"\n{global_tag}\n\n{event_snippet}\n"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "</head>" not in content:
        return

    # Remove existing tags to avoid duplicates
    # We will use regex to find the blocks and remove them.
    # Because of slight formatting differences, we can match the start and end of scripts.
    
    # Remove existing Google Tag block
    content = re.sub(r'<!-- Google tag \(gtag\.js\) -->.*?gtag\(\'config\', \'AW-18279595532\'\);\s*</script>', '', content, flags=re.DOTALL)
    
    # Remove existing Event snippet block
    content = re.sub(r'<!-- Event snippet for Visualização de página conversion page -->.*?\}\);\s*</script>', '', content, flags=re.DOTALL)

    # Clean up empty lines at the top of head if any were left
    content = re.sub(r'<head>\s*\n\s*\n+', '<head>\n', content)

    # Insert right before </head>
    content = content.replace('</head>', f"{full_snippet}</head>")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

html_files = []
for root, dirs, files in os.walk('.'):
    if 'anty-codex' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.html'):
            html_files.append(os.path.join(root, file))

for f in html_files:
    process_file(f)
    print(f"Processed {f}")

