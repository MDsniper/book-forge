# Images: covers, illustrations, concept art

How to generate images for the book — covers, interior illustrations, and concept art — using `scripts/image.py`. Provider-agnostic: configure whichever image API you have, and the script routes to it.

## Quick start

1. **Configure a provider** — set one of these env vars (or fill in `.book-forge/image-config.json`):
   ```bash
   export OPENAI_API_KEY=sk-...           # OpenAI gpt-image-1 (best for covers)
   # or
   export IDEOGRAM_API_KEY=...            # best at title text on cover
   # or
   export GOOGLE_GENAI_API_KEY=...        # Google Imagen
   # or
   export FAL_KEY=...                     # fal.ai (Flux)
   # or
   export STABILITY_API_KEY=...           # Stability SD3
   # or
   export REPLICATE_API_TOKEN=...         # Replicate
   # or
   export COMFYUI_URL=http://127.0.0.1:8188   # self-hosted (free)
   ```

2. **Check what's configured:**
   ```bash
   python3 scripts/image.py providers
   ```

3. **Generate a cover:**
   ```bash
   # From an inline prompt:
   python3 scripts/image.py cover "epic fantasy cover, a blacksmith's forge under a blood-red moon, painterly, oxblood and ash palette"

   # Or from a brief file (recommended — the writer persona fills it in):
   python3 scripts/image.py brief cover    # writes image-brief-cover.md
   # ... edit image-brief-cover.md ...
   python3 scripts/image.py cover image-brief-cover.md
   ```

## Choosing a provider

| Use case | Best provider | Why |
|---|---|---|
| Cover with title text rendered on image | **Ideogram** or **OpenAI gpt-image-1** | Strong text rendering. Most other models produce garbled text. |
| Cover, clean base for manual typesetting | **fal.ai Flux Pro** or **Stability SD3** | Highest image quality; you typeset title in Canva/BookBrush/Photoshop afterward. |
| Free / self-hosted / offline | **ComfyUI** | Runs locally, no API cost, full control. Requires GPU. |
| Interior illustrations (no text) | Any | Text rendering doesn't matter. Cheapest wins. |
| Children's book / illustrated chapter art | OpenAI gpt-image-1 or Flux | Style consistency across many images. |

The script auto-picks the best provider when you don't specify `--provider`. For covers (`cover` / `cover-print`), it prefers Ideogram or OpenAI so the title text renders correctly. For illustrations, it picks whatever's configured.

## Cost awareness

Image generation is rarely free. The script **always prints the cost estimate** before generating, and asks for confirmation (`--yes` to skip):

```
provider: ideogram (Ideogram v2)
cost:     ~$0.08 per image
size:     1600x2560
prompt:   epic fantasy cover, a blacksmith's forge under a blood-red moon...

Generate? [y/N]
```

Only ComfyUI (self-hosted) is free. Everything else bills per image — set `--dry-run` to preview without generating.

## Aspect ratios and presets

Built-in presets (auto-selected by command):

| Command | Aspect | Dimensions | Use |
|---|---|---|---|
| `cover` | 2:3 (portrait) | 1600×2560 | ebook cover (KDP/Apple/Kobo) |
| `cover-print` | 2:3 + bleed | 1800×2700 | print cover front (6×9 trim) |
| `illustration` | 4:3 | 1600×1200 | interior art |
| `concept` | 1:1 | 1024×1024 | concept variants |
| `social` | 3:2 | 1536×1024 | social/ads (Twitter/BookBub) |
| `generate` | custom | `--width --height` | anything else |

For a full print cover with spine, generate a clean front-only image and assemble front + spine + back in image-editing software using the dimensions from `publish.py cover-spec`.

## Text on the image: a critical caveat

**Most image models render text poorly.** Only Ideogram and OpenAI gpt-image-1 do it reliably. If you ask Flux or SD3 to "render the title 'THE ASH GARDEN' on the cover," you'll get garbled letters.

Two strategies:

1. **Generate text on image** — use Ideogram or OpenAI. Set `includeText: true` in the brief. Best for one-shot cover generation.
2. **Generate clean base + typeset manually** — use Flux/SD3/ComfyUI. Set `includeText: false`. Bring the image into Canva, BookBrush, or Photoshop and add the title text yourself. **This is what professional cover designers do** — the type is almost never AI-generated.

