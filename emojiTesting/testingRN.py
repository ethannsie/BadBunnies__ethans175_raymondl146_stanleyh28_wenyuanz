from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
import readJSON

EMOJI_DB = readJSON.getDict()

model = SentenceTransformer('all-MiniLM-L6-v2')

all_keywords = []
all_emojis = []

for emoji, keywords in EMOJI_DB.items():
    for kw in keywords:
        all_keywords.append(kw)
        all_emojis.append(emoji)

keyword_embeddings = model.encode(all_keywords, convert_to_numpy=True, normalize_embeddings=True)

d = keyword_embeddings.shape[1]
index = faiss.IndexFlatIP(d)
index.add(keyword_embeddings)

def text_to_emoji_faiss(text, threshold=0.6):
    words = re.findall(r'\b\w+\b', text.lower())
    output_words = []

    for word in words:
        word_emb = model.encode([word], convert_to_numpy=True, normalize_embeddings=True)
        D, I = index.search(word_emb, k=1)
        score = D[0][0]
        idx = I[0][0]
        if score >= threshold:
            output_words.append(all_emojis[idx])
        # else:
        #     output_words.append(word)
    return " ".join(output_words)

text = "Once upon a time, there was a cool dog. He liked to go on walks with his owner to the park. But one day, his owner fell into a hole and couldn't get out. The dog was very sad because he couldn't go on walks anymore. The End!"
sentences = text.split(". ")
for sentence in sentences:
    print(sentence)
    print(text_to_emoji_faiss(sentence))
