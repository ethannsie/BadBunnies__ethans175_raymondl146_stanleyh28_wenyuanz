# how-to :: FAISS (Facebook AI Similarity Search)
---
## Overview
Pig or Dog? That's the million dollar question and a serious one at that. Pig. Or. Dog. We often struggle to classify images and find relations anad FAISS does an amazing job at these tasks. In all seriousness, FAISS (Facebook AI Similarlity Search) is a library created by Meta AI to allow for efficient similarity searching and clustering. In short, it scales well with large amounts of data and allows us to more easily code functions like semantic searching, recommendation system, and nearest neighbor searching.
![Pig Or Dog?](pigdog.jpg)

### Estimated Time Cost: 1.2 hrs (round to nearest 0.1)

### Prerequisites:
- Python 3.7+
- Linear Algebra
  - Vector Spaces
  - Vectorization
- Packages:
  - faiss-cpu
  - faiss-gpu
  - numpy

### Procedure: A basic implementation of nearest neighbor searching
1. Download Basic Packages (you can also use `faiss-gpu`, if you want faster computations and have a GPU available)
    ```
    pip install faiss-cpu numpy
    ```
2. Basic Demonstration of creating a vector space. This code here generates 1000 randomly positioned vectors in 128-dimensional space
    ```
    import faiss
    import numpy as np

    dimensions = 128
    vector_count = 1000
    vector_space = np.random.random((vector_count, dimensions)).astype('float32')
    ```
3. Generate a FAISS Index. There are many built in indexes like IndexFlatIP and IndexIVFFlat. IndexFlatL2 finds the euclidean distances from any two vectors in the the vector_space
   ```
   index = faiss.IndexFlatL2(dim)
   index.add(xb)
   ```
4. Check for nearest-neighbors. It creates 5 new randomly placed vectors in the 128-dimension space. Then, we capture the distances and the indicies which indicate how far/close the placed_vector is from three (k=3) of the closest of the original 1000 vectors.
  ```
  placed_vectors = np.random.random((5, dim)).astype('float32')
  D, I = index.search(placed_vectors, k=3)
  print("Distances:", D)
  print("Indices:", I)
  ```

By encoding information in dimensions, we can account for semantic meaning and more complex similarities. This simple implementation of KNN allows us to determine similarity by simply calculating something we are all familiar with: Euclidean Distance. FAISS allows for more complex analysis like inner products and cosine similarities, but the base model is still very intuitive and helpful.

### Resources
* https://github.com/facebookresearch/faiss
* https://www.pinecone.io/learn/series/faiss/faiss-tutorial/
* https://ai.meta.com/tools/faiss/
* https://www.datacamp.com/blog/faiss-facebook-ai-similarity-search

---

Accurate as of (last update): 2025-05-28

#### Contributors:  
Ethan Sie, pd4  
