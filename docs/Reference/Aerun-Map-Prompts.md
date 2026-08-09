[Reference](../Reference.md) / Aerun Map Prompts <!-- wikidown:breadcrumb -->

# Aerun Map Prompts

Image-generation prompts for the new Aerun map set. The continent prompt is first; the drill-in template at the bottom generates regional maps as needed. Source geography: [the Glossary](../World/Dark-Sun/Glossary.md); shape reference: `assets/vermoon-map.png`; style reference: `assets/aerun_map.png` and `assets/scarlands_completed_map.png`.

## The continent prompt

> A detailed fantasy atlas map of the desert island continent of **AERUN**, painted in the style of a premium D&D campaign-setting poster map: top-down painterly cartography with soft 3D terrain relief, weathered parchment-and-ocean palette, dark teal textured sea, an ornate silver compass rose in one corner, and elegant serif place-name labels. Landscape orientation, 4:3. Title "AERUN" in large pale serif capitals, upper right. Small caption at bottom center: "A revised Dark Sun–inspired campaign map."
>
> **CONTINENT SHAPE (match exactly):** a broad, roughly oval island continent, slightly wider in the south, with a distinctive **notched bay and promontory on the west coast**, a **broad rounded peninsula lobe on the northwest**, a gently bulging smooth east coast, and a rounded southern coast with small bays. Two or three tiny rocky islets offshore to the west and northwest. Open ocean on all sides.
>
> **THE INTERIOR — THE SEA OF SILT:** the entire heart of the continent is a vast inland sea of **powder-fine pale-gray silt** — not sand-colored: a flat, matte, bone-gray dust ocean with faint wind-ripple textures and slow spiral storm patterns, visibly *lower and stranger* than the living coast. It is ringed by **the Rim Wall**: a continuous ring of sheer ochre cliffs separating the green coastal band from the gray interior. One long **arm of the silt reaches northeast** to touch the coast near the city of Raam, and one narrow **silt estuary (the Forked Tongue Estuary)** breaks through the Rim Wall in the south, reaching the ocean beside the city of Balic, with a few small islands in its channel. **Leave the deep center of the silt completely empty and featureless — no landmarks, no labels.** Label the interior "THE SEA OF SILT" and the cliff ring "THE RIM WALL."
>
> **THE COASTAL RING:** a band of habitable land between the ocean and the Rim Wall, cycling through terrain as it rounds the continent: green farmland and olive terraces in the south, scrub plains and stony barrens in the west and southwest, verdant foothill gardens in the northwest, fertile brown **mudflats** in the north, and a lush green **forest crescent (the Crescent Forest)** on the east coast with rust-red **Badlands** mesas rising behind it. A great **mountain range (the Ringing Mountains)** runs along the northwest-to-southwest arc behind the coast, with one distinct **volcano (the Mountain of the Black Crown)** at its southern end near Urik.
>
> **THE RING ROAD:** a single continuous, prominently drawn caravan highway circling the whole continent through every city — a warm ochre road with tiny painted wagon-train and giant-lizard-caravan icons spaced along it. Label it "THE RING ROAD" twice, on opposite sides of the continent.
>
> **THE SEVEN CITIES** (walled city icons, largest icons on the map), clockwise from the north:
> - **DRAJ** — north coast, built on a brown mudflat island amid fertile fields, connected to the Ring Road by a single stone causeway; a small stepped pyramid at its center.
> - **BLACKGUARD** — small grim walled waypoint town on the north-northeast coast.
> - **RAAM** — northeast, a huge sprawling city where the silt arm meets the coast; the largest city icon, chaotic and unwalled at its edges.
> - **NIBENAY** — east coast, at the northern edge of the Crescent Forest, surrounded by spring-fed rice paddies; ornate carved-stone look.
> - **GULG** — southeast, *inside* the Crescent Forest: not a built city but a great green ring — a circular living hedge wall with hut clusters and one giant tree at the center.
> - **AMBER VALLEY** — small caravanserai town on the southern Ring Road.
> - **BALIC** — south coast where the Forked Tongue Estuary meets the ocean: a white-stone harbor city between two seas, ocean port on one side, silt docks on the other, olive groves around it.
> - **URIK** — southwest, a square, brutally fortified fortress-city with high yellow walls, near the black volcano; obsidian quarry scars on the mountainside.
> - **HOLLOWSTORM** — fishing town on the western promontory at the notched bay.
> - **OSGAKER** — small salvage-port town on the west-northwest coast.
> - **TYR** — northwest, in the green foothills of the Ringing Mountains, with iron-mine terraces above it, a stadium and a great ziggurat visible in its icon.
> - **ELDORADO** — small inland town at a pass in the Rim Wall behind Tyr — the last outpost before the silt.
>
> **LANDMARKS** (small icons + fine labels): **Altaruk**, a tiny fortified trade post at the head of the estuary · **North & South Ledopolus**, twin dwarven villages on opposite estuary banks with an unfinished stone causeway reaching toward a small island (**Ledo Island**) between them · the **Mekillot Mountains**, an isolated small range near the south coast, with the village **Salt View** on its eastern face · the **Dragon's Bowl**, a round cliff-walled crater north of Urik holding a small brilliant blue lake (**Lake Pit**) — the only true blue water on the map · the **ruins of Yaramuke** with a dark stained oasis, halfway between Urik and Raam · **Walis**, a tiny village atop a rock spire in the northwestern foothills · **Ogo**, a step-pyramid just under the forest canopy near Gulg · **Bitter Well**, a lone oasis icon on the western scrub plains.
>
> **MOOD:** sun-bleached, majestic, slightly ominous — a living coastal ring of commerce clinging to the edge of a vast gray nothing. Faint wakes of something enormous moving beneath the silt in one or two places, subtle enough to miss.

