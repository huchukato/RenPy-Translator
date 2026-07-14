#!/usr/bin/env python3
"""
Ren'Py Translator - Translator Module
Backend di traduzione: Google, LibreTranslate, OpenRouter, llama_cpp
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Literal
import re
import requests

try:
    from deep_translator import GoogleTranslator
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False

try:
    from llama_cpp import Llama
    LLAMA_OK = True
except ImportError:
    LLAMA_OK = False

try:
    from huggingface_hub import hf_hub_download
    HF_OK = True
except ImportError:
    HF_OK = False


OPENROUTER_FREE_MODELS = [
    "google/gemma-2-9b-it:free",
    "google/gemma-2-27b-it:free",
    "meta-llama/llama-3-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "mistralai/mistral-nemo:free",
    "qwen/qwen-2-7b-instruct:free",
    "deepseek/deepseek-chat-v3.1:free",
]

LANG_NAMES = {
    "en": "English", "it": "Italian", "fr": "French", "es": "Spanish",
    "de": "German", "pt": "Portuguese", "ja": "Japanese", "zh": "Chinese",
    "ar": "Arabic", "ru": "Russian", "ko": "Korean",
}


@dataclass
class TranslatorConfig:
    backend: Literal["google", "bing", "bing_turbo", "bing_ultra", "libre", "openrouter", "llama"] = "google"
    source_lang: str = "en"
    target_lang: str = "it"
    libre_endpoint: str = "http://localhost:5000"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-2-9b-it:free"
    llama_model_repo: str = "llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic-GGUF"
    llama_model_file: str = ""
    preserve_names: bool = False
    translate_menu: bool = False
    timeout_s: int = 30
    batch_size: int = 20


class TranslationError(RuntimeError):
    pass


class Translator:
    RE_TOKEN = re.compile(
        r"(\\\\n|\\\\\"|\{[^}]*\}|\[[^\]]*\]|%\([^)]+\)[#0\- +]?\d*(?:\.\d+)?[a-zA-Z]|%[sdrof]|%%|https?://[^\s]+)"
    )

    def __init__(self, cfg: TranslatorConfig):
        self.cfg = cfg
        self.cache: dict[str, str] = {}
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def translate_many(
        self,
        texts: list[str],
        progress_cb: Callable[[int, int], None] | None = None,
        log_cb: Callable[[str, str], None] | None = None,
    ) -> dict[str, str]:
        unique = list(dict.fromkeys(t for t in texts if t))

        if self.cfg.preserve_names:
            preserved = {t for t in unique if self._is_name(t)}
            for n in preserved:
                self.cache[n] = n
            unique = [t for t in unique if t not in preserved]

        total = len(unique)
        batches = [unique[i:i + self.cfg.batch_size] for i in range(0, total, self.cfg.batch_size)]
        done = 0

        for batch in batches:
            if self.cancelled:
                raise TranslationError("Traduzione annullata.")
            translated = self._translate_batch(batch, log_cb)
            for orig, tr in zip(batch, translated):
                self.cache[orig] = tr
                done += 1
                if progress_cb:
                    progress_cb(done, total)

        return dict(self.cache)

    def _translate_batch(self, texts: list[str], log_cb=None) -> list[str]:
        protected, maps = zip(*[self._protect(t) for t in texts]) if texts else ([], [])
        protected = list(protected); maps = list(maps)
        raw = self._raw_batch(protected, log_cb)
        return [self._restore(r, m).replace("%", "%%") for r, m in zip(raw, maps)]

    def _raw_batch(self, texts: list[str], log_cb=None) -> list[str]:
        b = self.cfg.backend
        if b == "google":
            return self._google(texts)
        elif b == "bing":
            return self._bing(texts)
        elif b == "bing_turbo":
            return self._bing_turbo(texts)
        elif b == "bing_ultra":
            return self._bing_ultra(texts)
        elif b == "libre":
            return self._libre(texts)
        elif b == "openrouter":
            return self._openrouter(texts)
        elif b == "llama":
            return self._llama(texts, log_cb)
        raise TranslationError(f"Backend sconosciuto: {b}")

    def _google(self, texts: list[str]) -> list[str]:
        if not GOOGLE_OK:
            raise TranslationError("deep-translator non installato: pip install deep-translator")
        tr = GoogleTranslator(source=self.cfg.source_lang, target=self.cfg.target_lang,
                              timeout=self.cfg.timeout_s)
        try:
            res = tr.translate_batch(texts)
            return [r if r else t for r, t in zip(res, texts)]
        except Exception:
            out = []
            for t in texts:
                try:
                    out.append(tr.translate(t) or t)
                except Exception:
                    out.append(t)
            return out

    # ── Bing helpers ──────────────────────────────────────────────────────────

    _BING_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]
    _BING_ACCEPT_LANGS = [
        "en-US,en;q=0.9", "en-US,en;q=0.9,es;q=0.8",
        "en-GB,en;q=0.9", "en-CA,en-US;q=0.7,en;q=0.3",
    ]
    _BING_CHAR_LIMIT = 9000  # max caratteri per request (Bing usa ~10054, usiamo 9000 per sicurezza)
    _BING_SEP = "\n"          # separatore tra stringhe nello stesso chunk

    def _bing_make_session(self, base_url: str = "https://www.bing.com", idx: int = 0) -> tuple:
        """Crea sessione con IG + AbusePreventionHelper. Ritorna (session, ig, key, token)."""
        import random
        session = requests.Session()
        session.headers.update({
            "User-Agent": self._BING_USER_AGENTS[idx % len(self._BING_USER_AGENTS)],
            "Accept-Language": self._BING_ACCEPT_LANGS[idx % len(self._BING_ACCEPT_LANGS)],
        })
        ig_val = ""; key_val = ""; token_val = ""
        try:
            home = session.get(f"{base_url}/translator", timeout=10)
            html = home.text
            m_ig = re.search(r'IG:"([0-9A-F]+)"', html)
            m_abuse = re.search(
                r'var params_AbusePreventionHelper\s*=\s*\[(\d+),"([^"]+)",(\d+)\]', html
            )
            if m_ig:
                ig_val = m_ig.group(1)
            if m_abuse:
                key_val = m_abuse.group(1)
                token_val = m_abuse.group(2)
        except Exception:
            pass
        return session, ig_val, key_val, token_val

    def _bing_split_chunks(self, texts: list[str]) -> list[tuple[list[int], str]]:
        """
        Raggruppa texts in chunk da max _BING_CHAR_LIMIT caratteri.
        Ritorna lista di (indici, testo_concatenato).
        """
        chunks = []
        cur_indices = []
        cur_parts = []
        cur_len = 0
        for i, text in enumerate(texts):
            t = text.replace(self._BING_SEP, " ")  # evita collisioni col separatore
            needed = len(t) + (1 if cur_parts else 0)  # +1 per il \n
            if cur_parts and cur_len + needed > self._BING_CHAR_LIMIT:
                chunks.append((cur_indices, self._BING_SEP.join(cur_parts)))
                cur_indices = []; cur_parts = []; cur_len = 0
            cur_indices.append(i)
            cur_parts.append(t)
            cur_len += needed
        if cur_parts:
            chunks.append((cur_indices, self._BING_SEP.join(cur_parts)))
        return chunks

    def _bing_translate_chunk(self, session, chunk_text: str, src: str, tgt: str,
                              ig: str, key: str, token: str,
                              base_url: str = "https://www.bing.com") -> list[str]:
        """Traduce un intero chunk (più stringhe concatenate) in una sola request."""
        r = session.post(
            f"{base_url}/ttranslatev3",
            params={"isVertical": "1", "IG": ig, "IID": "translator.5024"},
            data={
                "fromLang": src,
                "to": tgt,
                "text": chunk_text,
                "token": token,
                "key": key,
            },
            timeout=self.cfg.timeout_s,
        )
        translated = r.json()[0]["translations"][0]["text"]
        return translated.split(self._BING_SEP)

    def _bing(self, texts: list[str]) -> list[str]:
        """Bing standard — una sessione, chunk multi-stringa."""
        src, tgt = self.cfg.source_lang, self.cfg.target_lang
        session, ig, key, token = self._bing_make_session()
        results = list(texts)
        for indices, chunk_text in self._bing_split_chunks(texts):
            try:
                parts = self._bing_translate_chunk(session, chunk_text, src, tgt, ig, key, token)
                for i, p in zip(indices, parts):
                    results[i] = p.strip()
            except Exception:
                pass  # lascia originale
        return results

    def _bing_turbo(self, texts: list[str]) -> list[str]:
        """Bing Turbo — 3 sessioni parallele, chunk multi-stringa per sessione."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        src, tgt = self.cfg.source_lang, self.cfg.target_lang
        n = 3
        sessions = [self._bing_make_session(idx=i) for i in range(n)]
        chunks = self._bing_split_chunks(texts)
        results = list(texts)

        def do_chunk(chunk_idx_data):
            chunk_idx, (indices, chunk_text) = chunk_idx_data
            sess, ig, key, token = sessions[chunk_idx % n]
            try:
                parts = self._bing_translate_chunk(sess, chunk_text, src, tgt, ig, key, token)
                return indices, parts
            except Exception:
                return indices, None

        with ThreadPoolExecutor(max_workers=n) as ex:
            futures = [ex.submit(do_chunk, (i, c)) for i, c in enumerate(chunks)]
            for f in as_completed(futures):
                indices, parts = f.result()
                if parts:
                    for i, p in zip(indices, parts):
                        results[i] = p.strip()
        return results

    def _bing_ultra(self, texts: list[str]) -> list[str]:
        """Bing Ultra — 6 sessioni parallele (3 www + 3 cn.bing.com), chunk multi-stringa."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        src, tgt = self.cfg.source_lang, self.cfg.target_lang
        bases = ["https://www.bing.com"] * 3 + ["https://cn.bing.com"] * 3
        sessions = [self._bing_make_session(base_url=b, idx=i) for i, b in enumerate(bases)]
        chunks = self._bing_split_chunks(texts)
        results = list(texts)

        def do_chunk(chunk_idx_data):
            chunk_idx, (indices, chunk_text) = chunk_idx_data
            sess, ig, key, token = sessions[chunk_idx % len(sessions)]
            base = bases[chunk_idx % len(bases)]
            try:
                parts = self._bing_translate_chunk(sess, chunk_text, src, tgt, ig, key, token, base)
                return indices, parts
            except Exception:
                # fallback www sessione 0
                try:
                    s, g, k, tk = sessions[0]
                    parts = self._bing_translate_chunk(s, chunk_text, src, tgt, g, k, tk)
                    return indices, parts
                except Exception:
                    return indices, None

        with ThreadPoolExecutor(max_workers=6) as ex:
            futures = [ex.submit(do_chunk, (i, c)) for i, c in enumerate(chunks)]
            for f in as_completed(futures):
                indices, parts = f.result()
                if parts:
                    for i, p in zip(indices, parts):
                        results[i] = p.strip()
        return results

    def _libre(self, texts: list[str]) -> list[str]:
        ep = self.cfg.libre_endpoint.rstrip("/") + "/translate"
        r = requests.post(ep, json={
            "q": texts,
            "source": self.cfg.source_lang,
            "target": self.cfg.target_lang,
            "format": "text",
        }, headers={"Content-Type": "application/json"}, timeout=self.cfg.timeout_s)
        if r.status_code != 200:
            raise TranslationError(f"LibreTranslate errore {r.status_code}")
        data = r.json()
        if isinstance(data, list):
            return [i.get("translatedText", "") for i in data]
        if isinstance(data, dict) and "translatedText" in data:
            tt = data["translatedText"]
            return tt if isinstance(tt, list) else [tt]
        raise TranslationError("Risposta API non valida")

    def _openrouter(self, texts: list[str]) -> list[str]:
        src = LANG_NAMES.get(self.cfg.source_lang, self.cfg.source_lang)
        tgt = LANG_NAMES.get(self.cfg.target_lang, self.cfg.target_lang)
        headers = {"Content-Type": "application/json"}
        if self.cfg.openrouter_api_key:
            headers["Authorization"] = f"Bearer {self.cfg.openrouter_api_key}"
        results = []
        for text in texts:
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": self.cfg.openrouter_model,
                        "messages": [
                            {"role": "system", "content": f"Translate from {src} to {tgt}. Only return the translation."},
                            {"role": "user", "content": text}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.3,
                    },
                    timeout=self.cfg.timeout_s
                )
                r.raise_for_status()
                results.append(r.json()["choices"][0]["message"]["content"].strip())
            except Exception:
                results.append(text)
        return results

    def _llama(self, texts: list[str], log_cb=None) -> list[str]:
        if not LLAMA_OK:
            raise TranslationError("llama-cpp-python non installato")
        if not HF_OK:
            raise TranslationError("huggingface-hub non installato")
        model_path = self._get_llama_model(log_cb)
        llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
        src = LANG_NAMES.get(self.cfg.source_lang, self.cfg.source_lang)
        tgt = LANG_NAMES.get(self.cfg.target_lang, self.cfg.target_lang)
        results = []
        for text in texts:
            try:
                prompt = f"<start_of_turn>user\nTranslate from {src} to {tgt}: {text}<end_of_turn>\n<start_of_turn>model\n"
                resp = llm(prompt, max_tokens=512, temperature=0.1, stop=["<end_of_turn>"], echo=False)
                translated = resp["choices"][0]["text"].strip() if resp and resp.get("choices") else text
                results.append(translated or text)
            except Exception:
                results.append(text)
        return results

    def _get_llama_model(self, log_cb=None) -> str:
        from pathlib import Path
        cache = Path.home() / ".cache" / "renpy-translator" / "models"
        cache.mkdir(parents=True, exist_ok=True)
        model_file = cache / self.cfg.llama_model_file
        if model_file.exists():
            return str(model_file)
        if log_cb:
            log_cb("system", f"Download modello {self.cfg.llama_model_file}...")
        path = hf_hub_download(repo_id=self.cfg.llama_model_repo,
                               filename=self.cfg.llama_model_file,
                               local_dir=str(cache))
        return path

    def _protect(self, text: str):
        mapping = {}
        counter = 0
        def rep(m):
            nonlocal counter
            k = f"\u27eaRNT{counter}\u27eb"; mapping[k] = m.group(0); counter += 1; return k
        return self.RE_TOKEN.sub(rep, text), mapping

    def _restore(self, text: str, mapping: dict) -> str:
        for k, v in mapping.items():
            text = text.replace(k, v)
        def norm(s): return re.sub(r"[^A-Za-z0-9]", "", s).upper()
        norm_map = {norm(k): v for k, v in mapping.items()}
        if norm_map:
            def repl(m):
                return norm_map.get(norm(m.group(0)), m.group(0))
            text = re.sub(r"(?:\u27ea\s*)?R\s*N\s*T\s*\d+(?:\s*\u27eb)?", repl, text, flags=re.IGNORECASE)
        return text

    def _is_name(self, text: str) -> bool:
        if not text or len(text) > 50 or ' ' in text or '\n' in text:
            return False
        return text[0].isupper() and text[1:].islower()
