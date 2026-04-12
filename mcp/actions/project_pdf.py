"""Generate a PDF from a project markdown file via LaTeX.

LaTeX handles all layout: page sizing, table column widths, page breaks,
font scaling, and section grouping. This action converts the markdown to
a .tex file and compiles it with lualatex.
"""

import os
import re
import subprocess
import tempfile

import frontmatter

from _projects import PROJECTS_DIR

VERB_GROUP = "create"
SKILL_GROUP = "projects"

SCHEMA = {
    "description": "Generate a formatted PDF from a project file, keeping sections together on pages",
    "input": {
        "properties": {
            "file": {
                "type": "string",
                "description": "Project filename (e.g. 'kubota-tractor-maintenance.md')",
            },
            "page_size": {
                "type": "string",
                "description": "Page size: letter, a4, legal, a5, halfletter, 5x8, 4x6 (default: letter)",
            },
            "booklet": {
                "type": "boolean",
                "description": "Impose pages for saddle-stitch booklet printing (halfletter, a5 only)",
            },
        },
        "required": ["file"],
    },
    "output": {
        "properties": {
            "pdf": {
                "type": "string",
                "description": "Path to the generated PDF file",
            },
        },
    },
}

TINYTEX_BIN = os.path.expanduser("~/Library/TinyTeX/bin/universal-darwin")

PAGE_GEOMETRIES = {
    "letter": "letterpaper",
    "a4": "a4paper",
    "legal": "legalpaper",
    "a5": "a5paper",
    "halfletter": "paperwidth=5.5in,paperheight=8.5in",
    "5x8": "paperwidth=5in,paperheight=8in",
    "4x6": "paperwidth=4in,paperheight=6in",
}

# Font sizes per page size (extarticle supports 9pt, 10pt, 11pt, 12pt, etc.)
PAGE_FONT_SIZES = {
    "4x6": "9pt",
    "5x8": "10pt",
    "halfletter": "10pt",
    "a5": "10pt",
    "a4": "11pt",
    "letter": "11pt",
    "legal": "11pt",
}

# Content page size -> physical sheet paper for booklet imposition
BOOKLET_SHEETS = {
    "halfletter": "letterpaper",
    "a5": "a4paper",
}


def _escape_latex(text):
    """Escape special LaTeX characters."""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for char, repl in replacements:
        text = text.replace(char, repl)
    return text


def _md_inline_to_latex(text):
    """Convert markdown inline formatting to LaTeX."""
    text = _escape_latex(text)
    # Bold: **text** -> \textbf{text}
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    # Code: `text` -> \texttt{text}
    text = re.sub(r"`(.+?)`", r"\\texttt{\1}", text)
    return text


def _convert_table(lines):
    """Convert markdown table lines to LaTeX tabularx."""
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    data_rows = []
    for row in lines[2:]:  # skip separator
        data_rows.append([c.strip() for c in row.strip("|").split("|")])

    n_cols = len(header)
    if n_cols == 0:
        return ""

    # Weighted X columns: non-last get 0.7 share, last gets the remainder
    # Ensures last column always gets adequate space on narrow pages
    if n_cols == 1:
        col_spec = r">{\raggedright\arraybackslash}X"
    else:
        small = 0.7
        last = n_cols - small * (n_cols - 1)
        sc = r">{\hsize=" + f"{small}" + r"\hsize\raggedright\arraybackslash}X"
        lc = r">{\hsize=" + f"{last:.1f}" + r"\hsize\raggedright\arraybackslash}X"
        col_spec = " ".join([sc] * (n_cols - 1) + [lc])

    tex = []
    tex.append(r"\begin{tabularx}{\linewidth}{" + col_spec + "}")
    tex.append(r"\toprule")

    # Header
    escaped = [_escape_latex(h) for h in header]
    tex.append(r"\textbf{" + r"} & \textbf{".join(escaped) + r"} \\")
    tex.append(r"\midrule")

    # Data rows with light gray separator lines
    for i, row in enumerate(data_rows):
        cells = row[:n_cols]
        while len(cells) < n_cols:
            cells.append("")
        escaped = [_escape_latex(c) for c in cells]
        tex.append(" & ".join(escaped) + r" \\")
        if i < len(data_rows) - 1:
            tex.append(r"\arrayrulecolor{black!15}\midrule\arrayrulecolor{black}")

    tex.append(r"\bottomrule")
    tex.append(r"\end{tabularx}")
    return "\n".join(tex)


