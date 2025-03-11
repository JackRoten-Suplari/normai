# normai
Test grounds for AI based normalizations

Anthropic_batch.py needs work to be integrated into this repo. Additional supporting data files are required such as 'data/boots-output.batch_1_of_1.jsonl'

normalize_companies.py includes grouping and fuzzy matching steps to: further make Anthropic normalization outputs ready for uploading to Suplari

Steps for Normalization:
1.  Data Preprocessing & Cleaning
i.e.
- Convert to lowercase: "UBER Inc." → "uber inc"
- Remove special characters: "U.B.E.R" → "uber"
- Expand abbreviations: "Corp." → "Corporation"
- Strip spaces: " Uber " → "Uber"

2. Rule-Based Matching for Quick Normalization
- Exact match with a vendor dictionary
- Prefix/suffix removal for common cases

3. Fuzzy Matching for Handling Typos & Variations
- Use Levenshtein Distance or Jaccard Similarity to find the closest match.

4. AI-Based Name Normalization (Word Embeddings & Clustering)
   - Use Word2Vec, BERT, or Transformer-based embeddings to match vendor names based on contextual similarity.
  
5. If normalized vendor names match other master mapped/ normalzied vendors, attach known website link

6. If no website link can be found, use AI-Based Web Search (Scraping & API)
- If no direct match exists, search the web using:
- Google Search API
- DuckDuckGo API
- BeautifulSoup + Web Scraping

7. Future goals would include Active Learning for continuous improvement
- Track low-confidence matches for human review.
- Manually correct errors and feed corrections into the ML model.
- Retrain the model over time for improved accuracy.
