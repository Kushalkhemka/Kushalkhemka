# Profile artwork

The profile uses self-contained SVGs with separate desktop and mobile layouts. The README's `picture` elements select the mobile artwork below a 600px viewport width.

## Rebuild

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_assets.py
```

Edit the copy, layout, and color constants in `build_assets.py`, rebuild, and commit both the source and updated `assets/` files. Keep README image alternatives and expandable text in sync with artwork changes.

Space Grotesk comes from the [Google Fonts repository](https://github.com/google/fonts/tree/main/ofl/spacegrotesk), under the included SIL Open Font License. It matches the typography of the OpenSec design reference. Text is converted to vector paths so GitHub images do not depend on web fonts or the viewer's installed fonts.

SVG assets have no scripts, external images, font requests, or animation. Links and expandable sections use GitHub's native README rendering. Dark artwork remains dark in both GitHub themes; GitHub controls the surrounding page appearance.
