# Beats: what the csar talk has to hit

A working document. The deck (`slides/talk.qmd`) is built around these beats;
when a pass changes a slide, it should be serving one of them. Beats are
tiered: **must** (the talk fails without it), **should** (the talk is clearly
weaker without it), **could** (cut first). Minutes are rough and add up to the
~21 minutes of talking the 25-minute slot allows.

Format per beat: the *takeaway* is the one sentence the audience should be able
to say afterward. *On screen* is what carries it. *Notes* are open questions
and risks.

## The spine

One sentence the whole talk serves:

> Shape is a design axis of a DGGS, just like area, and now there is a clean
> definition and a fast tool for measuring it.

Everything else is either setup for that sentence or evidence for it.

## Beat table

Rows are in narrative order, not priority order. Decided 2026-11-02: the
talk is image-led and opens cold on the pictures, with the question as the
title and no agenda slide (decided later the same day). The setup
beat moves to the front of the survey, where "area is what everyone
measures" is the lead-in to the shape-vs-area comparison.

| # | beat | tier | min | status in the draft |
|---|------|------|-----|---------------------|
| 1 | Cells are squished and you can see it | must | 1 | the three city plots, question as title; no agenda slide |
| 6 | Why shape matters | should | 1 | three lines + neighbors cartoon + Kimerling citation; then a how-to-measure slide |
| 11 | Why a new metric: what IPQ can't see | must | 1.5 | four live on-sphere slides: square stretched, square vs hexagon, hexagon stretched, star |
| 2 | The definition: TEEC, then AR | must | 4 | math slide + demo; needs the plain-words version |
| 9 | Lineage: this is MVEE lifted to the sphere | could | 1 | not in draft |
| 10 | It is convex: exact, certified | could | 1.5 | drafted (2 slides) |
| 4 | Where to get it | must | 1 | software slide |
| 8 | Setup: many DGGSs, area is the axis everyone measures | could | 0 | commented out 2026-11-02; the H3 globe note carries the one spoken line |
| 3 | AR over the globe, per system | must | 3.5 | six full-bleed ajglobe slides (H3, S2, ISEA7H, IVEA7H, A5, rHEALPix), AR/area toggle, hover readout, click-to-solve ellipse |
| 7 | How systems compare | should | 2.5 | after the globes: the six-row table, then the tradeoff scatter (which is also the close) |
| 12 | Open questions (sphere vs ellipsoid, extreme cells, resolution matching, sampling, direction), pointing at dggs_compare | should | 1 | one slide, replaces the ellipsoid slide |
| 5 | The close: many design axes, this is one | must | 0 | spoken over the tradeoff scatter; no text slide (cut 2026-11-02) |
| | about me, thanks | | 1 | |
| | **total** | | **~23** | |

Must beats alone are about 13.5 minutes. That is the floor the talk can shrink
to under a hard cut. The total is a minute or two over; the cut order below
is where it comes from.

## The beats

### 1. Cells are squished and you can see it (must)

**Takeaway:** same system, same resolution, different place on the globe,
visibly different shape.

**On screen:** the talk opens on this, no title, no words. Real grid cells
over a city basemap, so the squish reads in a context the eye knows: H3 in Sydney (its roundest), H3 in
Seoul (AR ~1.21, hexagons visibly wider than tall), S2 in Osaka (next to
a cube corner, AR ~1.7, squares sheared into parallelograms). Cities were
picked by computing AR at ~70 major cities and taking the extremes
(`figs/city_grids.jpg`, `scripts/make_city_grids.py`; OSM tiles, Web
Mercator). A wider stereographic view over coastlines also exists
(`figs/grid_maps.png`) but reads worse without landmarks. Then straight to "why
shape matters". (Bare single-cell slides and an agenda slide were tried
between the grids and the body, and retired: the title asks the question.)
The example cells come after the live demo with the ellipse on, as the
callback that closes the loop (the "same cells, measured" section).

**Notes:** this is the hook and it is already built. Resist adding more
systems here; two is enough to establish "this is a thing."

