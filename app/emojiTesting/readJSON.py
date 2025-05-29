import json

with open('emojiTesting/emoji-list.json', 'r', encoding='utf-8') as f:
    emoji_entries = json.load(f)

keyword_to_emoji = {}

for entry in emoji_entries:
    emoji_char = entry.get("emoji")
    keywords = entry.get("keywords", [])
    keyword_to_emoji[str(emoji_char)] = keywords

def getDict():
    return keyword_to_emoji
