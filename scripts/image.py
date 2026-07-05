#!/usr/bin/env python3
"""book-forge image generator.

Provider-agnostic image generation for covers, illustrations, and concept art.
Auto-detects which provider is configured (via env vars or image-config.json)
and routes to it. Pure stdlib (urllib) — no `requests` dependency.

Providers (set the env var / config key for the one you have):
  - comfyui   (self-hosted, free)        COMFYUI_URL=http://127.0.0.1:8188
  - google    (Imagen via Vertex/Gemini) GOOGLE_GENAI_API_KEY=...  (or GCP creds)
  - openai    (gpt-image-1, best text)   OPENAI_API_KEY=...
  - fal       (fal.ai, flux)             FAL_KEY=...
  - ideogram  (best at text on image)    IDEOGRAM_API_KEY=...
  - stability (Stable Diffusion 3)       STABILITY_API_KEY=...
  - replicate (many models)              REPLICATE_API_TOKEN=...

Configuration precedence (per provider):
  1. env var (e.g. OPENAI_API_KEY)
  2. .book-forge/image-config.json (project-scoped)
  3. ~/.config/book-forge/image-config.json (user global)
  4. assets/image-config.example.json (just the template — never has real keys)

Commands:
  image.py providers                     # list configured + available providers
  image.py cover <brief>                # ebook cover 1600x2560 (2:3)
  image.py cover-print <brief>          # print cover front (trim + bleed)
  image.py illustration <brief>         # interior illustration, 4:3
  image.py concept <brief> --variants N # N concept variants (square)
  image.py generate <brief> --w 1024 --h 1024 [--provider X] [--out FILE]
  image.py brief <type>                 # scaffold a brief template (writer persona fills)
  image.py --dry-run cover <brief>      # show what would be sent, generate nothing

Notes:
  - Cost-aware: prints an estimate before generating on paid providers.
  - Text-on-image: only ideogram and openai render title text reliably.
    Other providers produce a clean base image — set includeText:false and
    typeset the title in Canva/BookBrush/Photoshop afterward.
  - NEVER fails because no provider is configured — prints install hints.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
HOME = os.path.expanduser("~")

CONFIG_PATHS = [
    os.path.join(os.getcwd(), ".book-forge", "image-config.json"),
    os.path.join(HOME, ".config", "book-forge", "image-config.json"),
]

# --------------------------------------------------------------------------- #
# Provider definitions
# --------------------------------------------------------------------------- #

# Each provider: env vars to detect, the config keys it reads, cost estimate.
# `text_capability`: 'strong' (renders title text well), 'weak' (clean base only).
PROVIDERS = {
    "comfyui": {
        "label": "ComfyUI (self-hosted, free)",
        "env": ["COMFYUI_URL"],
        "config_keys": ["url", "workflow"],
        "cost": "$0.00 (self-hosted)",
        "text_capability": "weak",
        "hint": "Run ComfyUI locally (https://github.com/comfyanonymous/ComfyUI). "
                "Set COMFYUI_URL=http://127.0.0.1:8188. Optionally set a workflow JSON path.",
    },
    "google": {
        "label": "Google Imagen (Vertex AI / Gemini API)",
        "env": ["GOOGLE_GENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "GCP_PROJECT"],
        "config_keys": ["api_key", "project", "location", "model"],
        "cost": "~$0.04 (imagen-4) / ~$0.06 (imagen-4-ultra) per image",
        "text_capability": "strong",
        "hint": "Set GOOGLE_GENAI_API_KEY (Gemini API) OR configure gcloud + set "
                "GCP_PROJECT (Vertex AI). See https://ai.google.dev/imagen",
    },
    "openai": {
        "label": "OpenAI gpt-image-1 (best for covers per authorclaw testing)",
        "env": ["OPENAI_API_KEY"],
        "config_keys": ["api_key", "model"],
        "cost": "~$0.04 (standard 1024) / ~$0.19 (high 1536) per image",
        "text_capability": "strong",
        "hint": "Set OPENAI_API_KEY. See https://platform.openai.com/docs/api-reference/images.",
    },
    "fal": {
        "label": "fal.ai (Flux, SDXL, and many models)",
        "env": ["FAL_KEY"],
        "config_keys": ["api_key", "model"],
        "cost": "~$0.01-$0.05 per image depending on model (Flux Pro ~$0.05)",
        "text_capability": "weak",
        "hint": "Set FAL_KEY. autonovel uses fal.ai for cover art. See https://fal.ai/models",
    },
    "ideogram": {
        "label": "Ideogram (best at rendering text on images)",
        "env": ["IDEOGRAM_API_KEY"],
        "config_keys": ["api_key", "model"],
        "cost": "~$0.08 (v2) per image",
        "text_capability": "strong",
        "hint": "Set IDEOGRAM_API_KEY. Best choice if the title must be rendered on the cover. "
                "See https://developer.ideogram.ai/",
    },
    "stability": {
        "label": "Stability AI (Stable Diffusion 3)",
        "env": ["STABILITY_API_KEY"],
        "config_keys": ["api_key", "model"],
        "cost": "~$0.03-$0.065 per image (SD3 Large ~$0.065)",
        "text_capability": "weak",
        "hint": "Set STABILITY_API_KEY. See https://platform.stability.ai/",
    },
    "replicate": {
        "label": "Replicate (many models, including Flux and SDXL)",
        "env": ["REPLICATE_API_TOKEN"],
        "config_keys": ["api_token", "model"],
        "cost": "~$0.01-$0.05 per image depending on model",
        "text_capability": "weak",
        "hint": "Set REPLICATE_API_TOKEN. See https://replicate.com/docs",
    },
}


# --------------------------------------------------------------------------- #
# Config loading
# --------------------------------------------------------------------------- #

def load_config() -> dict:
    cfg = {}
    for path in CONFIG_PATHS:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    cfg.update(json.load(fh))
            except Exception as e:
                print(f"image: warning: could not parse {path}: {e}", file=sys.stderr)
    return cfg


def provider_configured(name: str, cfg: dict) -> bool:
    """True if this provider has its credentials available (env or config)."""
    p = PROVIDERS[name]
    # Check env vars first
    for env in p["env"]:
        if os.environ.get(env):
            return True
    # Then config keys
    sub = cfg.get(name, {})
    if not isinstance(sub, dict):
        return False
    for key in p["config_keys"]:
        # The first mandatory key (api_key/url) must be present
        if key in ("api_key", "url", "api_token") and sub.get(key):
            return True
    return False


def configured_providers(cfg: dict) -> list[str]:
    return [name for name in PROVIDERS if provider_configured(name, cfg)]


def choose_provider(requested: str | None, cfg: dict, needs_text: bool = False) -> str | None:
    """Pick the provider to use. Priority: explicit > text-capable > any configured."""
    configured = configured_providers(cfg)
    if not configured:
        return None
    if requested:
        if requested not in PROVIDERS:
            return None
        return requested if requested in configured else None
    if needs_text:
        # Prefer the strongest text renderer available
        for name in ("ideogram", "openai", "google"):
            if name in configured:
                return name
    return configured[0]


# --------------------------------------------------------------------------- #
# Brief scaffolds
# --------------------------------------------------------------------------- #

BRIEF_TEMPLATES = {
    "cover": """# Cover brief