def _convert_section(section_text):
    """Convert a single ## section of markdown to LaTeX."""
    tex = []
    lines = section_text.strip().split("\n")
    table_buffer = []
    section_title = ""  # track current section for marks

    def _mark():
        """Return an inline InsertMark for the current section, or empty."""
        if section_title:
            return r"\InsertMark{sectiontitle}{" + section_title + "}"
        return ""

    for line in lines:
        stripped = line.strip()

        # Flush table buffer
        if table_buffer and not stripped.startswith("|"):
            tex.append(_convert_table(table_buffer))
            tex.append("")
            table_buffer = []

        if not stripped:
            tex.append("")
        elif stripped.startswith("## "):
            title = _escape_latex(stripped[3:])
            section_title = title
            tex.append(r"\needspace{0.33\textheight}")
            tex.append(r"\subsection*{" + title + "}")
            tex.append(r"\InsertMark{sectiontitle}{" + title + "}")
        elif stripped.startswith("### "):
            title = _escape_latex(stripped[4:])
            section_title = title
            tex.append(r"\subsubsection*{" + title + "}")
            tex.append(r"\InsertMark{sectiontitle}{" + title + "}")
        elif stripped.startswith("|"):
            table_buffer.append(stripped)
        elif stripped.startswith("- [ ] "):
            text = _md_inline_to_latex(stripped[6:])
            tex.append(r"\item[$\square$] " + _mark() + text)
        elif stripped.startswith("- [x] "):
            text = _md_inline_to_latex(stripped[6:])
            tex.append(r"\item[$\boxtimes$] " + _mark() + text)
        elif stripped.startswith("- "):
            text = _md_inline_to_latex(stripped[2:])
            tex.append(r"\item " + _mark() + text)
        else:
            tex.append(_mark() + _md_inline_to_latex(stripped))

    if table_buffer:
        tex.append(_convert_table(table_buffer))

    return "\n".join(tex)


def _wrap_lists(tex_body):
    """Wrap consecutive \\item lines in itemize environments."""
    lines = tex_body.split("\n")
    result = []
    in_list = False

    for line in lines:
        is_item = line.strip().startswith(r"\item")

        if is_item and not in_list:
            result.append(r"\begin{itemize}[leftmargin=1.5em,labelsep=0.5em]")
            in_list = True
        elif not is_item and in_list:
            result.append(r"\end{itemize}")
            in_list = False

        result.append(line)

    if in_list:
        result.append(r"\end{itemize}")

    return "\n".join(result)


def _build_tex(post, page_geometry, font_size="11pt"):
    """Build a complete LaTeX document from a frontmatter post."""
    title = _escape_latex(post.metadata.get("title", "Project"))
    status = post.metadata.get("status", "")
    priority = post.metadata.get("priority", "")
    tags = post.metadata.get("tags", [])
    updated = post.metadata.get("updated", "")

    sub_parts = []
    if status:
        sub_parts.append(f"Status: {status}")
    if priority:
        sub_parts.append(f"Priority: {priority}")
    if tags:
        sub_parts.append(f"Tags: {', '.join(tags)}")
    if updated:
        sub_parts.append(f"Updated: {updated}")
    subtitle = _escape_latex("  |  ".join(sub_parts))

    # Convert body sections
    sections = re.split(r"(?=^## )", post.content, flags=re.MULTILINE)
    body_parts = []
    for section in sections:
        if section.strip():
            body_parts.append(_convert_section(section))

    body = _wrap_lists("\n\n".join(body_parts))

    return rf"""
\documentclass[{font_size}]{{extarticle}}
\usepackage{{fontspec}}
\setmainfont{{Avenir Next}}
\usepackage[{page_geometry},margin=0.25in,includehead,headheight=12pt,headsep=2pt]{{geometry}}
\usepackage{{tabularx}}
\usepackage{{booktabs}}
\usepackage{{colortbl}}
\usepackage[shortlabels]{{enumitem}}
\usepackage{{parskip}}
\usepackage{{needspace}}
\usepackage{{amssymb}}
\usepackage{{xcolor}}
\usepackage{{fancyhdr}}

\setlength{{\parindent}}{{0pt}}
\setcounter{{secnumdepth}}{{0}}
\widowpenalties 3 10000 10000 150
\clubpenalties 3 10000 10000 150

% Section mark using new LaTeX kernel marks (works with lualatex)
\NewMarkClass{{sectiontitle}}

\pagestyle{{fancy}}
\fancyhf{{}}
\fancyfoot[C]{{\thepage}}
\makeatletter
\fancyhead[C]{{%
  \edef\@mark@top{{\TopMark{{sectiontitle}}}}%
  \edef\@mark@first{{\FirstMark{{sectiontitle}}}}%
  \ifx\@mark@top\@empty\else
    \ifx\@mark@top\@mark@first
      \small\textit{{\TopMark{{sectiontitle}}\ (cont'd)}}%
    \fi
  \fi
}}
\makeatother
\renewcommand{{\headrulewidth}}{{0pt}}
\fancypagestyle{{plain}}{{\fancyhf{{}}\fancyfoot[C]{{\thepage}}\renewcommand{{\headrulewidth}}{{0pt}}}}

\begin{{document}}
\thispagestyle{{plain}}
\thispagestyle{{plain}}

{{\LARGE \textbf{{{title}}}}}

\smallskip
{{\small \textcolor{{gray}}{{{subtitle}}}}}

\medskip
\hrule
\bigskip

{body}

\end{{document}}
"""


