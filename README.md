# tech-resume

A Claude Code skill that writes tailored resumes and cover letters for tech jobs. It interviews you once to build a career profile, asks a few targeted questions for each job description, and produces DOCX and PDF files that:

- parse cleanly in ATS and AI screeners (Greenhouse, Lever, Ashby, Workday): single column, contact info in the body, no tables or text boxes, embedded fonts, no ligatures
- cover the job description's must-have terms with bullets that prove them, not just a skills list
- don't read as AI-written: a lint pass flags stock AI resume words, dashes, uniform bullets, and -ing riders before anything is built

It never invents numbers, titles, or tools. If a bullet needs a fact you haven't given it, it asks.

## Install

Requires [Claude Code](https://docs.claude.com/en/docs/claude-code), Python 3.9+, and git.

1. Clone the skill into your Claude Code skills folder. The scripts are called from this path, so keep the folder name `tech-resume`:

   ```bash
   git clone https://github.com/mzupan/tech-resume.git ~/.claude/skills/tech-resume
   ```

2. Install the Python packages the build and verify scripts use, in the same Python that `python3` runs in your shell:

   ```bash
   pip3 install -r ~/.claude/skills/tech-resume/requirements.txt
   ```

3. Install poppler for `pdftotext` and `pdftoppm` (recommended; the scripts fall back to pypdf without it):

   ```bash
   brew install poppler          # macOS
   sudo apt install poppler-utils  # Debian/Ubuntu
   ```

4. Optional but recommended: install the two writing skills the human-voice pass uses. The skill looks for them at these paths; without them it falls back to its own lint rules.

   ```bash
   git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer
   git clone https://github.com/theclaymethod/unslop.git ~/.claude/skills/unslop
   ```

   - [humanizer](https://github.com/blader/humanizer) rewrites AI writing patterns based on Wikipedia's "Signs of AI writing".
   - [unslop](https://github.com/theclaymethod/unslop) adds a phrase scanner that `scripts/lint.py` merges into its report.

5. Restart Claude Code. The skill shows up as `/tech-resume`.

PDFs use Arial when it's installed (macOS has it; on Linux install `ttf-mscorefonts-installer`) and fall back to Helvetica otherwise.

## Use

Run Claude Code from the folder where you want your career data to live (for example `~/career`). The skill creates `profile/` and `applications/` there.

| Command | What it does |
|---|---|
| `/tech-resume init old-resume.pdf` | Seeds your profile from an existing resume or LinkedIn PDF export and reports what would break in an ATS |
| `/tech-resume profile` | Interviews you role by role for scope, numbers, and ownership |
| `/tech-resume target staff` | Sets the level you're aiming for (senior, staff, principal, manager, director, vp, architect) |
| `/tech-resume apply <job URL or text>` | Asks 3-8 gap questions, then writes the resume and cover letter |
| `/tech-resume resume <JD>` / `cover <JD>` | Resume only / cover letter only |
| `/tech-resume review resume.pdf [JD]` | Critiques an existing resume and ranks fixes by impact |
| `/tech-resume base` | Lists base resumes, if you keep more than one version of your history |

Each application gets its own folder:

```
applications/2026-10-11-company-role/
  jd.md  keywords.txt  gaps.md  resume.md  cover-letter.md  report.md
  First-Last-Resume-Company.docx/.pdf
  First-Last-Cover-Letter-Company.docx/.pdf
```

`report.md` lists must-have keyword coverage, what was left out on purpose, and the facts that would most improve that resume.

Your profile and applications hold personal data. Keep that folder out of public repos.

## Scripts

The skill drives these, but they also work on their own:

| Script | Purpose |
|---|---|
| `scripts/extract.py` | Old resume (PDF, DOCX, TXT, MD) to text, with a parse report |
| `scripts/build.py` | Markdown to ATS-safe DOCX and PDF |
| `scripts/verify.py` | Parse test of the built files plus keyword coverage by section |
| `scripts/lint.py` | Flags AI-sounding and generic writing in a resume or letter |

`references/research.md` lists the sources behind the formatting and writing rules.

## License

MIT
