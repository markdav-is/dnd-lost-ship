[Reference](../Reference.md) / Aerun Atlas Handoff <!-- wikidown:breadcrumb -->

# Aerun Atlas — Generation Handoff Notes

*Written after the v6–v11 generation session. Read this before attempting another atlas generation pass.*

> **Canon updates since this was written** (see [Aerun Map Prompts](Aerun-Map-Prompts.md) for the current prompts and revision brief):
> - The southern **"silt finger"** is superseded — the plateau edge now **sweeps** from Raam down the eastern coast to Balic in one long arc (no peninsula, no pointed lobe).
> - The wall **grades down going south**, reaching the **Balic Saddle** at only two or three hundred feet — Balic sits *in a gap*, not at the foot of a cliff.
> - The **Ringing Mountains run the entire west coast**, and the **prevailing winds always blow from the west** (the rain-shadow explanation).
> - **Draj's stone causeway is canon** — the wiki has it as the city's whole defense. This page's "no causeway" note was a workaround for a *rendering* fault: the generator kept drawing the causeway running out into the silt sea. The fix is direction, not deletion — **the causeway runs landward, from the Ring Road on firm ground across the mudflats to the city gate, at sea level. It never touches the silt and never climbs the wall.**

## The best version so far

**`assets/Aerun_Atlas.png`** (the final; the numbered drafts including v10 have been deleted) — the version this page was written against had. It has:
- Correct mesa/plateau geography: cliff faces pointing outward, silt on top as high ground
- The southern silt finger/point pressing down toward Balic (correct shape)
- Balic correctly scaled and at the cliff base
- Raam perfectly rendered — built into the northeast cliff, ocean harbor below, silt shelf above
- Draj on the mudflat with no causeway
- Dragon's Bowl in the lowlands near Urik with Lake Pit as the only blue inland water
- Ring Road, Crescent Forest, Gulg hedge-ring, Badlands, Yaramuke, Bitter Well all correct
- Scale bar and compass rose

**What v10 still needed** (do not re-introduce these problems):
- Balic needed to be on the coast with ships in its harbor — the coastline needed to be pulled inward to meet it, not Balic moved
- The Ring Road gap between Balic and Amber Valley needed closing
- The north rim needed more cliff-face texture to read as elevated
- The silt plateau rim was slightly too heart-shaped/symmetric — needed more irregular geology
- "Walis" label kept rendering as "Walls" — text artifact, accept it or fix in post

## The core geography — never lose this

**The ONE BIG IDEA:** Aerun's center is a **colossal flat-topped MESA** — Monument Valley scaled to half a continent. The Sea of Silt is the flat TOP of that mesa. It is the HIGHEST surface on the map. The Rim Wall cliffs face OUTWARD toward the coast. The coast is LOW. The silt is HIGH.

**The three altitude bands (bottom to top):**
1. Ocean (sea level) — dark teal, ships near harbors
2. Green coastal ring (low) — farmland, scrub, forest, all cities, the Ring Road
3. Central mesa (high) — flat bone-gray silt plateau, cliff edges all around

**The two portage cities built into the cliff:**
- **Raam** (northeast): ocean harbor at sea level on its east face; silt shelf ~1,000 ft above on its west face; the city is built into the cliff between them — terraced, carved into the rock. This was rendered perfectly in v6 and preserved through v10. Do not change it.
- **Balic** (south): Minas Tirith built into the cliff. Tiered city carved into the rock face where the southern silt finger meets the coast. Ocean harbor at the bottom (south face, ships in water). Silt quays at the top. The city is SMALL at continental scale — a compact icon, not a grand palace complex. The coastline comes right up to it.

**The southern silt finger:** the plateau has a pointed lobe pressing south toward Balic — like a broad finger or gentle point. The cliff runs down the sides of this finger. Balic sits at the very tip where the cliff meets the ocean.

**Draj:** sits alone on a brown mudflat island on the north coast. No causeway, no bridge. The Ring Road runs along the coast nearby but no physical connection is drawn.

## What breaks the generation

- **Iterating too many changes at once** — each pass should fix ONE or TWO things maximum. When you ask for three or more changes, the generator starts losing previously correct elements.
- **The silt color** — the generator defaults to warm tan/sand or watery blue-gray. The correct color is **cool bone-gray, the color of dry cement and ash, matte and flat**. Lead every prompt with this if the color drifts.
- **Balic scale** — the generator wants to make Balic enormous and ornate. Keep explicitly calling it "small compact icon, same scale as Urik or Tyr."
- **The Draj causeway** — the generator keeps adding a causeway to Draj. Explicitly say "no causeway, no bridge" every time.
- **Text labels** — "Walis" renders as "Walls" consistently. Accept this or fix in post with image editing. Do not burn a generation pass on it.
- **The Rim Wall label** — tends to disappear in refinement passes. Add it back explicitly when needed.

## Generation strategy that worked

- **Start fresh with `generate_image` (not `generate_image_variation`)** when the reference image has accumulated too many problems. v6 was a clean start that got the mesa concept right for the first time.
- **Use `gpt-image-2` model** for refinement passes — it preserves the reference image better than default.
- **Use `quality: high`** — worth the extra time for this level of detail.
- **Reference the best version** — always use the cleanest prior version as the reference, not the most recent one if it drifted.
- **The Mesa/Monument Valley/Salar de Uyuni analogies** work well in prompts. Use them.
- **"Minas Tirith built into the cliff"** is the correct Balic reference and the generator understands it.

## Remaining issues for next session

1. Silt color still drifts warm/watery — needs a dedicated pass or post-processing
2. North rim cliff faces need more texture (reads as flat ground near Draj)
3. Ring Road gap between Balic and Amber Valley (v11 fixed this but introduced other problems)
4. Coastline near Balic should be pulled inward so Balic sits on the ocean
5. Rim Wall label missing
6. "Walis" → "Walls" label artifact
7. The silt plateau shape could be more geographically irregular (less heart-like) — but do this LAST, as a single dedicated pass, not combined with other changes