## Iteration notes

- If the generator fights the gray silt (defaults to sand), lead with: "The interior is GRAY DUST, the color of ash and bone — not a sand desert."
- If city icons come out generic, run the drill-in prompts below and composite.
- The First Source is **never marked** — [the Veil](../Campaign/Plot-Threads/The-First-Source.md) applies to cartographers too.

## Drill-in template (regional maps)

> A detailed fantasy regional map, painted in the same style as [describe/attach the continent map]: top-down painterly cartography, soft 3D relief, parchment palette, serif labels, compass rose. This map covers **[REGION]** of the desert continent of Aerun — roughly [WHICH ARC of the coastal ring], with the ocean on one side and the gray Sea of Silt behind the Rim Wall cliffs on the other. The Ring Road crosses the whole map through [CITIES]. Show: [CITY-SPECIFIC TERRAIN + LANDMARK LIST from the Glossary geography table]. City icons are large and architecturally distinct: [CITY ICON NOTES]. Mood: [MOOD].

**Planned drill-ins** (one per session of need):

1. **The Northwest** — Tyr, Eldorado, Osgaker: Ringing Mountains, iron terraces, Walis spire, the Rim Wall pass.
2. **The Southwest** — Urik and the Black Crown: the volcano, obsidian quarries, Yaramuke ruins on the Raam road — and the **Dragon's Bowl**: an irregular, *elongated* sunken basin with a ragged thousand-foot rim (emphatically not a neat circle), 35–50 miles long, Lake Pit's blue water in the northern lobe, and one torn-looking breach in the southern rim.
3. **The South** — Balic and the Forked Tongue: the two-seas harbor, Altaruk, the Ledopolus twins and Ledo Island, Mekillot Mountains + Salt View, Amber Valley.
4. **The East** — Nibenay and Gulg: the Crescent Forest between them, rice springs, the hedge-ring, Ogo, Badlands behind.
5. **The North** — Draj, Blackguard, Raam: the mudflats and causeway, the silt arm, the sprawl.
