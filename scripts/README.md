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

## GitHub statistics

```sh
.venv/bin/python scripts/update_github.py
```

The refresh workflow runs daily and can also be started manually in GitHub Actions. It fetches the public profile, public repository metadata, and the public contribution calendar, validates the complete calendar, and generates the summary, calendar, language chart, and project star/fork counts. A fetch failure leaves the published version intact. The dated snapshot is `assets/github-data.json`.

- Stars earned: sum of stars on public, non-fork repositories owned by this account.
- Repositories starred: number of repositories starred by this account.
- Contributions: the total shown by GitHub's public contribution calendar, not a commit count.
- Longest streak: consecutive days with contributions within that calendar's period.
- Languages: repository counts by primary language, excluding forks and repositories without a primary language; not a lines-of-code measure.

All project card image alternatives include their star/fork counts and snapshot date. The workflow uses only the standard repository-scoped Actions token; no personal access token is required. The SVGs remain available if a later refresh fails. GitHub may delay scheduled jobs or disable them after prolonged repository inactivity; the README links to the workflow status.

## Framework logos

The 26 framework and developer-tool logos in `assets/icons/` are sourced from [Skill Icons](https://github.com/tandpfun/skill-icons) using its dark-theme SVG endpoint. They are stored locally so the README can show them without depending on the icon API at viewing time. Its license is included in that directory. Trophy, research, and community icons are custom line SVGs in the profile's lime accent.
