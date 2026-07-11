# Multimodal Agents — Session Code

All demos use the **free Gemini API**. Get a free key here: https://aistudio.google.com/apikey

## Setup (one time)

```bash
pip install -r requirements.txt
```

1. Copy `.env.example` to `.env`
2. Paste your API key inside `.env`
3. Create the sample files:

```bash
python 00_create_samples.py
```

## Files (run in order)

| File | Topic | What students learn |
|------|-------|---------------------|
| `00_create_samples.py` | Setup | Creates demo images / audio / PDF (don't teach, just run) |
| `01_vlm.py` | Vision Language Model | Send image + question, get answer. Compare 2 images |
| `02_audio_lm.py` | Audio (classic) | `wave`+`numpy` measure sound + offline Sphinx → LLM interprets |
| `03_video_understanding.py` | Video (classic) | OpenCV reads colour/motion/scene-cuts → LLM narrates |
| `04_ocr_pipeline.py` | OCR Pipeline | Image → raw text → clean JSON → saved file |
| `05_document_understanding.py` | Documents | Full PDF: summary, tables, charts, headers/footers |
| `06_multimodal_rag.py` | Multimodal RAG | Caption → embed → retrieve image → answer |
| `07_tool_calling.py` | Tool Calling | Model asks us to run functions = agent behavior |

Run any file like:

```bash
python 01_vlm.py
```

## Tips for the live session

- **Better demos:** replace the generated samples with real files — your own photo (`sample.jpg`), a voice note (`sample_audio.wav`), any PDF (`sample.pdf`), real photos in `images/`.
- **Error 429 (rate limit):** free tier allows ~10 requests per minute. Wait 30–60 seconds and run again.
- **The big idea to repeat all session:** everything is the same pattern — `contents = [some media, some text]` → model → answer. Only the media type changes.
