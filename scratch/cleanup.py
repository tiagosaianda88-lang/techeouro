import re

with open('terminal.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I want to remove the leftover script.
# The leftover script starts around `var tickerTrack = root.querySelector('#ntrack');` or `function loadFinnhubNews()`
# But let's find the exact block.
# The new RTF widget ends with `})();\n</script>`
# The old one has `function loadFinnhubNews()` ... `setTimeout(function(){livePrices();loadNews();},800);\n  })();\n  </script>`

# Let's locate the RTF script end:
match = re.search(r'(</script>\s*)(<div class="sr-only">.*?setTimeout.*?</script>)', content, re.DOTALL)
if match:
    # We remove match.group(2)
    content = content.replace(match.group(2), "")
    with open('terminal.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Cleanup successful.")
else:
    # Let's try to find where the duplicate starts
    # `loadFinnhubNews` is a good marker for the old script
    idx = content.find("function loadFinnhubNews()")
    if idx != -1:
        # Find the previous </script> tag
        prev_script_end = content.rfind("</script>", 0, idx)
        if prev_script_end != -1:
            # Find the next </script> tag after idx
            next_script_end = content.find("</script>", idx)
            if next_script_end != -1:
                # Remove from after the first </script> to the next </script>
                # Actually, maybe the old script starts earlier. Let's just remove the whole <script> if it contains loadFinnhubNews.
                pass

print("Done")
