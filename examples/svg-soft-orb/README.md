# Soft Orb SVG Demo

This is a small public-safe SVG route demo. It uses a simple low-color PNG source, converts it with `png2svg.py`, then runs the result inside an idle SVG/HTML pet template.

## Files

- `source.png`: transparent raster source used as the input image.
- `soft-orb.svg`: vtracer output generated from the source PNG.
- `idle.svg.html`: runnable idle animation using the generated SVG plus hand-authored blink eyes.

## Reproduce

From the repository root:

```powershell
py -3.13 routes\svg\tools\png2svg\png2svg.py examples\svg-soft-orb\source.png examples\svg-soft-orb\soft-orb.svg --preset apple-precise
```

This demo run produced 74 SVG paths and a 60 KB SVG file.

## Why This Demo Works

- The source PNG is transparent, low-color, and has clean silhouettes.
- vtracer handles the body vectorization.
- The HTML template keeps eyes and mouth as editable SVG primitives so blinking remains easy to control.

For complex photos, heavy gradients, hair, fur, texture, or noisy edges, this route is expected to degrade. Use the APNG route or redraw key SVG shapes manually.
