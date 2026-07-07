import os
import glob

gtag_snippet = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18279595532"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'AW-18279595532');
</script>

<!-- Event snippet for Visualização de página conversion page -->
<script>
  gtag('event', 'conversion', {
      'send_to': 'AW-18279595532/dWcQCPqB-cYcFTz8sYxE',
      'value': 1.0,
      'currency': 'EUR'
  });
</script>
</head>
"""

def process_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check if already has Google Tag, to avoid duplicate
                if 'AW-18279595532' in content:
                    print(f"Skipping {filepath}, already has tag.")
                    continue
                
                # We need to find </head> and replace it
                if '</head>' in content:
                    new_content = content.replace('</head>', gtag_snippet)
                    with open(filepath, 'w') as f:
                        f.write(new_content)
                    print(f"Injected gtag to {filepath}")
                else:
                    print(f"No </head> found in {filepath}")

process_dir('/Users/tmss1988/Desktop/netfily')
