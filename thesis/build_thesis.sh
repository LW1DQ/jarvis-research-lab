#!/bin/bash
# build_thesis.sh - Compila la tesis con Pandoc
# Ubicación: ~/research-jarvis/thesis/build_thesis.sh

set -e

THESIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_FILE="$THESIS_DIR/main.md"
OUTPUT_DIR="$THESIS_DIR/output"

mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "  Building JARVIS Research Thesis"
echo "=========================================="
echo ""

# Verificar archivos
if [ ! -f "$MAIN_FILE" ]; then
    echo "ERROR: $MAIN_FILE not found"
    exit 1
fi

if [ ! -f "$THESIS_DIR/bibliography/references.bib" ]; then
    echo "ERROR: bibliography/references.bib not found"
    exit 1
fi

# Descargar IEEE CSL si no existe
CSL_FILE="$THESIS_DIR/bibliography/ieee.csl"
if [ ! -f "$CSL_FILE" ]; then
    echo "Downloading IEEE CSL style..."
    curl -sL "https://raw.githubusercontent.com/citation-style-language/styles/master/ieee.csl" -o "$CSL_FILE"
fi

# Verificar Pandoc
if ! command -v pandoc &> /dev/null; then
    echo "ERROR: pandoc not installed. Install with: sudo apt install pandoc"
    exit 1
fi

# Verificar LaTeX (para PDF)
LATEX_ENGINE="xelatex"
if ! command -v xelatex &> /dev/null; then
    echo "WARNING: xelatex not found. PDF generation may fail."
    echo "Install with: sudo apt install texlive-xetex texlive-fonts-recommended texlive-latex-extra"
    LATEX_ENGINE="pdflatex"
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Building outputs..."
echo "  Timestamp: $TIMESTAMP"
echo "  Main file: $MAIN_FILE"
echo "  Output dir: $OUTPUT_DIR"
echo ""

# 1. PDF (LaTeX via Pandoc)
echo "1. Generating PDF..."
pandoc "$MAIN_FILE" \
    --from markdown \
    --to pdf \
    --pdf-engine="$LATEX_ENGINE" \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    --variable=geometry:margin=2.5cm \
    --variable=fontsize:11pt \
    --variable=linestretch:1.15 \
    --variable=documentclass:report \
    --variable=classoption:oneside \
    --metadata=title:"JARVIS Research: Asistente de Investigación Automatizado para Doctorado con Simulaciones NS-3 y Deep Learning" \
    --metadata=author:"Diego [Apellido]" \
    --metadata=date:"$(date +%Y-%m-%d)" \
    --metadata=degree:"Doctorado en [Área]" \
    --metadata=university:"[Universidad]" \
    --metadata=department:"[Departamento]" \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.pdf"

if [ $? -eq 0 ]; then
    echo "   ✓ PDF: $OUTPUT_DIR/thesis_${TIMESTAMP}.pdf"
else
    echo "   ✗ PDF generation failed"
fi

# 2. DOCX (Word)
echo "2. Generating DOCX..."
pandoc "$MAIN_FILE" \
    --from markdown \
    --to docx \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    --reference-doc="$THESIS_DIR/templates/ieee_reference.docx" \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.docx" 2>/dev/null || \
pandoc "$MAIN_FILE" \
    --from markdown \
    --to docx \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.docx"

if [ $? -eq 0 ]; then
    echo "   ✓ DOCX: $OUTPUT_DIR/thesis_${TIMESTAMP}.docx"
else
    echo "   ✗ DOCX generation failed"
fi

# 3. LaTeX (para edición manual)
echo "3. Generating LaTeX..."
pandoc "$MAIN_FILE" \
    --from markdown \
    --to latex \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    --variable=geometry:margin=2.5cm \
    --variable=fontsize:11pt \
    --variable=linestretch:1.15 \
    --variable=documentclass:report \
    --variable=classoption:oneside \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.tex"

if [ $? -eq 0 ]; then
    echo "   ✓ LaTeX: $OUTPUT_DIR/thesis_${TIMESTAMP}.tex"
else
    echo "   ✗ LaTeX generation failed"
fi

# 4. HTML (para web)
echo "4. Generating HTML..."
pandoc "$MAIN_FILE" \
    --from markdown \
    --to html5 \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    --standalone \
    --css="$THESIS_DIR/templates/thesis.css" \
    --metadata=title:"JARVIS Research Thesis" \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.html"

if [ $? -eq 0 ]; then
    echo "   ✓ HTML: $OUTPUT_DIR/thesis_${TIMESTAMP}.html"
else
    echo "   ✗ HTML generation failed"
fi

# 5. EPUB (para e-readers)
echo "5. Generating EPUB..."
pandoc "$MAIN_FILE" \
    --from markdown \
    --to epub3 \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    --epub-cover-image="$THESIS_DIR/templates/cover.png" \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.epub" 2>/dev/null || \
pandoc "$MAIN_FILE" \
    --from markdown \
    --to epub3 \
    --citeproc \
    --bibliography="$THESIS_DIR/bibliography/references.bib" \
    --csl="$CSL_FILE" \
    --number-sections \
    --toc \
    --toc-depth=3 \
    -o "$OUTPUT_DIR/thesis_${TIMESTAMP}.epub"

if [ $? -eq 0 ]; then
    echo "   ✓ EPUB: $OUTPUT_DIR/thesis_${TIMESTAMP}.epub"
else
    echo "   ✗ EPUB generation failed (cover image optional)"
fi

# Copiar bibliografía
cp "$THESIS_DIR/bibliography/references.bib" "$OUTPUT_DIR/references_${TIMESTAMP}.bib"

echo ""
echo "=========================================="
echo "  Build Complete!"
echo "=========================================="
echo ""
echo "Outputs in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"/thesis_${TIMESTAMP}.*
echo ""
echo "To compile LaTeX manually:"
echo "  cd $OUTPUT_DIR"
echo "  xelatex thesis_${TIMESTAMP}.tex"
echo "  biber thesis_${TIMESTAMP}"
echo "  xelatex thesis_${TIMESTAMP}.tex"
echo "  xelatex thesis_${TIMESTAMP}.tex"