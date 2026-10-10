# Thomas Giglia — Portfolio

A static site (plain HTML/CSS/JS, no build step) ready to host on [Vercel](https://vercel.com).

```
index.html                  Home: project gallery + "More projects"
projects/<slug>/index.html  One page per project
assets/                     CSS, JS, KaTeX, optimized images, videos, docs
vercel.json                 Clean URLs (/projects/fsae instead of .../index.html)
```

## Deploy (GitHub → Vercel)

1. Create a new **empty** repository on GitHub, e.g. `portfolio` (no README).
2. In this folder, run:
   ```bash
   git init
   git add .
   git commit -m "Portfolio site"
   git branch -M main
   git remote add origin https://github.com/thomas-giglia/portfolio.git
   git push -u origin main
   ```
   (Or use GitHub Desktop: *File → Add local repository → Publish repository*.)
3. Go to **vercel.com → Add New… → Project**, import the `portfolio` repo.
   - Framework preset: **Other**
   - Build command: *(leave empty)*
   - Output directory: *(leave empty / `.`)*
4. Click **Deploy**. Every later `git push` redeploys automatically.

## Preview locally

```bash
npx serve .
```
Then open http://localhost:3000 (clean URLs work the same as on Vercel).

## Editing

Pages are plain HTML. Text lives in `projects/<slug>/index.html`; shared styles in
`assets/site.css`. Images are WebP under `assets/img/<slug>/`.
