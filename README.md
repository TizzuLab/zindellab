# Zindel Lab — zindellab.ch

Source code for the lab website. Built with [Quarto](https://quarto.org), deployed to <https://zindellab.ch>.

## For lab members: how to update your card

Each member has a partial file in `_people/`. To update yours, no Git CLI is needed — everything works in the browser via github.com.

### 1. Edit your card

Open your file in [`_people/`](https://github.com/TizzuLab/zindellab/tree/main/_people) and click the **pencil icon** top-right. Change the role, room, email, phone, or bio. Scroll to the bottom → **Commit changes** → leave the default options, commit directly to `main`.

The site rebuilds within ~1–2 minutes. You can watch progress at [github.com/TizzuLab/zindellab/actions](https://github.com/TizzuLab/zindellab/actions).

### 2. Add or replace your photo

1. Prepare a **square JPG**, about 600×600 px, ideally under 100 KB. The free in-browser tool [squoosh.app](https://squoosh.app) does this in a few clicks (drop your photo, set Resize to 600 px, save).
2. Upload to [`assets/people/`](https://github.com/TizzuLab/zindellab/tree/main/assets/people) → **Add file → Upload files** → drag in → commit.
3. **Filename must match your card slug** — e.g. `firstname-lastname.jpg`.
4. In your card file, find the image line:
   ```html
   <!-- ![](assets/people/firstname-lastname.jpg){.person-photo} -->
   ```
   Remove the `<!-- ` at the start and ` -->` at the end so it becomes:
   ```html
   ![](assets/people/firstname-lastname.jpg){.person-photo}
   ```
   Commit. Done.

### 3. Optional — add a LinkedIn (or other) profile link

In your card's contact block (between the `::: {.contact}` and `:::` lines), add a new paragraph:

```html
<a href="https://www.linkedin.com/in/YOUR-HANDLE/" target="_blank"><i class="bi bi-linkedin"></i> LinkedIn</a>
```

Replace `YOUR-HANDLE` with your own. The icon shows automatically because Bootstrap Icons are loaded site-wide.

For other profiles (ORCID, Google Scholar, X, GitHub, Bluesky) use the matching `bi-...` class — list at [icons.getbootstrap.com](https://icons.getbootstrap.com), search for the brand name.

### 4. Optional — advertise a semester project

If you have an open topic you would like a semester student to work on, mention it in your bio. A sentence or two is enough. Example structure:

> *I work on [research topic]. **Open for semester projects:** a project on [specific subtopic] — drop me an email if interested.*

Prospective students are pointed from the [Job Opportunities](https://zindellab.ch/jobs.html) page to the [People](https://zindellab.ch/people.html) page for exactly this.

## What NOT to edit

Please only touch your own card and your own photo. Don't change:

- `_quarto.yml` — site config (navbar, theme, pages list)
- `theme-dark.scss` — colors, fonts, spacing
- `index.qmd`, `publications.qmd`, `jobs.qmd`, `contact.qmd` — global pages
- Other people's files in `_people/`
- `.github/workflows/` — deploy pipeline
- `assets/` outside of `assets/people/<your-photo>.jpg`

If anything else on the site needs changing, please contact the PI.

## How publishing works

Every commit to `main` triggers a GitHub Action that re-renders the whole site and deploys it to <https://zindellab.ch> within ~1–2 minutes.

If a commit accidentally breaks the build (rare — typically a YAML or markdown typo), the site stays on the last working version. Nothing broken ever goes public; the PI is notified by email about the failed build.

## Tech notes

- Framework: [Quarto](https://quarto.org) (multi-page website mode)
- Theme: dark-only, custom SCSS layer on top of `darkly`
- Font: DIN Next webfont (institutionally licensed), self-hosted under `assets/fonts/`
- Deploy: GitHub Pages via `.github/workflows/publish.yml` using the modern Actions flow
- Custom domain via the `CNAME` file at repo root
- Per-person cards: partials in `_people/`, included into `people.qmd` via `{{< include … >}}` shortcodes
