# how-to :: sentence_transformers (Capturing Semantic Meaning)
---
## Overview
Sentence Transformers transform word(s) into dense vector embeddings. This is helpful for us because these dense vectors are repesented in a high dimensional space that captures a lot of information about the word. Thus, we often turn to sentence transformers when we want to do similarity searching, clustering, or semantic searching with words.

### Estimated Time Cost: 0.5 hrs (round to nearest 0.1)

### Prerequisites:
- Python (3.6+)
- `sentence-transformers` library

### Procedure:
1. Begin your adventure.
  ```
  pip install sentence-transformers
  ```
2. Load a model! Sentence-transformers are so intuitive and easy to use because we don't need to do the embeddings ourselves. Here, we can load a model that allows vectorization.
  ```
  from sentence_transformers import SentenceTransformer

  model = SentenceTransformer('all-MiniLM-L6-v2')
  ```
3. Apply the model on some word(s)!
  ```
  sentences = ["I love making how-to guides", "I absolutely despise writing these despicable guides", "LOVE"]
  embeddings = model.encode(sentences)
  ```
4. Next steps include using libraries like sklearn to apply cosine similarities (the angle between the vectors). A larger angle indicates a larger deviation in semantic meaning while a smaller angle indicates a correlation in meaning. Thus, when we compare embeddings here like `embedding[0]` and `embedding[1]`, we would expect a fairly large angle while `embedding[0]` and `embedding[2]` may be much more closer.

### Resources
* https://github.com/UKPLab/sentence-transformers
* https://www.sbert.net

---

Accurate as of (last update): 2025-05-28

#### Contributors:  
Ethan Sie, pd4  
