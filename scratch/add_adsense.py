import glob

html_files = glob.glob('*.html')
adsense_code = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2757348402596933" crossorigin="anonymous"></script>'

for file in html_files:
    if file == 'terminal.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if adsense_code not in content and '</head>' in content:
        content = content.replace('</head>', f'  {adsense_code}\n</head>', 1)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("Done")