**"Isn't that just the map projection?"** must be pre-empted, because the
audience knows projections distort shapes and will assume that is what
they are seeing. Two layers: (1) the grid pictures are Web Mercator
(the city figure) or stereographic (the coastline one), both conformal,
so the shapes on screen are exact; an orthographic view would have
squashed the rim by ~4.5% at that patch size, the same order as H3's own
squish, which is why it is not used;
(2) the metric itself never projects: it takes the corner points on the
sphere and finds a cone, so there is no projection to blame. Say (1) as
one line on the grid slide; (2) belongs to the definition beat and is
part of why the cone formulation is the right one.

### 2. The definition (must, the centerpiece)

**Takeaway:** csar AR is the elongation of the tightest elliptical cone, tip
at the center of the sphere, that contains the cell's corners. One is round;
bigger is more squished.

**On screen:** a picture first, the live demo (drag a corner, the cone and
its rim follow, the number changes), and only then the optimization problem,
flagged as "for those who want it."

**Notes:** the AR definition depends on the TEEC definition being
unambiguous, so the plain-words version has to carry both. Candidate
phrasings, to pick one and repeat it verbatim:

- "Put the tip of a cone at the center of the earth. Open it up just enough
  to swallow all the corners of the cell. The cone is allowed to be
  elliptical. The aspect ratio is how elliptical it had to be."
- "The smallest elliptical cone, apex at the center, that contains the
  points. AR is the ratio of the long axis to the short axis of its cross
  section."
- "An ellipse on the sphere, drawn as tightly as possible around the cell's
  corners. AR is its elongation." (Simplest. Hides the cone, which is the
  thing that makes it well defined. Maybe the first sentence, with the cone
  as the second.)
