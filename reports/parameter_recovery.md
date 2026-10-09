# Parameter recovery note (STORY-201)

Directional check only — Meridian ROI / Hill parameterization ≠ Path-C
`media_beta` × geometric adstock × Hill saturation. Compare ranks, not
point estimates.

## Estimated iROAS (posterior mean, units per $)

- `meta`: 1.0308
- `tiktok`: 0.9218
- `tv`: 0.7867
- `google`: 0.6040

## Path-C planted signals

Channel contribution means (units):
- `tv`: 1975.00
- `google`: 1384.63
- `meta`: 1048.19
- `tiktok`: 699.63

media_beta (DGP scale):
- `tv`: 2600.0
- `google`: 2200.0
- `meta`: 1800.0
- `tiktok`: 1400.0

adstock_decay (higher = longer memory):
- `tv`: 0.7
- `google`: 0.45
- `meta`: 0.35
- `tiktok`: 0.25

## Rank comparison

- Meridian iROAS rank: ['meta', 'tiktok', 'tv', 'google']
- Path-C contribution rank: ['tv', 'google', 'meta', 'tiktok']
- Spearman rank correlation (iROAS vs contribution): -0.600
- Verdict: **directional mismatch** — investigate media scaling / priors.
