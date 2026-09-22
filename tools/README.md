# tools

Small stdlib-only scripts for the campaign. No pip installs.

## gen_image.py — campaign art via Gemini (ElevenLabs as backup)

**Gemini is the default and the one in use** (no Flux account as of 2026-09-22). Use `--pro` (gemini-3-pro-image) for encounter art and portraits.

- **Gemini** (Nano Banana), the default: `GEMINI_API_KEY`, from https://aistudio.google.com/apikey. Good at holding a face across scenes from a `--ref` portrait, and at maps with labels. Moderation is stricter. `--pro` uses gemini-3-pro-image, the newest Google image model on the key.
- **Flux** (Black Forest Labs), dormant: `BFL_API_KEY`, from https://dashboard.bfl.ai → API → Keys. It runs only with `--backend flux`. FLUX.2 [pro] from $0.03 an image; `--pro` uses FLUX.2 [max].
- **ElevenLabs**, the backup: `ELEVENLABS_API_KEY` (the podcast key). `--backend elevenlabs` serves the same Gemini models on ElevenLabs credits, and `--model` picks any other model it serves (`gpt-image-2`, `gpt-image-2.5-sunburst`, `bytedance-seedream-5-pro`, …). No Flux here; Flux is web-UI only on ElevenLabs. If Google answers 429 (quota spent), the tool switches to ElevenLabs by itself and says so; `--no-fallback` stops that. **The endpoint needs an ElevenLabs Pro plan or above.** On the current plan it answers 402 `paid_plan_required` (checked 2026-09-22), so this backend is ready but won't run until the plan is upgraded.

```
py tools/gen_image.py --list-styles
py tools/gen_image.py --prompt-file tools/prompts/erleena_portrait.txt --style erleena --ref docs/.attachments/erleena_riser.jpg --out docs/.attachments/erleena_portrait.jpg
py tools/gen_image.py --prompt-file tools/prompts/enc_lab_at_s42.txt --style alpha --out docs/.attachments/enc_lab_at_s42.jpg
py tools/gen_image.py --prompt-file tools/prompts/enc_beneath_the_lighthouse.txt --style sickbay --ref docs/.attachments/erleena_portrait.jpg --out docs/.attachments/enc_beneath_the_lighthouse.jpg
```

- `--style <name>` prepends `tools/styles/<name>.txt` — the house-style blocks (`alpha` = lit ship, *Space: 1999* look; `dark` = the mold side; `sickbay` = Erleena's lab; `erleena` = her face and uniform). Edit these rather than repeating the look in every prompt.
- `alpha_still` is the photographic take on `alpha`: a 35mm production still from a 1975 TV set rather than a painting. Used for the 2026-09-22 S42 set (`george_portrait_s42`, `enc_s42_reveal`, `enc_s42_demonstration`, `enc_s42_fitting`), with the portrait passed as `--ref` to hold George's face.
- `--ref <image>` (repeatable, up to 8 on Flux) attaches reference images: a previous render to keep the layout, a portrait to keep a face, `medical_android.png` for the uniform.
- `--aspect` defaults to `3:2` to match the existing encounter art; `--size` defaults to `2K` (about 3.5 MP on Flux, which costs a little more than the 1 MP base).
- `--safety 0-5` (Flux only) sets moderation tolerance; default 4.
- Every render writes `tools/renders/<name>.prompt.txt` with the backend, model, settings, and the full prompt used, so a pass can be reproduced.

Scene prompts live in `tools/prompts/`. Keep them about the scene; keep the style in the style files.

### City maps

The seven Aerun city prompts are exported from the wiki page `/Reference/Aerun-Map-Prompts` as `tools/prompts/city_<name>.txt` (tyr, draj, raam, nibenay, gulg, balic, urik), with the shared cartography preamble as the `citymap` style. Maps carry labels, so use the **Gemini** backend, 4:3, and pass the approved atlas (and the previous render, to keep the layout) as references:

```
py tools/gen_image.py --backend gemini --pro --aspect 4:3 --prompt-file tools/prompts/city_raam.txt --style citymap --ref docs/.attachments/aerun_atlas.png --ref docs/.attachments/raam_city.png --out docs/.attachments/raam_city.png
```

The wiki page is the source of truth: edit the prompt there, then re-export. The current set (2026-09-21) drops every temple label — there are no gods on Aerun — and adds one **Spáhus** per city plus the outland-guild sites (Gleaners' Quarter in Raam, Sun Garden in Nibenay, Seed Hall and Moon Houses in Draj, the Gleaners' hall / G4CE office / Academy of the Fettered Mind in Balic, Bureau District in Tyr).

## make_gallery.py — the wiki Gallery page

```
py tools/make_gallery.py --write
```

Scans every image in `docs/.attachments/`, makes a 360-px thumbnail in `docs/.attachments/thumbs/` (only when the source is newer), works out which pages embed each one, and writes the `/Gallery` page — grouped by subject, each thumbnail linking to the full image and its page. Run it after adding or replacing art. Needs Pillow (already installed). `--write` publishes through the `wikidown` CLI so `.order` and breadcrumbs stay right; without it the markdown just lands in `tools/renders/gallery.md`.