title: <book title>
author: <author name>
genre: <genre>
subgenre: <optional>
mood: <e.g., brooding / triumphant / wistful / menacing>
era: <historical period or 'contemporary' or 'near future'>
setting: <the world / place — 1-2 sentences, sensory>
keyImagery: <the single strongest visual image — a person, place, object, moment>
palette: <2-4 hex colors or descriptive: 'oxblood and ash', 'ice blue and gunmetal'>
avoidImagery: <what NOT to include>
style: <realistic | illustrated | minimalist | painterly | photographic>
includeText: <true (render title on cover) | false (clean base for manual typesetting)>
""",
    "illustration": """# Illustration brief

chapter: <which chapter this illustrates>
scene: <the specific moment depicted>
characters: <who is in the scene, with physical description markers>
setting: <place, time of day, weather>
mood: <emotional tone>
composition: <framing: close-up / wide / over-the-shoulder / environmental>
palette: <color palette>
style: <realistic | woodcut | watercolor | ink | line drawing>
caption: <optional caption for the image>
""",
    "concept": """# Concept brief

purpose: <what we're exploring visually — character design, location, prop, mood>
variants: <N — generate this many distinct interpretations>
elements: <what MUST appear in every variant>
variation_axes: <what should differ between variants — e.g., 'age, attire, lighting'>
style: <visual style>
""",
}


# --------------------------------------------------------------------------- #
# Aspect ratio presets
# --------------------------------------------------------------------------- #

PRESETS = {
    # (width, height, label)
    "cover":       (1600, 2560, "ebook cover 2:3 (KDP/Apple/Kobo)"),
    "cover-print": (1800, 2700, "print cover front (6x9 trim + bleed)"),
    "illustration":(1600, 1200, "interior illustration 4:3"),
    "square":      (1024, 1024, "square concept"),
    "social":      (1536, 1024, "social media 3:2 (Twitter/BookBub)"),
}


# --------------------------------------------------------------------------- #
# HTTP helper (pure stdlib)
# --------------------------------------------------------------------------- #

def _http_request(url: str, headers: dict, body: bytes | None = None,
                  method: str = "POST", timeout: int = 120):
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read(), dict(resp.headers)


def _save_image(data: bytes, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(data)
    return out_path


def _download(url: str, out_path: str, headers: dict | None = None) -> str:
    h = headers or {}
    status, data, _ = _http_request(url, h, method="GET")
    if status != 200:
        raise RuntimeError(f"download failed ({status}): {url}")
    return _save_image(data, out_path)


# --------------------------------------------------------------------------- #
# Provider implementations (one per provider)
# --------------------------------------------------------------------------- #

def gen_openai(prompt: str, w: int, h: int, out_path: str, cfg: dict,
               include_text: bool = True) -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or cfg.get("openai", {}).get("api_key")
    model = cfg.get("openai", {}).get("model", "gpt-image-1")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    size = _nearest_openai_size(w, h)
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
    }).encode()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    status, resp, _ = _http_request("https://api.openai.com/v1/images/generations",
                                    headers, body, timeout=180)
    if status != 200:
        raise RuntimeError(f"OpenAI error ({status}): {resp[:400].decode('utf-8', 'replace')}")
    data = json.loads(resp)["data"][0]
    if "b64_json" in data:
        import base64
        return _save_image(base64.b64decode(data["b64_json"]), out_path)
    return _download(data["url"], out_path)


def _nearest_openai_size(w: int, h: int) -> str:
    # gpt-image-1 accepts: 1024x1024, 1024x1536 (portrait), 1536x1024 (landscape),
    # and auto. Pick the closest.
    ratio = w / h
    if ratio > 1.2:
        return "1536x1024"
    if ratio < 0.85:
        return "1024x1536"
    return "1024x1024"


def gen_ideogram(prompt: str, w: int, h: int, out_path: str, cfg: dict,
                 include_text: bool = True) -> str:
    api_key = os.environ.get("IDEOGRAM_API_KEY") or cfg.get("ideogram", {}).get("api_key")
    model = cfg.get("ideogram", {}).get("model", "v2")
    if not api_key:
        raise RuntimeError("IDEOGRAM_API_KEY not set")
    body = json.dumps({
        "prompt": prompt,
        "aspect_ratio": _ratio_string(w, h),
        "model": model,
        "magic_prompt_option": "OFF",
        "style_type": "GENERAL",
    }).encode()
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }
    status, resp, _ = _http_request("https://api.ideogram.ai/v1/ideogram-v3/generate",
                                    headers, body, timeout=180)
    if status != 200:
        raise RuntimeError(f"Ideogram error ({status}): {resp[:400].decode('utf-8', 'replace')}")
    data = json.loads(resp)
    url = data["data"][0]["url"]
    return _download(url, out_path)


def _ratio_string(w: int, h: int) -> str:
    from math import gcd
    g = gcd(w, h)
    return f"{w//g}x{h//g}"


def gen_fal(prompt: str, w: int, h: int, out_path: str, cfg: dict,
            include_text: bool = True) -> str:
    api_key = os.environ.get("FAL_KEY") or cfg.get("fal", {}).get("api_key")
    model = cfg.get("fal", {}).get("model", "fal-ai/flux/1.1-pro")
    if not api_key:
        raise RuntimeError("FAL_KEY not set")
    # fal uses a submit + poll pattern via REST
    body = json.dumps({
        "prompt": prompt,
        "image_size": {"width": w, "height": h},
        "num_inference_steps": 50,
    }).encode()
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
    }
    # Submit
    status, resp, _ = _http_request(f"https://queue.fal.run/{model}",
                                    headers, body, timeout=60)
    if status != 200:
        raise RuntimeError(f"fal.ai error ({status}): {resp[:400].decode('utf-8', 'replace')}")
    req_id = json.loads(resp).get("request_id")
    if not req_id:
        raise RuntimeError(f"fal.ai: no request_id in response")
    # Poll for result
    for _ in range(60):  # up to ~5 min
        time.sleep(5)
        s, r, _ = _http_request(f"https://queue.fal.run/{model}/requests/{req_id}/status",
                                headers, method="GET", timeout=30)
        if s == 200:
            st = json.loads(r).get("status")
            if st == "COMPLETED":
                s2, r2, _ = _http_request(
                    f"https://queue.fal.run/{model}/requests/{req_id}",
                    headers, method="GET", timeout=30)
                if s2 == 200:
                    img_url = json.loads(r2).get("images", [{}])[0].get("url")
                    if img_url:
                        return _download(img_url, out_path)
            elif st == "FAILED":
                raise RuntimeError(f"fal.ai: generation failed")
    raise RuntimeError("fal.ai: timed out waiting for result")


def gen_google(prompt: str, w: int, h: int, out_path: str, cfg: dict,
               include_text: bool = True) -> str:
    api_key = os.environ.get("GOOGLE_GENAI_API_KEY")
    project = os.environ.get("GCP_PROJECT") or cfg.get("google", {}).get("project")
    model = cfg.get("google", {}).get("model", "imagen-4.0-generate-001")
    if api_key:
        # Gemini API path (developer key)
        body = json.dumps({
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": _ratio_string(w, h)}
        }).encode()
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
               f"?key={api_key}")
        headers = {"Content-Type": "application/json"}
        status, resp, _ = _http_request(url, headers, body, timeout=180)
        if status != 200:
            raise RuntimeError(f"Google Imagen error ({status}): {resp[:400].decode('utf-8','replace')}")
        import base64
        b64 = json.loads(resp)["predictions"][0]["bytesBase64Encoded"]
        return _save_image(base64.b64decode(b64), out_path)
    raise RuntimeError("Google Imagen needs GOOGLE_GENAI_API_KEY (Gemini API) configured. "
                       "Vertex AI auth via gcloud is supported but requires more setup — see references/images.md.")


def gen_stability(prompt: str, w: int, h: int, out_path: str, cfg: dict,
                  include_text: bool = True) -> str:
    api_key = os.environ.get("STABILITY_API_KEY") or cfg.get("stability", {}).get("api_key")
    model = cfg.get("stability", {}).get("model", "sd3-large")
    if not api_key:
        raise RuntimeError("STABILITY_API_KEY not set")
    # Stability uses multipart form data
    boundary = "----bookforge" + str(int(time.time()))
    parts = []
    for key, val in [("prompt", prompt), ("output_format", "png"),
                     ("aspect_ratio", _ratio_string(w, h))]:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f'name="{key}"\r\n\r\n{val}\r\n')
    body = ("".join(parts) + f"--{boundary}--\r\n").encode()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    url = f"https://api.stability.ai/v2beta/stable-image/generate/sd3"
    status, resp, _ = _http_request(url, headers, body, timeout=180)
    if status != 200:
        raise RuntimeError(f"Stability error ({status}): {resp[:400].decode('utf-8','replace')}")
    # Returns image bytes directly
    return _save_image(resp, out_path)


def gen_replicate(prompt: str, w: int, h: int, out_path: str, cfg: dict,
                  include_text: bool = True) -> str:
    token = os.environ.get("REPLICATE_API_TOKEN") or cfg.get("replicate", {}).get("api_token")
    model = cfg.get("replicate", {}).get("model", "black-forest-labs/flux-1.1-pro")
    if not token:
        raise RuntimeError("REPLICATE_API_TOKEN not set")
    version_suffix = model.split("/")[-1] if "/" in model else model
    body = json.dumps({"input": {"prompt": prompt, "aspect_ratio": _ratio_string(w, h)}}).encode()
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
        "Prefer": "wait",  # synchronous mode where supported
    }
    url = f"https://api.replicate.com/v1/models/{model}/predictions"
    status, resp, _ = _http_request(url, headers, body, timeout=300)
    if status not in (200, 201):
        raise RuntimeError(f"Replicate error ({status}): {resp[:400].decode('utf-8','replace')}")
    data = json.loads(resp)
    output = data.get("output")
    if isinstance(output, list) and output:
        return _download(output[0], out_path)
    if isinstance(output, str):
        return _download(output, out_path)
    raise RuntimeError(f"Replicate: no image URL in response")


def gen_comfyui(prompt: str, w: int, h: int, out_path: str, cfg: dict,
                include_text: bool = True) -> str:
    base = os.environ.get("COMFYUI_URL") or cfg.get("comfyui", {}).get("url", "http://127.0.0.1:8188")
    workflow_path = cfg.get("comfyui", {}).get("workflow")
    # If a pre-built workflow JSON is provided, use it; otherwise build a minimal
    # txt2img workflow via the /prompt API.
    if workflow_path and os.path.isfile(workflow_path):
        with open(workflow_path) as fh:
            workflow = json.load(fh)
        # Inject prompt + dimensions into the workflow's CLIPTextEncode + EmptyLatentImage nodes.
        # (Workflow authors parametrize these; we look for known node titles.)
        for node in workflow.values():
            if isinstance(node, dict):
                if node.get("class_type") == "CLIPTextEncode" and node.get("_meta", {}).get("title", "").lower().startswith("positive"):
                    node["inputs"]["text"] = prompt
                if node.get("class_type") == "EmptyLatentImage":
                    node["inputs"]["width"] = w
                    node["inputs"]["height"] = h
    else:
        # Minimal default workflow (basic txt2img)
        workflow = _default_comfyui_workflow(prompt, w, h)
    body = json.dumps({"prompt": workflow}).encode()
    headers = {"Content-Type": "application/json"}
    status, resp, _ = _http_request(f"{base}/prompt", headers, body, timeout=60)
    if status != 200:
        raise RuntimeError(f"ComfyUI error ({status}): {resp[:400].decode('utf-8','replace')}")
    prompt_id = json.loads(resp).get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI: no prompt_id returned")
    # Poll history
    for _ in range(120):
        time.sleep(3)
        s, r, _ = _http_request(f"{base}/history/{prompt_id}", {}, method="GET", timeout=30)
        if s == 200:
            hist = json.loads(r).get(prompt_id)
            if hist and hist.get("status", {}).get("completed"):
                outputs = hist.get("outputs", {})
                for node_out in outputs.values():
                    for img in node_out.get("images", []):
                        img_url = f"{base}/view?filename={img['filename']}&subfolder={img.get('subfolder','')}&type={img.get('type','output')}"
                        return _download(img_url, out_path)
            if hist and hist.get("status", {}).get("status_str") == "error":
                raise RuntimeError("ComfyUI: workflow execution error")
    raise RuntimeError("ComfyUI: timed out waiting for generation")


def _default_comfyui_workflow(prompt: str, w: int, h: int) -> dict:
    """A minimal valid ComfyUI txt2img workflow graph."""
    return {
        "3": {"class_type": "KSampler", "inputs": {
            "seed": int(time.time()) % (2**32), "steps": 30, "cfg": 8,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1,
            "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
            "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]},
              "_meta": {"title": "Positive prompt"}},
        "7": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "text, watermark, signature, low quality, deformed",
                         "clip": ["4", 1]}, "_meta": {"title": "Negative prompt"}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0]}},
    }


PROVIDER_FUNCS = {
    "openai": gen_openai,
    "ideogram": gen_ideogram,
    "fal": gen_fal,
    "google": gen_google,
    "stability": gen_stability,
    "replicate": gen_replicate,
    "comfyui": gen_comfyui,
}


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_providers(cfg: dict) -> int:
    print("Image providers:")
    print()
    configured = configured_providers(cfg)
    for name, p in PROVIDERS.items():
        mark = "✓" if name in configured else "·"
        print(f"  {mark} {name:12} {p['label']}")
        print(f"      cost: {p['cost']}")
        print(f"      text-on-image: {p['text_capability']}")
        print(f"      env: {', '.join(p['env'])}")
        if name not in configured:
            print(f"      setup: {p['hint']}")
        print()
    if not configured:
        print(f"No providers configured. Set one of the env vars above, or")
        print(f"create a config file at one of:")
        for path in CONFIG_PATHS:
            print(f"  {path}")
        print(f"\nTemplate: {SKILL_DIR}/assets/image-config.example.json")
        return 1
    print(f"{len(configured)} provider(s) configured: {', '.join(configured)}")
    return 0


def cmd_brief(brief_type: str) -> int:
    if brief_type not in BRIEF_TEMPLATES:
        print(f"unknown brief type: {brief_type}. Valid: {list(BRIEF_TEMPLATES)}", file=sys.stderr)
        return 2
    out = f"image-brief-{brief_type}.md"
    with open(out, "w") as fh:
        fh.write(BRIEF_TEMPLATES[brief_type])
    print(f"wrote {out} — fill it in, then run: image.py {brief_type} {out}")
    return 0


def cmd_generate(args, cfg: dict) -> int:
    # Read brief from file or treat arg as inline prompt
    prompt = args.brief
    if os.path.isfile(args.brief):
        with open(args.brief, "r", encoding="utf-8", errors="replace") as fh:
            brief_text = fh.read()
        # Naive extraction: use the whole brief, but strip comments
        prompt = _extract_prompt_from_brief(brief_text)
        include_text = "includeText: true" in brief_text or "includeText:true" in brief_text
    else:
        include_text = True

    w, h = args.width, args.height
    needs_text = include_text and args.command in ("cover", "cover-print")
    provider = choose_provider(args.provider, cfg, needs_text=needs_text)

    if not provider:
        print("No image provider configured. Set one of:", file=sys.stderr)
        for name, p in PROVIDERS.items():
            print(f"  {name}: env {', '.join(p['env'])}")
        print(f"\nTemplate: {SKILL_DIR}/assets/image-config.example.json")
        print("Or run: image.py providers")
        return 1

    if provider != args.provider and args.provider:
        print(f"warning: requested provider '{args.provider}' not configured, "
              f"using '{provider}' instead", file=sys.stderr)

    # Cost notice
    print(f"provider: {provider} ({PROVIDERS[provider]['label']})")
    print(f"cost:     {PROVIDERS[provider]['cost']}")
    print(f"size:     {w}x{h}")
    print(f"text:     {'on-image' if include_text and needs_text else 'clean base'}")
    print(f"prompt:   {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    print()

    if args.dry_run:
        print("--dry-run: not generating.")
        return 0

    if not args.yes:
        try:
            answer = input("Generate? [y/N] ")
            if answer.lower() not in ("y", "yes"):
                print("aborted.")
                return 1
        except EOFError:
            pass  # non-interactive; proceed

    # Output path
    if not args.out:
        slug = args.command
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        args.out = os.path.join("images", f"{slug}-{ts}.png")

    try:
        fn = PROVIDER_FUNCS[provider]
        path = fn(prompt, w, h, args.out, cfg, include_text=include_text)
        size_kb = os.path.getsize(path) // 1024
        print(f"\n✓ wrote {path} ({size_kb} KB)")
        return 0
    except Exception as e:
        print(f"\n✗ generation failed: {e}", file=sys.stderr)
        if PROVIDERS[provider]["text_capability"] == "weak" and needs_text:
            print(f"  note: {provider} is weak at rendering text. "
                  "Retry with --provider ideogram or openai, or generate a "
                  "clean base and typeset the title manually.", file=sys.stderr)
        return 2


def _extract_prompt_from_brief(text: str) -> str:
    """Turn a filled brief into a single image prompt."""
    lines = [l for l in text.split("\n") if l.strip() and not l.startswith("#")]
    parts = []
    for l in lines:
        if ":" in l:
            k, _, v = l.partition(":")
            k, v = k.strip(), v.strip().strip("<>")
            if v and v.lower() not in ("true", "false"):
                parts.append(f"{k.strip()}: {v}")
    # Compose into a single descriptive prompt
    return ". ".join(parts) + "."


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="book-forge image generator")
    p.add_argument("command",
                   choices=["providers", "brief",
                            "cover", "cover-print", "illustration", "concept",
                            "generate"])
    p.add_argument("brief", nargs="?", default=None,
                   help="brief file (.md) or inline prompt text")
    p.add_argument("--provider", default=None,
                   help="force a provider (overrides auto-detection)")
    p.add_argument("--out", default=None, help="output path (default: images/<cmd>-<ts>.png)")
    p.add_argument("--variants", type=int, default=1, help="number of variants (concept only)")
    p.add_argument("--width", type=int, default=None)
    p.add_argument("--height", type=int, default=None)
    p.add_argument("--dry-run", action="store_true", help="show what would be sent, don't generate")
    p.add_argument("--yes", action="store_true", help="skip confirmation prompt")
    args = p.parse_args(argv)

    cfg = load_config()

    if args.command == "providers":
        return cmd_providers(cfg)

    if args.command == "brief":
        if not args.brief:
            print("brief type required: cover | illustration | concept", file=sys.stderr)
            return 2
        return cmd_brief(args.brief)

    # Preset sizing
    preset = None if args.command == "generate" else args.command
    if preset and preset in PRESETS:
        w, h, label = PRESETS[preset]
        args.width = args.width or w
        args.height = args.height or h
        if not args.dry_run and not args.yes:
            print(f"preset: {preset} ({label})")
    elif args.command == "generate":
        args.width = args.width or 1024
        args.height = args.height or 1024
    else:
        print(f"unknown preset: {args.command}", file=sys.stderr)
        return 2

    return cmd_generate(args, cfg)


if __name__ == "__main__":
    raise SystemExit(main())
