# tools

Small stdlib-only scripts for the campaign. No pip installs.

## gen_image.py — campaign art via Flux or Gemini

Two backends, picked by which key is set:

- **Flux** (Black Forest Labs) — `BFL_API_KEY`, from https://dashboard.bfl.ai → API → Keys. Preferred for encounter art and portraits: painterly, matches the existing pieces, rarely refuses fantasy scenes. FLUX.2 [pro] from $0.03 an image; `--pro` uses FLUX.2 [max].
- **Gemini** (Nano Banana) — `GEMINI_API_KEY`, from https://aistudio.google.com/apikey. Better for maps and anything with labels; stricter moderation. `--pro` uses gemini-3-pro-image.

Set both and pick with `--backend flux|gemini`.

```
py tools/gen_image.py --list-styles
py tools/gen_image.py --prompt-file tools/prompts/erleena_portrait.txt --style erleena --ref docs/.attachments/erleena_riser.jpg --out docs/.attachments/erleena_portrait.jpg
py tools/gen_image.py --prompt-file tools/prompts/enc_lab_at_s42.txt --style alpha --out docs/.attachments/enc_lab_at_s42.jpg
py tools/gen_image.py --prompt-file tools/prompts/enc_beneath_the_lighthouse.txt --style sickbay --ref docs/.attachments/erleena_portrait.jpg --out docs/.attachments/enc_beneath_the_lighthouse.jpg
```

- `--style <name>` prepends `tools/styles/<name>.txt` — the house-style blocks (`alpha` = lit ship, *Space: 1999* look; `dark` = the mold side; `sickbay` = Erleena's lab; `erleena` = her face and uniform). Edit these rather than repeating the look in every prompt.
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
