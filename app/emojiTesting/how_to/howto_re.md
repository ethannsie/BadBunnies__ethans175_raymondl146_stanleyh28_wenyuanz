# how-to :: re (Regular Expression Operations)
---
## Overview
re or Regular Expression Operations or regex. These are powerful tools for searching, manipulating, and matching strings. Imagine if .split() .index() were on steroids---that's regex in a nutshell. re is a built in module in Python that is very useful for cleaning data and parsing text.

### Estimated Time Cost: 0.5 hrs (round to nearest 0.1)

### Prerequisites:
- Python 3+

### Procedure:
1. Import the module
  ```
  import re
  ```
2. Example of parsing text with regex
  ```
  text = "I, don't, understand, why? I. am. awake. right! now! My punctuation. is. trashhhh ."
  words = re.findall(r'\b\w+\b', text.lower())
  ```
  This looks like a nightmare to parse through right? Imagine if you wanted to isolate each of the words in text when there's no clear cut delimiter or way to isolate words. Regular expressions allows you to find patterns. The code above separates each word based on punctuation, sayint that each word (`\w+`) should simply be bounded by itself (`\b`). We then get an output like this:
  ```
  print(words)
  # ["I", 'don', 't', "understand", "why", "I", "am", "awake", "right", "now", "My", "punctuation", "is", "trashhhh"]
  ```
3. But wait! I want my apostrophes. No worries, regex has you covered.
  ```
  words = re.findall(r"\b\w+(?:'\w+)?\b", text.lower())

  ```
  This nifty little addition (`(?:'\w+)?`) allows us to check if there is an apostrophe and if so, it keeps the apostrophe in between what would have been considered two separate words.

Regex is not very intuitive at first, but it is very helpful for cleaning up messy data and is definitely worth taking a look at! If you wish to find more of the regular expressions, look to resources below.

### Resources
* https://docs.python.org/3/library/re.html
* https://regex101.com

---

Accurate as of (last update): 2025-05-28

#### Contributors:  
Ethan Sie, pd4  