The script warns if you request text on a weak-text provider.

## The brief

A good image brief has the same structure authorclaw's cover-designer skill uses:

```markdown
# Cover brief

title: <book title>
author: <author name>
genre: <genre>
mood: <brooding / triumphant / wistful / menacing>
era: <historical / contemporary / near future>
setting: <the world — 1-2 sensory sentences>
keyImagery: <the single strongest visual image>
palette: <2-4 colors, hex or descriptive>
avoidImagery: <what NOT to include>
style: <realistic | illustrated | minimalist | painterly | photographic>
includeText: <true | false>
```

The writer persona generates this from `voice.md`, `world.md`, and the manuscript. Strong briefs:
- **Lead with genre signals** — readers identify genre from the cover thumbnail in <1 second. Make the genre unmistakable.
- **One focal image** — no clutter. The cover is a billboard, not a description.
- **Palette over plot** — emotional tone (via color) lands before the eye reads the title.
- **Avoid: "a scene from chapter 7."** Covers sell the *promise*, not the plot.

## Cover design rules (the things the AI can't judge)

Even with a great AI image, the cover needs human judgement on:

- **Thumbnail legibility** — shrink to 120px wide; can you still read the title and tell the genre?
- **Title size** — at least 1/3 of cover height. New authors err small; established authors can go smaller.
- **Hierarchy** — title > author name (unless you're a name author) > tagline/series.
- **Contrast** — dark type on light, or vice versa. Never low-contrast.
- **Genre signals** — display serif for literary/historical; chunky sans for thriller; script for some romance. The AI image gives you the visual; the typography must match the genre.

For professional-grade covers, **hire a designer** (Reedsy $625–$1,250; Damonza $500–$2,000). Use AI for early concepts and comps, then hand the chosen direction to a pro for final execution.

## Interior illustrations

For children's books, illustrated nonfiction, or chapter art:

```bash
python3 scripts/image.py brief illustration
# edit image-brief-illustration.md
python3 scripts/image.py illustration image-brief-illustration.md
```

**Style consistency** is the hard part for series of illustrations. Strategies:
- Use the same provider, model, and style keywords for every image.
- Include a "reference image" prompt component that ties them together ("in the same painterly woodcut style as the previous illustrations").
- For OpenAI gpt-image-1, you can pass `--variants N` on `concept` to explore a style, pick a direction, then lock it in.

## What this script does NOT do

- Does not design the cover for you. The brief is the design direction; the AI renders it. Quality still depends on the brief + human judgement.
- Does not assemble a full print cover (front + spine + back + barcode). Generate the front-only image, then assemble with the dimensions from `publish.py cover-spec` using image-editing software.
- Does not iterate on a chosen image (no img2img / inpainting in this version — use the provider's own UI for that, then bring the result back).
- Does not validate the image is genre-appropriate or commercially competitive. That's a human call.

## Setup hints by provider

### ComfyUI (free, self-hosted)
1. Install: https://github.com/comfyanonymous/ComfyUI
2. Download a checkpoint (e.g. SDXL Base) into `models/checkpoints/`
3. Run: `python main.py` → serves on http://127.0.0.1:8188
4. Set `COMFYUI_URL=http://127.0.0.1:8188`
5. Optional: build a workflow in the ComfyUI UI, save as JSON, point `comfyui.workflow` at it. The script injects your prompt into the "Positive prompt" node and dimensions into the EmptyLatentImage node.

### Google Imagen
- **Gemini API path** (simplest): get a key at https://aistudio.google.com/apikey, set `GOOGLE_GENAI_API_KEY`.
- **Vertex AI path** (enterprise): `gcloud auth application-default login`, set `GCP_PROJECT`. Used for higher volume.

### OpenAI
- Get a key at https://platform.openai.com/api-keys. Needs an org with image-generation access.
- `gpt-image-1` is the current cover-grade model.

### Ideogram
- Get a key at https://developer.ideogram.ai/. Best text rendering on the market.

### fal.ai
- Get a key at https://fal.ai/dashboard/keys. autonovel uses this. Flux Pro is the workhorse.

### Stability
- Get a key at https://platform.stability.ai/. SD3 Large is the cover-grade model.

### Replicate
- Get a token at https://replicate.com/account/api-tokens. Hosts Flux and many other models.
