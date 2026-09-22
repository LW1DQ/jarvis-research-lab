#!/usr/bin/env python3
"""
Writer Agent - Markdown + Pandoc + Zotero Integration
Generates academic documents in Markdown, converts to DOCX via Pandoc with Zotero citations
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Zotero integration
try:
    from pyzotero import zotero
except ImportError:
    zotero = None

# Pandoc via panflute
try:
    import panflute as pf
except ImportError:
    pf = None


@dataclass
class Citation:
    """Represents a citation with Zotero metadata"""
    key: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    item_type: str = "article"
    zotero_key: Optional[str] = None


@dataclass
class DocumentSection:
    """Represents a document section"""
    title: str
    level: int = 1
    content: str = ""
    subsections: List['DocumentSection'] = field(default_factory=list)


@dataclass
class Document:
    """Represents a complete document"""
    title: str
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    sections: List[DocumentSection] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ZoteroManager:
    """Manages Zotero library and citations"""
    
    def __init__(self, library_id: str = None, library_type: str = "user", api_key: str = None):
        if not zotero:
            raise ImportError("pyzotero not installed. Run: pip install pyzotero")
        
        self.library_id = library_id or os.getenv("ZOTERO_LIBRARY_ID")
        self.library_type = library_type
        self.api_key = api_key or os.getenv("ZOTERO_API_KEY")
        
        if not self.library_id or not self.api_key:
            raise ValueError("ZOTERO_LIBRARY_ID and ZOTERO_API_KEY must be set")
        
        self.client = zotero.Zotero(self.library_id, self.library_type, self.api_key)
    
    def search_items(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Zotero library"""
        try:
            return self.client.items(q=query, limit=limit)
        except Exception as e:
            print(f"Zotero search error: {e}")
            return []
    
    def get_item(self, key: str) -> Optional[Dict]:
        """Get item by key"""
        try:
            return self.client.item(key)
        except Exception as e:
            print(f"Zotero get error: {e}")
            return None
    
    def create_citation(self, item: Dict) -> Citation:
        """Convert Zotero item to Citation"""
        data = item.get("data", {})
        creators = data.get("creators", [])
        authors = [f"{c.get('lastName', '')}, {c.get('firstName', '')}" for c in creators]
        
        return Citation(
            key=data.get("key", ""),
            title=data.get("title", ""),
            authors=authors,
            year=data.get("date", "")[:4] if data.get("date") else None,
            doi=data.get("DOI"),
            url=data.get("url"),
            item_type=data.get("itemType", "article"),
            zotero_key=data.get("key")
        )
    
    def format_citation(self, citation: Citation, style: str = "apa") -> str:
        """Format citation for Pandoc"""
        # Pandoc citation format: [@key]
        return f"[@{citation.key}]"