- "AR is the stretch you would have to undo to make the cell round." (The
  operational one; it is what the IPQ slide demonstrates, so saying it
  there and repeating it here costs nothing. Exact when the stretch is
  along the cell's long axis, which is the only case the slide shows.)

Things the definition must make clear, because they are what distinguish it
from the obvious alternatives: it uses only the corner points, it needs no
map projection and no choice of center, the answer is unique, and it is
dimensionless. The demo shows most of this without words.

Open: how much of the "it is the MVEE problem" lineage belongs here (see 9).
This beat should open by answering beat 11's setup: "so we want a number that
is only about elongation; here is one."

### 3. AR over the globe, per system (must)

**Takeaway:** squish is not noise, it is a smooth field with a pattern that
is the projection's fingerprint. Icosahedron edges for H3, cube corners for
S2, a six-pointed star per face for ISEA7H.

**On screen:** the AR-colored globes, one per slide, spinnable, drawn from
the dggs_compare data release's own globe binaries with the ajglobe bundle
vendored (`scripts/make_globes.py` fetches them; `slides/web/globeslide.js`). The globe fills
the slide with a lean side panel: title, AR/area toggle, the globe's
distribution of the shown metric as a histogram over a horizontal colour
bar with a plain numeric axis (hovered cell marked), and a fixed two-row
AR / area readout. No counts, no ranges, no hint text; nothing moves on
hover.
One shared AR scale, capped at 1.75 so A5 saturates: light = round, dark =
stretched, through the deck's teal and purple; area is a WARM diverging
scale (brown small, cream at the mean, orange-red large) so the two views
cannot be confused. Hover reads both numbers; click runs csar in the
browser and draws the cell's ellipse. Keys steer a focused globe. All the
globe slides share one view (orientation and zoom) and one metric, so
flipping between systems compares like with like.

**Notes:** this is the most visually memorable part of the talk and is
mostly a "look at this" beat. Which systems get screen time is the main
choice; H3 is required (proposal), S2 and one equal-area system make the
contrast. The embed-mode issue on the dggs_compare page decides whether the
globes are above the fold.

### 4. Where to get it (must)

**Takeaway:** `pip install csar`; it is fast enough to measure every cell in
your system; also runs in the browser.

**On screen:** one slide with the install line, the three repos, and one
sentence on speed. Pointing back at the demo ("that was the real solver")
does the credibility work for free.

### 5. The close (must)

**Takeaway:** a DGGS makes many design choices. Area is the one everyone
measures. Shape is another. This was a tool for seeing one more of them.

**On screen:** the tradeoff scatter, if beat 7 keeps it, is the perfect
backdrop: nobody is at the ideal corner, everyone picked a point.

**Notes:** tone matters. People in the room are proud of their equal-area
systems and that pride is deserved. The line is "area is one goal," never
"area is overrated." The tradeoff plot makes the point without a sentence
having to: equal-area systems pay in shape, shape-friendly systems pay in
area, and that is a choice, not a failing. Let the picture be the critic.

### 6. Why shape matters (should)

**Takeaway:** anything that treats neighbors as equidistant is off by about
the aspect ratio: kernels, stencils, k-rings, neighbor distances.

**On screen:** one picture would help more than the bullets, e.g. a k-ring on
a round cell next to one on a squished cell. Bullets are acceptable.

**Notes:** this earns the audience's attention for the definition. Keep it
to one slide; the people who need convincing are convinced by the first
example.

**Precedent (read 2026-11-02).** The field never argued shape at length.
Kimerling, Sahr, White & Song (1999) inherit compactness as Goodchild
criterion 5 and give it one paragraph: "a single vector of values will be
associated with all the points in a single areal cell", so the points
should be "as close to each other as possible" (Tobler's first law). That
rationale is about *distance within a cell*, which a stretched cell
violates along its long axis: it is a better argument for AR than for
IPQ. Their criterion 11 maps (centerpoint spacing by direction, the
"propeller" pattern following Tissot angular deformation) are
direction-dependent squish measured in 1999. Their Table 1 already shows
the area/shape trade: ISEA scores 10 on equal area and 7 on compactness,
gnomonic 3 and 9; "if cell compactness is of prime importance... a
Gnomonic map projection... would be the best alternative." Kmoch et al.
(2022, 2025) argue area at length (±50% in H3 "can skew multi-criteria
evaluations") and take shape as a given virtue of hexagons ("approach
circular geometry more closely... uniform adjacency"); per-cell shape is
measured and reported, not motivated. So: one line is the field's own
level of argument for shape; the talk's contribution is the number, not
the case that shape matters. Kimerling's line can be borrowed outright.

### 7. How systems compare (should)

**Takeaway:** every system sits somewhere on a shape-versus-area plane, and
none sits at the ideal.

**On screen:** the tradeoff scatter is the one picture. Histograms show the
within-system spread (H3 tight, S2 wide, A5 never round). A table gives the
numbers for people who want to write one down.

**Notes:** the draft has all three; under time pressure the scatter stays and
the others go, in the order table, then histograms. Decide whether four
systems (what the figures show) or six (what the proposal lists) is the
story; six probably only matters on the table.

### 8. Setup: many DGGSs, area is the axis everyone measures (should)

**Takeaway:** we have lots of systems and need ways to compare them; area is
the established one.

**Notes:** this is framing and can compress to one slide, or into the first
sentence of beat 1. Its real job is to make beat 5 land as a bookend.

### 9. Lineage: this is MVEE lifted to the sphere (could)

**Takeaway:** if you know the minimum-volume enclosing ellipsoid, this is
that, with the ellipsoid replaced by a cone through the center. If you
don't, nothing is lost.

**On screen:** a two-panel picture: points in the plane with their MVEE;
points on the sphere with their TEEC. Same idea, one dimension up and
through the origin.

**Notes:** the cost is time and the risk is a detour. The benefit is that
people who know MVEE get the whole definition in one glance, and it
positions the work as established math applied, not invented math. One
slide, no derivation, placed right after the plain-words definition. If the
talk runs long this goes first.

### 10. It is convex: exact and certified (could)

**Takeaway:** there are no local optima to get stuck in, and the solver hands
back a proof of optimality with every answer, so "certified" means checked.

**Notes:** one slide. The declarative-programming / agents observation is one
spoken sentence at most; it is interesting to us and a tangent for them.

### 11. Why a new metric: what IPQ can't see (must, but ~1 minute)

**Takeaway:** stretch any cell 50% and AR reads 1.5. IPQ reads a number
that depends on what you started with, because it is answering a different
question: how efficiently the boundary encloses area. Both useful; this
talk is about the stretch one.

**Why it is a must:** "we have IPQ, why another metric?" is the question in
the room before anyone will listen to a definition. Answer it first and the
definition becomes the obvious next move.

**The slide (one, ~60-75 s):** a grid of shapes, rows = square then hexagon
(triangle optional), columns = original and stretched 1.5x along one axis,
the enclosing ellipse drawn on each, two numbers under each. The square row
goes first because a 1.5x-stretched square is a 3:2 rectangle, and everyone
already calls that "aspect ratio 1.5": the metric agrees with the word the
audience already uses. The hexagon row second, because that is what DGGS
cells are and it shows the agreement is not a rectangle coincidence.
Live on the sphere (`slides/data/shapes.js`, from `scripts/make_stretch.py`).

| shape | IPQ before → after | AR before → after |
|---|---|---|
| hexagon | 0.907 → 0.852 | 1.00 → 1.50 |
| square | 0.785 → 0.754 | 1.00 → 1.50 |
| triangle | 0.605 → 0.568 | 1.00 → 1.50 |
| ellipse | 1.000 → 0.941 | 1.00 → 1.50 |

(Planar numbers at small scale, for the record; the slides show the SPHERICAL
IPQ of shapes ~40° across, which differs in the second decimal: see
`slides/data/shapes.js` for the numbers on screen. The AR column is the same
for every row at every size, which is the point.)

The message line on the slide (it answers the talk's title):

> **When you say a cell is squished, this is the number you mean.**

with two support lines:

> Compactness (IPQ) measures how efficiently the boundary encloses area.
> Aspect ratio measures stretch, and reads the stretch you applied, for any shape.

Spoken, verbatim (settled 2026-11-02): "IPQ is a good measure of what it
measures. Within one DGGS every cell is about equally smooth, so stretch is
what varies, and that's what this isolates." This names the quantity
instead of ranking metrics, so nobody's favorite number is being graded.

**Why this is not circular:** the metric is calibrated on ellipses by
construction (an ellipse's AR is its own axis ratio), and that is a feature.
The non-trivial claim is that the calibration carries over to every other
shape, and the hexagon and square rows demonstrate it without an ellipse
ever being the input. The ellipse is the output. (Paper: under a linear
stretch along the enclosing ellipse's axis, AR scales by exactly the
stretch; IPQ's response depends on the boundary-direction distribution.)
This is also the strongest argument that the definition is *natural*, so
the slide does double duty: motivation and a preview of the definition.

**Appendix slide, after Thanks, for Q&A:** the response-curve figure
(`figs/ipq_vs_ar.png`) with the polygon-class lines, and the facts behind
it: IPQ moves under 3% across the AR band where hexagonal DGGS cells live,
polygon class moves it far more, so cross-system IPQ comparisons mostly
compare hexagons to squares. Keep "the published conclusion is partly a
metric artifact" for the answer to a direct question, not the slide.

**Tone:** "a different question," never "IPQ is wrong." IPQ sees boundary
roughness, which AR ignores. Companions.

**"Stretched how, on the sphere or in the plane?"** (a likely question).
The stretch is in the gnomonic chart: central projection from the sphere's
center onto the tangent plane at the cell's axis, stretch there, project
back along the rays. That is the natural stretch for a cone, because it is
a linear map of 3-space (fix the axis, scale one tangent direction) and
linear maps send rays to rays, cones to cones, and the tightest enclosing
cone to the tightest enclosing cone of the stretched points. So AR scales
by exactly the factor at *any* cell size; checked numerically at angular
radii from 0.05° to 50°, AR = 1.500000000 every time. At DGGS cell sizes
(~1e-3 rad for the figure, smaller for real cells) the sphere is flat to
~1e-6 and every planar notion of stretch agrees, so IPQ computed in the
plane is fine too. Spoken answer: "in the tangent plane; at cell scale the
sphere is flat. If you want it exact, it is a stretch of the gnomonic
coordinates, which is the one stretch that maps cones to cones, and the
result holds at any size."

### 12. Open questions (should; was "Sphere vs ellipsoid")

**Takeaway:** this is work in progress; here is what is unsettled, and
here is where every number lives. Five questions, one line each: which
sphere is the fair arena; how to report extreme cells (pentagons, cube
corners, polar caps); how to match resolutions across systems; enumerate
or sample; the direction of stretch, not just its size. Ends on the
dggs_compare URL. The sphere-vs-ellipsoid material below is now the
first bullet's speaker note.

#### The old beat: sphere vs ellipsoid

**Takeaway:** the metric is defined on the sphere; real grids live on WGS84;
no map is both equal-area and conformal, so area and shape use different
auxiliary spheres; the shape difference is tiny; it is a modeling choice.

**Notes:** one slide, stated as an open question. Also the natural place to
say how the survey handled it (authalic for area, and what for shape). Easy
cut; the proposal only promised a "discussion."

## Cut order, if it runs long

1. MVEE lineage (9), unless it has replaced part of the definition.
2. Convex / certified (10) down to one spoken sentence on the software slide.
3. Ellipsoid (12) down to one sentence in the close.
4. Table, then histograms, from beat 7.
5. The S2 round cell from beat 1.
6. Setup (8) folded into the first sentence of beat 1.

Not on the list: the IPQ beat (11). Under a hard cut it compresses to the
response-curve slide alone, but it does not go.

## Open questions

- Which plain-words definition (beat 2) do we commit to and repeat?
- Does the MVEE picture make the definition faster to grasp, or slower?
  Worth building the two-panel figure and deciding by looking at it.
- Is the "why shape matters" beat better as a picture or as bullets?
- Beat 11's figure: two rows (square, hexagon) or three (plus triangle)?
  Two is cleaner; three hammers "any shape." Or the square row alone on
  the slide, with the hexagon spoken ("same for a hexagon, same for a
  triangle").

## Terms, and where a careful reader could catch us

- **Shape**: the umbrella (Goodchild criterion 4 "same shape"; Kmoch "shape
  distortion"). AR measures one component, elongation. Never "AR measures
  shape".
- **Compactness**: a specific area-to-perimeter family, criterion 5. Not a
  synonym for round. Kimerling's instrument is ZSC, Kmoch's a normalized
  compactness from area and perimeter.
- **IPQ**: planar 4πA/P² (= Polsby-Popper). Spherical: A(4π−A)/P². Kimerling's
  ZSC is the SQUARE ROOT of the spherical one: hexagon IPQ 0.907 but ZSC 0.952.
  The stretch slide must say "IPQ (4πA/P²)"; notes carry the ZSC conversion.
- **Aspect ratio**: ours is the axis ratio of the tightest enclosing ellipse on
  the sphere (via the cone). Other definitions exist (bounding box, PCA,
  inscribed/circumscribed circle in mesh quality). State ours once.
- **Stretched / squished**: plain words. Squished suggests size; AR is
  scale-free. Say once, early, that the number ignores size (the city plots
  show area variation too).
- **"Reads the stretch you applied, for any shape"**: exact only when the
  stretch is along the enclosing ellipse's axis; for the regular shapes on
  the slide every direction is an axis. Don't universalize in speech.
- **Their reason, our number**: Kimerling's paragraph motivates compactness;
  we borrow it for AR. "Criterion 5" and "see" keep it honest.
- **Reock / minimum bounding ellipse** (redistricting): area over enclosing
  circle (or ellipse) area; the nearest cousin. Mixes elongation with
  roughness again, and is planar. Have the one-line answer ready.
- **Tissot**: defined for a projection, not a cell. "Per-cell analogue of
  Tissot's a/b", never "the cell's indicatrix".
- **Agree with Kmoch**: our survey's H3-best-on-shape matches their headline.
  Say so; sharper measurement of an agreed result beats a correction.
