#!/usr/bin/env node
/**
 * Generate static gallery pages under each city's photos/ tree.
 * For every city (dir with index.html), if photos/ exists, create an index.html in:
 * - photos/
 * - photos/<subdir>/** for all subdirectories
 *
 * Each gallery page lists immediate subfolders and the images in that folder only.
 * Thumbnails pair mini_* -> full-size in same folder; otherwise use the image itself.
 * Navigation:
 * - Back to city top (../../.. as needed)
 * - Back to parent gallery for subfolders
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..', '..');

function listCityDirs(root) {
  const out = [];
  const skip = new Set(['assets', '.git', 'node_modules']);
  function walk(dir, depth = 0) {
    if (depth > 6) return;
    for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, ent.name);
      if (ent.isDirectory()) {
        if (skip.has(ent.name)) continue;
        walk(full, depth + 1);
      } else if (ent.isFile() && ent.name === 'index.html') {
        out.push(path.dirname(full));
      }
    }
  }
  walk(root);
  return out;
}

function readCityTitle(cityDir) {
  const dataPath = path.join(cityDir, 'data.js');
  try {
    const code = fs.readFileSync(dataPath, 'utf8');
    const ctx = { window: {} };
    vm.createContext(ctx);
    vm.runInContext(code, ctx, { timeout: 1000 });
    const p = ctx.window.TDM_PAGE || {};
    if (typeof p.title === 'string' && p.title.trim()) return p.title.trim();
  } catch {}
  // fallback to index.html <title>
  try {
    const html = fs.readFileSync(path.join(cityDir, 'index.html'), 'utf8');
    const m = html.match(/<title>([\s\S]*?)<\/title>/i);
    if (m) return m[1].trim();
  } catch {}
  return '';
}

function readCaption(absFolder, imgName) {
  const baseNoMini = imgName.replace(/^mini_/i, '');
  const stem = baseNoMini.replace(/\.(jpe?g|png|webp)$/i, '');
  const txt = stem + '.txt';
  const txtPath = path.join(absFolder, txt);
  try {
    if (fs.existsSync(txtPath)) {
      return fs.readFileSync(txtPath, 'utf8').trim();
    }
  } catch {}
  return '';
}

function listFolderImages(absFolder) {
  const files = fs.readdirSync(absFolder, { withFileTypes: true })
    .filter((d) => d.isFile() && /\.(jpe?g|png|webp)$/i.test(d.name))
    .map(d => d.name)
    .sort();
  const set = new Set(files);
  const items = [];
  const addedThumb = new Set();
  for (const f of files) {
    if (/^mini_/i.test(f)) {
      const full = f.replace(/^mini_/i, '');
      const href = set.has(full) ? full : f;
      const title = readCaption(absFolder, f);
      items.push({ href, src: f, title });
      addedThumb.add(f);
    }
  }
  for (const f of files) {
    if (/^mini_/i.test(f)) continue;
    const mini = 'mini_' + f;
    if (addedThumb.has(mini)) continue;
    const title = readCaption(absFolder, f);
    items.push({ href: f, src: f, title });
  }
  return items;
}

function assetsPrefixForDepth(depthFromCity) {
  // From city root, assets is ../../assets
  // From photos/ (depth 1): ../../../assets => '../' * (2+1)
  return '../'.repeat(2 + depthFromCity) + 'assets/';
}

function pathToCityTop(depthFromPhotosFolder) {
  return '../'.repeat(depthFromPhotosFolder + 1) + 'index.html#top';
}

function parentLink(depthFromPhotosFolder) {
  if (depthFromPhotosFolder === 0) return '';
  return '../index.html';
}

function makeHtml({ cityTitle, relFolder, absFolder, depth }) {
  const assets = assetsPrefixForDepth(depth + 1);
  const backTop = pathToCityTop(depth);
  const parentHref = parentLink(depth);

  // Subfolder links (immediate children only)
  const subdirs = fs.readdirSync(absFolder, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name).sort();
  const subLinks = subdirs.map(n => `        <li><a href="${n}/index.html">${n}</a></li>`).join('\n');

  const images = listFolderImages(absFolder);
  const gallery = images.map(it => {
    const titleAttr = it.title ? ` title=\"${it.title.replace(/\"/g, '&quot;')}\"` : '';
    const alt = it.title ? it.title.replace(/\"/g, '&quot;') : '';
    return `          <a data-lightbox=\"gallery\" href=\"${it.href}\" target=\"_blank\"${titleAttr}>\n            <img loading=\"lazy\" src=\"${it.src}\" alt=\"${alt}\" />\n          </a>`;
  }).join('\n');

  return `<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${cityTitle}${relFolder ? ' – ' + relFolder : ''}</title>
    <link rel="stylesheet" href="${assets}styles.css" />
    <link rel="stylesheet" href="${assets}fonts.css" />
    <link rel="stylesheet" href="${assets}theme.css" />
    <link rel="stylesheet" href="${assets}lightbox.css" />
  </head>
  <body>
    <main class="content" style="max-width:1200px;margin:0 auto;padding:16px">
      <div class="backlink" style="margin-bottom:8px">
        <a href="${backTop}">← Retour à la page ville</a>
        ${parentHref ? ` · <a href="${parentHref}">Dossier parent</a>` : ''}
      </div>
      <h1 style="margin:8px 0 16px">${cityTitle}${relFolder ? ' – ' + relFolder : ''}</h1>
      ${subdirs.length ? `<div class="subfolders"><strong>Dossiers</strong><ul>${subLinks}</ul></div>` : ''}
      <div class="gallery" style="margin-top:12px">
${gallery}
      </div>
    </main>

    <script src="${assets}lightbox.js"></script>
    <script src="${assets}theme.js"></script>
  </body>
</html>`;
}

function buildCityPhotos(cityDir) {
  const photosDir = path.join(cityDir, 'photos');
  if (!fs.existsSync(photosDir)) return 0;
  const cityTitle = readCityTitle(cityDir);

  // Walk all folders under photos
  const folders = [];
  function walk(rel, depth) {
    folders.push({ rel, depth, abs: path.join(photosDir, rel) });
    for (const ent of fs.readdirSync(path.join(photosDir, rel || '.'), { withFileTypes: true })) {
      if (ent.isDirectory()) walk(path.posix.join(rel, ent.name), depth + 1);
    }
  }
  walk('', 0);

  let written = 0;
  for (const f of folders) {
    const html = makeHtml({ cityTitle, relFolder: f.rel, absFolder: f.abs, depth: f.depth });
    const outPath = path.join(f.abs, 'index.html');
    fs.writeFileSync(outPath, html, 'utf8');
    written++;
  }
  return written;
}

function main() {
  const cities = listCityDirs(ROOT);
  let totalPages = 0;
  for (const dir of cities) {
    totalPages += buildCityPhotos(dir);
  }
  console.log('build-photo-pages complete. generated', totalPages, 'gallery pages');
}

if (require.main === module) main();
