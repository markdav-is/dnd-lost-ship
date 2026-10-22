[Home](../Home.md) / [Reference](../Reference.md) / Aerun Visitors Guide <!-- wikidown:breadcrumb -->

# Aerun Visitor's Guide (plan)

**DM-side planning page.** This page is the plan for the in-world visitor's guide website, agreed with Mark on 2026-10-21. Nothing is built yet. Update this page as each decision lands.

## What it is

- **An in-world artifact.** It's the guide the party gets on their phones when they step off the ship on Aerun, and they discover it in play. It is written to travelers in the world, not to the players: no DCs, rolls, classes, or "player-facing" notes.
- **Published by The Aerun Travel Council,** a fictitious travel agency.
- **Delivered over the Aura network.** Each region's chapter comes from that region's relay tower when the party enters it ([The Aura Network](../World/The-Aura-Network.md)). Nobody has to visit an office, unless they want a printed map.
- **It grows as the party travels.** The party starts at **Balic's southern port**. On day one the guide holds the continent map, the full Balic chapter, and a short teaser for every other region ending in "visit X for more". When the party reaches a region, its full chapter unlocks.
- **The silt is dead air.** The network fails beyond the Rim Wall, so the Sea of Silt and the Long Reach can only ever be teasers.

## Structure

Organized by **region, one per merchant family**, starting at Balic. It is not organized by topic.

| Region | City | Also in the region |
| :--- | :--- | :--- |
| House Wavir | Balic | Altaruk (held jointly, Wavir chief), Amber Valley (neutral), Salt View, the Mekillot Mountains |
| House Inika | Gulg | Ogo, the Crescent Forest |
| House Shom | Nibenay | the Rust-Red Badlands |
| House M'ke | Raam | Blackguard |
| House Tsalaxa | Draj | the north coast |
| House Vordon | Tyr | Eldorado, Walis, Osgaker (independent), the Ringing Mountains, Bitter Well |
| House Stel | Urik | Hollowstorm (independent), the Black Crown, the Dragon's Bowl, Lake Pit, Yaramuke and the Black Oasis |
| The Caravan Guild | none | the Ring Road, the Long Reach, the waystations, the Balic Saddle |
| Nobody | none | the Sea of Silt, the Rim Wall |

The borders and colors come from the prototype map, which Mark called "a fine start". The order after Balic (east toward Gulg or west toward Urik) is open.

Source text is the [Gazetteer](../Aerun-Players-Guide/Gazetteer.md), rewritten into the guide's voice. Never use DM-side material, and never say what Tyr's Ziggurat holds.

## Maps

- **Clickable inline SVG in the markdown.** The atlas is an `<image>`. Each family region is a tinted `<a>` shape in its banner-based color. The Ring Road is a solid gold line and the Long Reach a dashed one (both Guild). The silt is hatched gray. Places get pins, and places not held by a single family get a dashed pin.
- **Region pages reuse the same SVG with a cropped `viewBox`.** Places outside the region still show, dimmed, and still link.
- **Locked regions are greyed out** on the continent map. Unlocking a region changes one CSS class.
- **No JavaScript, no map libraries, no custom build scripts.**
- **Links in the SVG are ordinary relative `.md` links.** Wikidown 0.12 rewrites and checks them (see below).

## Images and downloads

- **On the page:** a phone-sized JPEG of each map, around 1600 px wide and a few hundred KB. Shrink once when a map is added, and commit the result.
- **Downloads:** the full-size original of each map, plus the whole guide as a PDF from `wikidown export-pdf`. Downloads unlock with their region.

## Where it lives and how it publishes

- **A second wiki folder in this repo,** separate from `/docs`, and rendered with `--root`.
- **A GitHub Action** builds and deploys it, copying the Wikidown repo's own `pages.yml`. It runs `wikidown export-html --root <folder> --output site --base-url /dnd-lost-ship --clean`, runs `export-pdf` for the guide PDF, adds `.nojekyll`, then uploads and deploys the Pages artifact. Pin the Wikidown.Cli version.
- **No Jekyll.** `export-html` is Wikidown's own renderer.
- **Unlocking is publishing.** Swap a region's teaser for its full chapter and push, and the Action redeploys.

## Wikidown support (0.12.0 and later)

Tested on Wikidown.Cli 0.12.0 on 2026-10-21. Inline SVG maps are fully supported, so **write ordinary relative `.md` links in the SVG**, the same as in markdown:

- `export-html` rewrites `.md` to `.html` in SVG and HTML `<a href>`, including `xlink:href`. It keeps `#fragments` and leaves external URLs alone.
- `check-links` reports broken `.md` links and missing `<image href>` files inside an SVG.
- `move` rewrites SVG links when a page is renamed.
- A blank line inside an `<svg>` no longer breaks it. The no-blank-lines rule is now just tidiness.

Pin the GitHub Action to Wikidown.Cli 0.12.0 or later.

## Open questions

1. Folder name and site address. The default is `markdav-is.github.io/dnd-lost-ship/`, or a custom domain later.
2. After Balic, which way round: east toward Gulg or west toward Urik?
3. Printable PDFs per map, or are the full-size images enough?
4. What a full region chapter holds, starting with Balic.
5. The wording of the "visit X for more" teasers.
6. The publisher's name is spelled "Council" here; confirm.

## Next steps

1. ~~Update Wikidown to 0.12 and rerun the SVG test.~~ Done 2026-10-21; all fixes confirmed.
2. Settle open questions 1, 2 and 4.
3. Create the guide folder: Home with the continent map and contents, the full Balic chapter, and teaser pages for the other regions.
4. Make the phone-sized images.
5. Add the GitHub Action and switch Pages to "GitHub Actions" (Mark's go-ahead needed).
6. At each session, unlock the regions the party reached.

## Related

- [Aerun City Map Roster](Aerun-City-Map-Roster.md): which city maps are approved (Balic and Urik are not yet).
- [Aerun Players Guide](../Aerun-Players-Guide.md): the player-facing source pages, with lore-check tables, which the guide does not use.
- The existing player campaign site on Manus is linked from [Reference](../Reference.md).
