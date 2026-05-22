# The Goodbook — Tiberius Inscriptus Interlinearis

Campaign ledger for **Tiberius Inscriptus Interlinearis**, Level 3 Illusionist Wizard.  
Player: Chris · Campaign: Frank's

## 🌐 Live Site
After enabling GitHub Pages → deploy from Actions:  
`https://<your-username>.github.io/Tiberius---Online-Campaign-Frank/`

## 📁 Structure

| File | Purpose |
|---|---|
| `index.qmd` | Character overview |
| `treasury.qmd` | Gold ledger (party accounting) |
| `spells.qmd` | Spell usage journal |
| `items.qmd` | Item acquisitions log |
| `milestones.qmd` | XP / level-up log |
| `generate_ledger.py` | Generates `Tiberius-Ledger.pdf` (printable version) |
| `Tiberius.pdf` | Filled character sheet |
| `_quarto.yml` | Quarto site config |
| `.github/workflows/deploy.yml` | Auto-deploy to GitHub Pages on every push |

## 🚀 Local preview

```bash
quarto preview
```

## 📄 Regenerate printable PDF

```bash
.venv/bin/python generate_ledger.py
```
