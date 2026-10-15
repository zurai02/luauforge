# LuauForge

A free coding assistant that only does **Luau and Roblox**. It runs entirely in the visitor's browser: no account, no API key, no server, no paid plan. Host it on GitHub Pages and anyone in the world can use it.

## What is in it

| Layer | What it does | Needs |
| --- | --- | --- |
| **Docs mode** (always on) | Searches a built-in Luau and Roblox knowledge base (57 entries), runs the built-in code checker on anything you paste, and replays answers you taught it | Any browser |
| **AI mode** (optional) | A free open-weights coding model (Qwen2.5-Coder, 0.5B to 7B) runs on the visitor's own GPU. Every question is grounded with the best knowledge-base entries and your lessons | A browser with WebGPU (recent Chrome or Edge) |
| **Self-check loop** | After the AI answers, the checker lints its Luau. If it used `wait()`, an unprotected DataStore call, an unvalidated remote and so on, the AI is told what is wrong and rewrites the code | AI mode |
| **Lessons** | Lessons you save ("Good answer", "Correct it", or typed in) are recalled for similar questions. Export them as markdown and share them | Any browser |

The checker flags: deprecated APIs (`wait`, `spawn`, `delay`, `tick`, `:connect`, `FindPartOnRay`, body movers, `Humanoid:LoadAnimation`, old collision calls), `Instance.new(class, parent)`, DataStore and HTTP calls without `pcall`, `OnServerEvent` handlers whose first parameter is not the player, `while true do` loops with no yield, `require(assetId)`, `loadstring`, and unbalanced brackets. It is heuristic. It is not a type-checker, so keep testing in Studio.

## Put it online (GitHub Pages)

1. Create a new public GitHub repository, for example `luauforge`.
2. Upload `index.html` to the root of the repo. It is the whole app in one file (styles, code and knowledge base included), so nothing else is required. Optionally upload the `kb/` folder and `.nojekyll` too.
3. Open **Settings > Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`, and save.
4. After about a minute the site is live at `https://<your-username>.github.io/luauforge/`.

Double-clicking `index.html` also works, for Docs mode. The AI model needs the page hosted, or run `python3 -m http.server 8000` in this folder and open http://localhost:8000.

## Editing the source

The `source/` folder holds the editable files. After you change anything in it, run `python3 build.py` inside `source/`. It writes a fresh single-file app to `source/dist/index.html`. Copy that over the `index.html` in the zip's top folder.

`kb/community.md` next to `index.html` is read live when the page is hosted, so you can add community entries to it without rebuilding.

## How the "learning" works (and what it is not)

The model's weights do not change in the browser. Training a language model needs GPUs and a large dataset, and a web page cannot do that. LuauForge learns the way a good reference does, by growing what it can look up:

- **Lessons**: tap **Good answer** or **Correct it** under any reply, or add one in the **Lessons** panel. The best matching lesson is shown first in Docs mode and given to the AI as a verified example in AI mode. Lessons stay in that visitor's browser.
- **Community knowledge**: export your lessons from **Lessons** (they download as markdown in the same format as `kb/`) and add them to `kb/community.md` through a pull request. Every visitor gets them on their next page load. This is how the site gets smarter for everyone, with no server.
- **Add checker rules**: each rule in `source/js/lint.js` is a few lines. When you meet a new common mistake, add a rule and a knowledge entry that explains the fix.

## Honest limits

- A 1.5B to 7B model running in a browser is much weaker than the large hosted models at open-ended coding. What makes LuauForge useful is the grounding, the checker and the focus on Luau, not raw model size. Use the 7B model if your GPU has about 6 GB free.
- The first AI load downloads 1 to 5 GB depending on the model size, then the browser caches it. Docs mode needs no download.
- The knowledge base examples were checked with the official `luau-analyze` for syntax and core-library correctness. Roblox-specific API names were written from knowledge of the engine and not machine-verified, so report anything that is wrong.
- Check each model's license on its Hugging Face page before using it in a commercial game. I believe the 3B model is research-only, so prefer 1.5B or 7B for commercial use.

## Your own model (the long-term "custom model" path)

1. Collect a few thousand high-quality Luau and Roblox question and answer pairs (the lessons exported from **Lessons** are a good start).
2. Fine-tune a small coding model with LoRA (for example Qwen2.5-Coder-1.5B-Instruct) using a free notebook GPU.
3. Convert and quantize it to MLC format with `mlc_llm`, upload the weights to a Hugging Face repo, and compile the model library (`.wasm`).
4. In the app, open **Settings > Use your own fine-tuned model** and enter the model id, the weights URL (ending in `/resolve/main/`) and the `.wasm` URL.

The app code does not need to change.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The finished app, in one file. Upload this |
| `kb/community.md` | Community entries, read live when hosted |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |
| `source/index.html`, `source/style.css` | Page and theme (editable) |
| `source/js/app.js` | Chat flow, prompts, Docs mode, self-check loop, dialogs |
| `source/js/llm.js` | Loads and streams from the in-browser model (WebLLM) |
| `source/js/kb.js` | Knowledge base parser and search |
| `source/js/memory.js` | Lessons: save, recall, export, import |
| `source/js/lint.js` | The Luau checker |
| `source/js/md.js` | Markdown rendering and Luau syntax highlighting |
| `source/kb/*.md` | Knowledge base. Add entries here, then rebuild |
| `source/build.py` | Bundles everything into one `index.html` |

## Privacy

Nothing you type leaves your browser. In AI mode the model files are fetched once from the jsDelivr and Hugging Face CDNs, and the page loads the WebLLM library from jsDelivr (`esm.run`).
