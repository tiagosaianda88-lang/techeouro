import os

def process_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                if 'oWCQCPq8-cYcElz8sYxB' in content:
                    new_content = content.replace('oWCQCPq8-cYcElz8sYxB', 'dWcQCPqB-cYcFTz8sYxE')
                    with open(filepath, 'w') as f:
                        f.write(new_content)
                    print(f"Fixed {filepath}")

process_dir('/Users/tmss1988/Desktop/netfily')
