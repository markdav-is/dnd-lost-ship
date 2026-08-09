[Reference](../Reference.md) / Aerun Map Prompts <!-- wikidown:breadcrumb -->

# Aerun Map Prompts

Image-generation prompts for the new Aerun map set. The continent prompt is first; the drill-in template at the bottom generates regional maps as needed. Source geography: [the Glossary](../World/Dark-Sun/Glossary.md); shape reference: `assets/vermoon-map.png`; style reference: `assets/aerun_map.png` and `assets/scarlands_completed_map.png`.

## The continent prompt (v2 — plateau-explicit)

> A detailed fantasy atlas map of the desert island continent of **AERUN**, painted like a premium D&D campaign-setting poster: top-down painterly cartography with strong 3D terrain relief, weathered parchment-and-ocean palette, dark teal textured sea, ornate silver compass rose, elegant serif labels. Landscape 4:3. Title "AERUN" upper right; **scale bar reading 0–100–200 miles** (the continent spans ~500 miles).
>
> **THE ONE BIG IDEA — READ FIRST:** the center of this island is a **colossal flat-topped MESA** — a tableland plateau like Monument Valley scaled to half a continent. **The flat TOP of the mesa is a smooth, pale-gray dust plain (the Sea of Silt).** The gray plain is the HIGHEST large surface on the map — higher than all the green land, higher than everything except a few mountain peaks. This is a RAISED TABLE, absolutely not a crater, not a lake, not a lowland, not a shoreline.
>
> **BUILD THE TERRAIN BOTTOM-TO-TOP, three altitude bands:**
> 1. **Sea level — the ocean:** dark teal water surrounding the island on all sides. Sailing ships near harbors.
> 2. **The green coastal ring (low):** a band of living lowland around the island's entire edge — farmland, olive terraces, scrub, forest on the east — carrying **THE RING ROAD**, a continuous ochre caravan highway through every city, with tiny mekillot-wagon icons. All twelve settlements live in this band.
> 3. **The central mesa (high):** rising from the middle of the green ring, **steep terracotta cliff walls climb ~2,000 feet** on every side to the tabletop. **The tabletop is the Sea of Silt: featureless matte bone-gray dust, dead flat, with faint wind-ripples and slow spiral storm textures.** Label the gray plain "THE SEA OF SILT" and the cliff ring "THE RIM WALL."
>
> **HOW TO MAKE THE ELEVATION READ (do all of these):**
> - **Shadow logic:** light from the northwest; the mesa's southeastern cliff walls cast one continuous soft shadow band **outward onto the green lowlands**. The gray tabletop is brightly, evenly lit.
> - **Cliff texture:** the mesa edge is everywhere a rendered cliff face — vertical striations, buttresses, scree fans at the foot — with the **gray always meeting the TOP edge of the cliff** and green always at the BOTTOM.
> - **Silt-falls:** at several low notches in the rim, thin gray dust-falls spill over the edge and streak partway down the cliff face, like slow waterfalls of powder.
> - **Mountain overlaps:** along the northwest–southwest arc, the **Ringing Mountains** rise from the coastal ring and stand **taller than the mesa** — peaks overlapping in front of and above the tabletop edge, with one smoking **volcano (the Mountain of the Black Crown)** near Urik. On the east, rust-red **Badlands** mesas rise behind the Crescent Forest to shoulder height with the rim.
> - **The two spill-ramps:** at the mesa's **northeast** (toward Raam) and **south** (toward Balic), the gray descends the wall in broad **stepped, terraced ramps** — frozen lobes of silt stair-stepping partway down — the northeast one stopping at a shelf above Raam, the southern one a single broad ramp stopping dead at a **rock dam** on whose face the city of Balic is built. **The gray NEVER reaches the ocean.**
>
> **ON THE GRAY TABLETOP (sparse):** a faint dotted **shipping lane** arcing across the eastern and southern reaches from the Raam ramp to the Balic ramp, with tiny bone channel-markers and two or three skimmer-convoy icons. **The entire northwestern third of the gray: completely empty. No lane, no icons, no labels, no texture variation. Blank.**
>
> **THE TWELVE SETTLEMENTS** (city icons as small dots-with-architecture at this 500-mile scale), clockwise from north: **DRAJ** (north coast, on a brown mudflat apron at the cliff's foot, stone causeway) · **BLACKGUARD** (grim NE-coast waypoint) · **RAAM** (northeast, largest icon, between its blue ocean harbor and the silt shelf-ramp above it) · **NIBENAY** (east, forest edge, rice paddies) · **GULG** (southeast, a green ring inside the Crescent Forest) · **AMBER VALLEY** (south-coast caravanserai) · **BALIC** (south coast, white harbor city built into the rock dam at the foot of the southern silt-ramp — ocean on one side, gray above on the other) · **URIK** (southwest, square yellow fortress-city under the volcano) · **HOLLOWSTORM** (west promontory) · **OSGAKER** (northwest coast) · **TYR** (northwest foothills, ziggurat and stadium) · **ELDORADO** (small town at a high rim pass behind Tyr).
>
> **LANDMARKS** (small icons, fine labels, all in the green band unless noted): the **Dragon's Bowl** — an irregular, elongated sunken basin in the barrens north of Urik (**outside the mesa, in the lowlands**) holding the tiny brilliant-blue **Lake Pit**, the only true blue water inland · ruins of **Yaramuke** with a black-stained oasis, between Urik and Raam · **Altaruk**, a walled caravan fort on the southern Ring Road · the **Mekillot Mountains** with **Salt View** · **Walis** on its rock spire · **Ogo** under the forest canopy · **Bitter Well** on the western scrub.
>
> **FORBIDDEN (hard negatives):** do not render the gray as a lake, bay, inland sea at coast level, crater, or depression. No beaches or shorelines where gray meets green at equal height. No water touching the gray anywhere. No green or roads on the tabletop. The gray is never darker or lower-looking than the coastal ring — it is the bright, high, empty roof of the map.
>
> **MOOD:** sun-bleached and majestic; a living green ring of commerce hugging the shores of an island crowned by a vast dead gray table — and faint wakes of something enormous moving beneath the dust, subtle enough to miss.

## Iteration notes

- If the generator fights the gray silt (defaults to sand), lead with: "The interior is GRAY DUST, the color of ash and bone — not a sand desert."
- If city icons come out generic, run the drill-in prompts below and composite.
- The First Source is **never marked** — [the Veil](../Campaign/Plot-Threads/The-First-Source.md) applies to cartographers too.

## Drill-in template (regional maps)

> A detailed fantasy regional map, painted in the same style as [describe/attach the continent map]: top-down painterly cartography, soft 3D relief, parchment palette, serif labels, compass rose. This map covers **[REGION]** of the desert continent of Aerun — roughly [WHICH ARC of the coastal ring], with the ocean on one side and the gray Sea of Silt behind the Rim Wall cliffs on the other. The Ring Road crosses the whole map through [CITIES]. Show: [CITY-SPECIFIC TERRAIN + LANDMARK LIST from the Glossary geography table]. City icons are large and architecturally distinct: [CITY ICON NOTES]. Mood: [MOOD].

**Planned drill-ins** (one per session of need):

1. **The Northwest** — Tyr, Eldorado, Osgaker: Ringing Mountains, iron terraces, Walis spire, the Rim Wall pass.
2. **The Southwest** — Urik and the Black Crown: the volcano, obsidian quarries, Yaramuke ruins on the Raam road — and the **Dragon's Bowl**: an irregular, *elongated* sunken basin with a ragged thousand-foot rim (emphatically not a neat circle), 35–50 miles long, Lake Pit's blue water in the northern lobe, and one torn-looking breach in the southern rim.
3. **The South** — Balic and the dam: the two-seas harbor, the Cochlea, the southern silt-ramp, Altaruk road-fort, Mekillot Mountains + Salt View, Amber Valley.
4. **The East** — Nibenay and Gulg: the Crescent Forest between them, rice springs, the hedge-ring with **Sunlight Home**'s titanic tree rising from its center, Ogo, the **Witchgrove** deep in the forest (a darker, denser, *wrong-looking* stand of trees), Badlands behind.
5. **The North** — Draj, Blackguard, Raam: the mudflats and causeway, the silt arm, the sprawl.