def _build_booklet_tex(content_pdf, sheet_paper, signature):
    """Build a LaTeX wrapper that imposes content pages as a saddle-stitch booklet."""
    return rf"""
\documentclass[{sheet_paper},landscape]{{article}}
\usepackage[{sheet_paper},landscape,margin=0pt]{{geometry}}
\usepackage{{pdfpages}}
\begin{{document}}
\includepdf[pages=-, nup=2x1, signature={signature}]{{{content_pdf}}}
\end{{document}}
"""


def run(file, page_size="letter", booklet=False, **kwargs):
    filepath = PROJECTS_DIR / file
    if not filepath.exists():
        return {"error": f"Project not found: {file}"}

    page_size = page_size.lower().strip()
    if page_size not in PAGE_GEOMETRIES:
        return {"error": f"Unknown page size: {page_size}. Options: {', '.join(PAGE_GEOMETRIES)}"}

    if booklet and page_size not in BOOKLET_SHEETS:
        return {"error": f"Booklet not supported for {page_size}. Options: {', '.join(BOOKLET_SHEETS)}"}

    post = frontmatter.load(str(filepath))
    font_size = PAGE_FONT_SIZES.get(page_size, "11pt")
    tex_source = _build_tex(post, PAGE_GEOMETRIES[page_size], font_size)

    suffix = f"{page_size}-booklet" if booklet else page_size
    pdf_path = filepath.with_name(f"{filepath.stem}-{suffix}.pdf")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "project.tex")
        with open(tex_path, "w") as f:
            f.write(tex_source)

        env = os.environ.copy()
        env["PATH"] = TINYTEX_BIN + ":" + env.get("PATH", "")

        result = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
            capture_output=True,
            env=env,
            timeout=30,
        )

        content_pdf = os.path.join(tmpdir, "project.pdf")
        if not os.path.exists(content_pdf):
            log = result.stdout.decode("utf-8", errors="replace")
            return {"error": f"lualatex failed:\n{log[-2000:]}"}

        if booklet:
            # Parse page count from lualatex output to calculate signature size
            log = result.stdout.decode("utf-8", errors="replace")
            match = re.search(r"Output written on .+\((\d+) pages?,", log)
            if not match:
                return {"error": "Could not determine page count from lualatex output"}
            page_count = int(match.group(1))
            signature = ((page_count + 3) // 4) * 4

            booklet_tex = _build_booklet_tex(
                content_pdf, BOOKLET_SHEETS[page_size], signature
            )
            booklet_tex_path = os.path.join(tmpdir, "booklet.tex")
            with open(booklet_tex_path, "w") as f:
                f.write(booklet_tex)

            result = subprocess.run(
                ["lualatex", "-interaction=nonstopmode", "-output-directory", tmpdir, booklet_tex_path],
                capture_output=True,
                env=env,
                timeout=30,
            )

            final_pdf = os.path.join(tmpdir, "booklet.pdf")
            if not os.path.exists(final_pdf):
                log = result.stdout.decode("utf-8", errors="replace")
                return {"error": f"Booklet imposition failed:\n{log[-2000:]}"}
        else:
            final_pdf = content_pdf

        import shutil
        shutil.copy(final_pdf, str(pdf_path))

    return {"pdf": str(pdf_path)}
