import os
import glob

files = glob.glob('/Users/tmss1988/Desktop/netfily/*.html')

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'AW-182795955532' in content:
        new_content = content.replace('AW-182795955532', 'AW-18279595532')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {file_path}")
    else:
        print(f"No match in {file_path}")
