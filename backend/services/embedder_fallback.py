import numpy as np
from typing import Any, List, Union


class FallbackEmbedder:
    """
    Lightweight fallback embedder used when SentenceTransformer weights
    cannot be fetched from Hugging Face Hub (e.g. offline, rate-limited, or slow connection).
    Uses spaCy vectors if available, otherwise token frequency vectors.
    """

    def __init__(self, nlp=None):
        self.nlp = nlp

    def encode(
        self,
        texts: Union[str, List[str]],
        convert_to_tensor: bool = False,
        show_progress_bar: bool = False,
        normalize_embeddings: bool = True,
        **kwargs: Any,
    ) -> Any:
        is_single = isinstance(texts, str)
        items = [texts] if is_single else list(texts)

        vectors = []
        for text in items:
            text_str = str(text) if text else ""
            if self.nlp:
                doc = self.nlp(text_str[:1500])
                vec = doc.vector.astype(np.float32)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    if normalize_embeddings:
                        vec = vec / norm
                    vectors.append(vec)
                else:
                    vectors.append(np.zeros(96, dtype=np.float32))
            else:
                vec = np.zeros(64, dtype=np.float32)
                for word in text_str.lower().split():
                    vec[hash(word) % 64] += 1.0
                norm = np.linalg.norm(vec)
                if norm > 0 and normalize_embeddings:
                    vec = vec / norm
                vectors.append(vec)

        res = np.array(vectors, dtype=np.float32)
        return res[0] if is_single else res