class PandocConverter:
    """Converts Markdown to DOCX using Pandoc with Zotero citations"""
    
    def __init__(self, csl_style: str = "apa", bibliography_path: str = None):
        self.csl_style = csl_style
        self.bibliography_path = bibliography_path
        
        # Check if pandoc is available
        try:
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            self.pandoc_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.pandoc_available = False
            print("Warning: pandoc not found. Install with: sudo apt-get install pandoc")
    
    def markdown_to_docx(
        self, 
        markdown_content: str, 
        output_path: str,
        citations: List[Citation] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Convert Markdown to DOCX with Pandoc"""
        if not self.pandoc_available:
            print("Error: pandoc not available")
            return False
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as md_file:
            md_file.write(markdown_content)
            md_path = md_file.name
        
        bib_path = None
        if citations:
            bib_path = self._create_bibtex(citations)
        
        try:
            # Build pandoc command
            cmd = [
                "pandoc",
                md_path,
                "-o", output_path,
                "--from", "markdown",
                "--to", "docx",
                "--standalone",
                "--citeproc",
            ]
            
            # Skip CSL file if not available - Pandoc will use default style
            # cmd.extend(["--csl", self._get_csl_file(self.csl_style)])
            
            if bib_path:
                cmd.extend(["--bibliography", bib_path])
            
            if metadata:
                # Add metadata as variables
                for key, value in metadata.items():
                    cmd.extend(["--metadata", f"{key}={value}"])
            
            # Add reference-doc for custom styling (optional)
            # cmd.extend(["--reference-doc", "reference.docx"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"Pandoc error: {result.stderr}")
                return False
            
            print(f"DOCX generated: {output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            print("Pandoc timeout")
            return False
        except Exception as e:
            print(f"Pandoc error: {e}")
            return False
        finally:
            # Cleanup temp files
            try:
                os.unlink(md_path)
            except:
                pass
            if bib_path:
                try:
                    os.unlink(bib_path)
                except:
                    pass
    
    def _get_csl_file(self, style: str) -> str:
        """Get CSL file path for citation style"""
        # Common CSL styles available in Pandoc
        csl_map = {
            "apa": "apa",
            "ieee": "ieee",
            "mla": "modern-language-association",
            "chicago": "chicago-author-date",
            "harvard": "harvard1",
        }
        
        style_key = style.lower()
        if style_key in csl_map:
            return csl_map[style_key]
        else:
            # Return the style name directly - pandoc will try to find it
            return style_key
    
    def _create_bibtex(self, citations: List[Citation]) -> str:
        """Create temporary BibTeX file from citations"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
            for cite in citations:
                entry = self._citation_to_bibtex(cite)
                f.write(entry + "\n\n")
            return f.name
    
    def _citation_to_bibtex(self, citation: Citation) -> str:
        """Convert Citation to BibTeX entry"""
        entry_type = self._map_item_type(citation.item_type)
        fields = [
            f"@article{{{citation.key},",
            f"  title = {{{citation.title}}},",
            f"  author = {{{' and '.join(citation.authors)}}},",
        ]
        
        if citation.year:
            fields.append(f"  year = {{{citation.year}}},")
        if citation.doi:
            fields.append(f"  doi = {{{citation.doi}}},")
        if citation.url:
            fields.append(f"  url = {{{citation.url}}},")
        
        fields.append("}")
        return "\n".join(fields)
    
    def _map_item_type(self, item_type: str) -> str:
        """Map Zotero item type to BibTeX entry type"""
        type_map = {
            "journalArticle": "article",
            "book": "book",
            "bookSection": "incollection",
            "conferencePaper": "inproceedings",
            "preprint": "article",
            "thesis": "phdthesis",
            "report": "techreport",
            "webpage": "misc",
        }
        return type_map.get(item_type, "article")


class MarkdownDocumentBuilder:
    """Builds Markdown documents programmatically"""
    
    def __init__(self):
        self.sections: List[DocumentSection] = []
        self.citations: List[Citation] = []
        self.metadata: Dict[str, Any] = {}
    
    def set_metadata(self, title: str, authors: List[str] = None, abstract: str = "", **kwargs):
        self.metadata = {
            "title": title,
            "authors": authors or [],
            "abstract": abstract,
            "date": datetime.now().strftime("%Y-%m-%d"),
            **kwargs
        }
    
    def add_section(self, title: str, level: int = 1, content: str = "") -> DocumentSection:
        section = DocumentSection(title=title, level=level, content=content)
        self.sections.append(section)
        return section
    
    def add_subsection(self, parent: DocumentSection, title: str, content: str = "") -> DocumentSection:
        subsection = DocumentSection(title=title, level=parent.level + 1, content=content)
        parent.subsections.append(subsection)
        return subsection
    
    def add_citation(self, citation: Citation):
        self.citations.append(citation)
    
    def add_text(self, text: str):
        """Add text to the last section"""
        if self.sections:
            self.sections[-1].content += "\n" + text
        else:
            # Create a default section
            self.add_section("", level=1, content=text)
    
    def add_citation_ref(self, citation_key: str):
        """Add citation reference in text"""
        self.add_text(f"[@{citation_key}]")
    
    def to_markdown(self) -> str:
        """Convert to Markdown string"""
        lines = []
        
        # YAML frontmatter
        if self.metadata:
            lines.append("---")
            for key, value in self.metadata.items():
                if isinstance(value, list):
                    lines.append(f"{key}:")
                    for v in value:
                        lines.append(f"  - {v}")
                else:
                    lines.append(f"{key}: {value}")
            lines.append("---")
            lines.append("")
        
        # Sections
        for section in self.sections:
            lines.extend(self._section_to_markdown(section))
        
        # Bibliography placeholder (Pandoc will fill this)
        if self.citations:
            lines.append("\n# References")
            lines.append("")
        
        return "\n".join(lines)
    
    def _section_to_markdown(self, section: DocumentSection, level: int = 0) -> List[str]:
        lines = []
        indent = "  " * level
        prefix = "#" * (section.level + level)
        lines.append(f"{indent}{prefix} {section.title}")
        if section.content:
            lines.append(f"{indent}{section.content}")
        for subsection in section.subsections:
            lines.extend(self._section_to_markdown(subsection, level + 1))
        return lines


class WriterAgent:
    """
    Writer Agent that produces academic documents in Markdown,
    converts to DOCX via Pandoc with Zotero citations.
    """
    
    def __init__(self, zotero_manager: ZoteroManager = None):
        self.zotero = zotero_manager
        self.pandoc = PandocConverter()
        self.builder = MarkdownDocumentBuilder()
    
    def create_document(
        self,
        title: str,
        research_findings: List[str],
        ns3_results: List[str] = None,
        critique_feedback: str = None,
        revision: int = 0
    ) -> Document:
        """Create a complete document from research findings"""
        
        # Initialize builder
        self.builder = MarkdownDocumentBuilder()
        self.builder.set_metadata(
            title=title,
            authors=["JARVIS Research Assistant"],
            abstract=f"Research report on {title} generated by JARVIS Research Assistant."
        )
        
        # Add research findings
        if research_findings:
            research_section = self.builder.add_section("Literature Review", level=1)
            for i, finding in enumerate(research_findings):
                self.builder.add_text(f"## Finding {i+1}\n{finding}")
        
        # Add NS-3 results
        if ns3_results:
            ns3_section = self.builder.add_section("NS-3 Simulation Results", level=1)
            for result in ns3_results:
                self.builder.add_text(result)
        
        # Add critique feedback if revision
        if critique_feedback and revision > 0:
            critique_section = self.builder.add_section("Revision Notes", level=1)
            self.builder.add_text(f"Revision {revision} based on critique feedback:\n{critique_feedback}")
        
        # Generate markdown
        markdown = self.builder.to_markdown()
        
        # Convert to DOCX
        output_path = f"/home/diego/research-jarvis/projects/{title.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        # Prepare citations from builder
        citations = []  # Would be populated from research findings
        
        success = self.pandoc.markdown_to_docx(
            markdown_content=markdown,
            output_path=output_path,
            citations=citations,
            metadata={"title": title}
        )
        
        # Create document object
        doc = Document(
            title=title,
            sections=[DocumentSection(title=s.title, level=s.level, content=s.content) for s in self.builder.sections],
            citations=self.builder.citations,
            metadata=self.builder.metadata
        )
        
        return doc
    
    def export_markdown(self, output_path: str) -> bool:
        """Export document as Markdown file"""
        markdown = self.builder.to_markdown()
        try:
            with open(output_path, 'w') as f:
                f.write(self.builder.to_markdown())
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False


# ============================================================
# Convenience Functions
# ============================================================

def create_writer_agent(zotero_library_id: str = None, zotero_api_key: str = None) -> WriterAgent:
    """Factory function to create WriterAgent with Zotero"""
    zotero_manager = None
    if zotero_library_id and zotero_api_key:
        zotero_manager = ZoteroManager(zotero_library_id, api_key=zotero_api_key)
    return WriterAgent(zotero_manager)


# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Writer Agent - Markdown + Pandoc + Zotero")
    parser.add_argument("--topic", default="MARL for WiFi scheduling in dense networks", help="Research topic")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()
    
    writer = create_writer_agent()
    
    doc = writer.create_document(
        title=args.topic,
        research_findings=[
            "Finding 1: MARL improves scheduling efficiency in dense WiFi networks",
            "Finding 2: Centralized training with decentralized execution (CTDE) paradigm shows promise",
            "Finding 3: Reward shaping is critical for convergence in dense environments"
        ],
        ns3_results=["NS-3 simulation shows 23% throughput improvement with MARL scheduler"]
    )
    
    print(f"Document created: {doc.title}")
    print(f"Sections: {len(doc.sections)}")