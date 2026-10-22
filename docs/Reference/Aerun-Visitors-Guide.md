[Home](../Home.md) / [Reference](../Reference.md) / Aerun Visitors Guide <!-- wikidown:breadcrumb -->

# Aerun Visitor's Guide (plan)

**DM-side page.** The plan and the running instructions for the in-world visitor's guide website, agreed with Mark on 2026-10-21. **Version 1 is built and published:** <https://markdav-is.github.io/dnd-lost-ship/>. The guide's source is the second wiki in `/guide`.

## What it is

- **An in-world artifact.** It's the guide the party gets on their phones when they step off the ship on Aerun, and they discover it in play. It is written to travelers in the world, not to the players: no DCs, rolls, classes, or "player-facing" notes.
- **Published by The Aerun Travel Council,** a fictitious travel agency.
- **Delivered over the Aura network.** Each region's chapter comes from that region's relay tower when the party enters it ([The Aura Network](../World/The-Aura-Network.md)). Nobody has to visit an office, unless they want a printed map.
- **It grows as the party travels.** The party starts at **Balic's southern port**. On day one the guide holds the continent map, the full House Wavir chapter, the Guild's chapter, and a teaser for every other region. When the party reaches a region, its full chapter unlocks.
- **The silt is dead air.** The network fails beyond the Rim Wall, so the Sea of Silt page is permanently "no signal". The Long Reach and waystation pages are in the Guild's chapter, written as "read this before you board".

## What's in version 1

| Page (in `/guide`) | State |
| :--- | :--- |
| `index.html` | Landing screen: "Signal received · House Wavir relay · Balic", with buttons into the guide |
| `/Home` | Welcome, the clickable continent map with "you are here" at Balic, chapters by road distance from Balic, the full-size atlas download, how the guide works |
| `/House-Wavir` + 7 pages | **Full chapter:** Arriving in Balic (the gate ritual, heat, coin, who runs Aerun, things you'll notice), Balic, the Balic Saddle, Altaruk, the Mekillot Mountains, Salt View, Amber Valley |
| `/The-Caravan-Guild` + 4 pages | **Full chapter:** the Ring Road, Distances and Days (the mileage board), the Long Reach, the waystations |
| `/House-Inika`, `/House-Stel`, `/House-Shom`, `/House-Mke`, `/House-Tsalaxa`, `/House-Vordon` | **Teasers:** zoomed map, "Chapter not yet received" notice, banner, what's known from Balic, the places in the region, and how far it is |
| `/The-Sea-of-Silt` | "No signal" page: what can be seen and said from the coast |

All text comes from the player [Gazetteer](../Aerun-Players-Guide/Gazetteer.md) and the Primer and Gate Ritual pages, rewritten into the Council's voice. The banners (heraldry) come from [The Merchant Houses](../World/Factions/The-Merchant-Houses.md). Nothing else from the DM side is used, and Tyr's Ziggurat is never explained.

Chapters are listed **by road distance from Balic** (Wavir, then Inika and Stel, Shom, M'ke, Tsalaxa, Vordon), so the guide doesn't have to decide east or west.

## How to unlock a region

When the party enters a family's region:

1. **Write the full chapter.** Replace the teaser text on `/House-X` (keep its `<svg>` map) with the region page, and add place pages under it with `wikidown new --root guide --path /House-X/Place`. House Wavir is the model.
2. **Lift the lock.** In `guide/assets/wikidown.css`, find the **CHAPTER LOCKS** block and delete the house (e.g. `.r-inika`) from **both** selector lists. Every map in the guide stops greying it out.
3. **Point the map pins at the new pages.** While locked, every pin in that region links to `House-X.md`. The map is copied into 10 pages (Home, the 7 house pages, the Guild, the silt), all at the wiki root, so one find-and-replace per pin across `guide/*.md` does it. For example: `<a href="House-Inika.md" class="pin city r-inika"><title>Gulg</title>` becomes `<a href="House-Inika/Gulg.md" class="pin city r-inika"><title>Gulg</title>`.
4. **Move the signal.** In `guide/_layouts/wikidown.html` and `guide/index.html`, change "Wavir relay · Balic" to the new relay. On `/Home`, update "You are here", the green "here" ring's coordinates in the maps (it is the `<g class="here">` group), and the chapter table's **Guide** column.
5. **Add the city map, if approved.** Make a phone-sized JPEG into `guide/.attachments/` (about 1600 px wide), copy the full-size PNG in too, and add a download button like the atlas one on Home.
6. **Check and push.** Run `wikidown check-links --root guide`, then push. The Action republishes in about a minute.

## How it's built

- **Maps:** inline SVG in the markdown. The atlas (`.attachments/aerun-atlas.jpg`) is an `<image>`, the regions are tinted `<a>` shapes, the Ring Road is solid gold and the Long Reach dashed gold, and the silt is hatched. All the styling lives in `guide/assets/wikidown.css`, including the region colors and the chapter locks, so the SVGs themselves only carry classes. Region pages use the same SVG with a cropped `viewBox` and a `focus-<house>` class.
- **Links in the SVG are ordinary relative `.md` links.** Wikidown 0.12 rewrites them to `.html`, `check-links` validates them, and `move` updates them.
- **Theme:** started from `wikidown pages` and customized: `assets/wikidown.css` (sand, sea and Guild gold, light and dark), `_layouts/wikidown.html` (Travel Council top bar, the relay "signal" pill, an in-world footer, no GitHub link), and a standalone `index.html` landing screen. Never run `wikidown pages --root guide --force`; it would overwrite all three.
- **Images:** phone-sized JPEGs on the pages, plus full-size downloads. They were resized once with .NET's System.Drawing from PowerShell, with no extra tools.
- **Publishing:** `.github/workflows/visitors-guide.yml` runs on every push to `guide/**` on `main`, or by hand from the Actions tab. It installs Wikidown.Cli 0.12.0, runs `check-links` (a broken link fails the build), runs `export-html --root guide --base-url /dnd-lost-ship`, adds `.nojekyll`, and deploys to GitHub Pages. Pages is set to deploy from GitHub Actions.

## Known gaps

- **No guide PDF yet.** `wikidown export-pdf` can't draw inline SVG; it prints "[unsupported HTML block omitted]" in place of every map, and it doesn't size large images to the page. The site offers the full-size atlas image instead. Worth a Wikidown feature request: render an `<svg>`'s `<image>` (or a `{.print-only}` image) in PDFs, and fit images to the page width.
- **The Balic and Urik city maps** aren't approved yet ([Aerun City Map Roster](Aerun-City-Map-Roster.md)), so Balic's page uses the dusk painting instead of a city map.
- **The region borders are a first draft** ("a fine start"). Changing one means editing the same `<path>` in all 10 map copies.
- **The repo is public,** so a curious player could read the teaser pages' source, or the DM wiki, on GitHub. The site itself only shows what's been unlocked.

## Open questions

1. Is "Council" the right spelling for the publisher?
2. A custom domain later, so the address doesn't say "dnd-lost-ship"?

## Related

- [Aerun City Map Roster](Aerun-City-Map-Roster.md): which city maps are approved.
- [Aerun Players Guide](../Aerun-Players-Guide.md): the player-facing source pages, with lore-check tables, which the guide does not use.
- The older player campaign site on Manus is linked from [Reference](../Reference.md).
