# Street Fade Fix (Transport Fever 2)

Streets whiten -- or, under Vulkan on AMD, turn into multicoloured speckles --
when the camera is far from the map centre. It is most visible with the line
manager's grey layer (CommonAPI calls it the "white layer"), and it happens on
vanilla Megalomaniac maps as well as on larger ones.

| Renderer | Symptom (camera far from the centre, grey layer on) |
| --- | --- |
| OpenGL | streets whiten progressively from ~10 km of camera distance |
| Vulkan | streets whiten too; on AMD, past ~23 km they become coloured speckles |

## Cause

Five material vertex shaders fade an object out by the camera's distance to the
object's bounding box:

```glsl
float distToCam = calcDistToBox(u_view.viewInverse[3].xyz, instAttrBbox);
float alpha = compFadeOutAlpha(distToCam, u_vmat.fadeOutRanges[0] * ...);
```

When the renderer supplies no box, `instAttrBbox` falls back to
`defaultInstaAttrBBox = { vec3(0), vec3(0) }` -- a single point at the **map
centre**. The distance is then the camera's distance to the centre, not to the
object. Street materials fade out between 10 and 20 km (`fade_out_range`), so in
that pipeline every street fades by where the camera is. OpenGL blends the
half-transparent street over the white ground; Vulkan on AMD renders the
transparency with alpha-to-coverage, whose dither shows up as speckles.

Measured on a 57 km map: the speckle boundary is a circle of ~23,000 m around
the centre, and it moves with the zoom, because the camera *eye* is what is
measured.

## Fix

When both corners of the box are zero (no box), the distance is measured to the
vertex itself (`std` shaders) or to the leafcard centre (`leafcard` shaders).
Objects that do supply a box behave exactly as before.

Replaced files, all in `res/shaders2/mat/vs/`:
`std/normal.vs`, `std/color.vs`, `std/color_diffuse.vs`,
`leafcard/normal.vs`, `leafcard/color.vs`.

Purely visual and client-side: no save data, safe to add or remove at any time,
nothing needed on other multiplayer peers.

## Install

Copy `street_fade_fix_1` into `%APPDATA%\Transport Fever 2\mods\` (or subscribe
on mod.io once published) and enable it for the game.

## Languages

The description in the mod list is translated into all 13 vanilla languages
(English, French, German, Spanish, Italian, Dutch, Polish, Russian, Brazilian
Portuguese, Japanese, Korean, Simplified and Traditional Chinese) + Czech,
Ukrainian and Turkish. The name stays "Street Fade Fix" in every language. Apart
from English and French, the translations were machine-written and have not been
reviewed by native speakers: corrections are welcome. `python tools/check_strings.py`
checks that the files load, that every language has its description, and that no code
is mistyped.

## Rebuilding the shaders

The shipped shaders are the game's own files with one statement changed. To
regenerate them from an installation:

```
python tools/build_mod.py --game "<Transport Fever 2 folder>"
```

The script requires each anchor to match exactly once and writes nothing
otherwise. The shipped copies were generated from the GOG build (2024-12-12),
the same game version as Steam build 35924.

## Licence

[MIT](LICENSE) for `tools/build_mod.py`, `tools/check_strings.py`, `mod.lua`,
`strings.lua` and this README. **The licence does not cover the shader files** in
`street_fade_fix_1/res/shaders2`: they are Urban Games' shaders, each with one
statement changed, redistributed modified as is customary for Transport Fever 2
shader mods; all rights to the original code remain theirs.
