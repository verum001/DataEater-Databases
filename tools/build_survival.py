"""Reproducible local preparation of format-v1 databases from supplied PDF files.

Requires PyMuPDF. Source redistribution permissions are checked separately.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
MANUALS = [
    ("army-survival-2002", "fm3-05-70 sirvival.pdf", "FM 3-05.70 (FM 21-76): Survival (May 2002)", "Department of the Army", 2002, "U.S. government work; supplied edition carries a distribution restriction, retained in extracted text"),
    ("nwss-1987", "NWSS 1987.pdf", "Nuclear War Survival Skills: Updated and Expanded 1987 Edition", "Oregon Institute of Science and Medicine; Cresson H. Kearny", 1987, "Cresson H. Kearny conditional reproduction terms and electronic edition notice; see SOURCE_NOTICES.md"),
    ("af-sere-2017", "AFH 10-644 Survival Evasion Resistance Escape .pdf", "AFH 10-644: Survival Evasion Resistance Escape (SERE) Operations (27 March 2017)", "Department of the Air Force", 2017, "U.S. government work; source states no releasability restrictions; third-party credits retained"),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def ordered_blocks(page, columns):
    blocks = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]
    if not columns:
        return sorted(blocks, key=lambda b: (round(b[1], 1), b[0]))
    # The NWSS edition has two text columns. Full-width text blocks divide
    # the page into bands; within each band read left, then right.
    middle = page.rect.width / 2
    left = [b for b in blocks if b[2] <= middle + 12]
    right = [b for b in blocks if b[0] >= middle - 12 and b not in left]
    if not left or not right:
        return sorted(blocks, key=lambda b: (b[1], b[0]))
    spans = sorted([b for b in blocks if b not in left and b not in right], key=lambda b: b[1])
    result = []
    remaining = left + right
    for span in spans:
        band = [b for b in remaining if b[1] < span[1]]
        result.extend(sorted(band, key=lambda b: (b[0] >= middle - 12, b[1], b[0])))
        remaining = [b for b in remaining if b not in band]
        result.append(span)
    result.extend(sorted(remaining, key=lambda b: (b[0] >= middle - 12, b[1], b[0])))
    assert len(result) == len(blocks)
    return result


def build(only_public=False):
    manuals = [MANUALS[-1]] if only_public else MANUALS
    sources, chunks, audit = [], [], []
    for source_id, filename, title, publisher, year, license_text in manuals:
        path = ROOT / "survival" / "sources" / filename
        document = pymupdf.open(path)
        sources.append(dict(id=source_id, title=title, publisher=publisher, year=year,
                            license=license_text, language="en", original_file=filename,
                            sha256=digest(path.read_bytes()), pdf_pages=len(document)))
        # Only genuine PDF bookmarks supply navigation ancestry.
        headings = {}
        stack = []
        for level, heading, number in document.get_toc():
            if not 1 <= number <= len(document):
                continue
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, " ".join(heading.split())))
            headings[number] = " > ".join(h for _, h in stack)[:2000]
        section = ""
        for number, page in enumerate(document, 1):
            section = headings.get(number, section)
            blocks = ordered_blocks(page, source_id == "nwss-1987")
            buffer = []
            block_ids = []

            def flush():
                if not buffer:
                    return
                text = "\n\n".join(buffer)
                chunks.append(dict(id=f"c{len(chunks)+1:06d}", source_id=source_id,
                                   section=section.split(" > ")[-1] if section else "",
                                   page=number, text=text, search_context=section, lang="en",
                                   source_blocks=list(block_ids)))
                buffer.clear()
                block_ids.clear()

            for block_index, block in enumerate(blocks):
                # Line breaks, punctuation, values and all short text remain.
                text = "\n".join(line.rstrip() for line in block[4].splitlines()).strip()
                if buffer and len(("\n\n".join(buffer) + "\n\n" + text).encode()) > 1800:
                    flush()
                # AFH PDF page 389 uses Wingdings F0A7 for a square bullet,
                # verified against the rendered page and the span font.
                if source_id == "af-sere-2017" and number == 389:
                    text = text.replace("\uf0a7", "▪")
                buffer.append(text)
                block_ids.append(block_index)
                if len(text.encode()) > 1800:
                    flush()  # Whole block retained; oversized units are reported.
            flush()
            audit.append(dict(source_id=source_id, page=number, text_blocks=len(blocks),
                              image_count=len(page.get_images()),
                              characters=sum(len(b[4].strip()) for b in blocks)))
        document.close()
    assert len({c['id'] for c in chunks}) == len(chunks)
    known = {s['id']: s['pdf_pages'] for s in sources}
    assert all(c['source_id'] in known and 1 <= c['page'] <= known[c['source_id']] for c in chunks)
    # Every extracted block must occur once, with no dropped short pages.
    for row in audit:
        included = [i for c in chunks if c['source_id'] == row['source_id'] and c['page'] == row['page'] for i in c['source_blocks']]
        assert sorted(included) == list(range(row['text_blocks']))
    source_bytes = encode(sources)
    chunk_bytes = ("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n").encode()
    name = "sere" if only_public else "survival"
    directory = ROOT / name / "versions" / "0.1.0"
    directory.mkdir(parents=True, exist_ok=True)
    description = "; ".join(s['title'] for s in sources)
    manifest = dict(format="dataeater", format_version=1, database_id=f"{name}-0.1.0",
                    name=f"{name.title()} manuals 0.1.0", description=description,
                    language="en", license="Source-specific terms; see sources.json and source notices",
                    encryption="none", created_utc="2026-10-11T00:00:00Z", database_version="0.1.0",
                    counts=dict(documents=len(sources), chunks=len(chunks)),
                    files={n:dict(sha256="sha256:"+digest(b)) for n,b in [('sources.json',source_bytes),('chunks.jsonl',chunk_bytes)]})
    output = directory / f"{name}.dataeater"
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for filename, data in [('manifest.json',encode(manifest)),('sources.json',source_bytes),('chunks.jsonl',chunk_bytes)]:
            info = zipfile.ZipInfo(filename, (2026,10,11,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.namelist()[0] == 'manifest.json'
        assert archive.testzip() is None
        for filename, entry in manifest['files'].items():
            assert 'sha256:'+digest(archive.read(filename)) == entry['sha256']
    report = dict(version="0.1.0", sources=sources, pages=len(audit), chunks=len(chunks),
                  bytes=output.stat().st_size, sha256=digest(output.read_bytes()),
                  oversized_passages=[dict(id=c['id'], source_id=c['source_id'], page=c['page'], bytes=len(c['text'].encode())) for c in chunks if len(c['text'].encode())>1800],
                  suspicious_character_passages=[c['id'] for c in chunks if any(0xe000<=ord(x)<=0xf8ff or x=='\ufffd' for x in c['text'])],
                  extraction=pymupdf.VersionBind, page_audit=audit,
                  verified_repairs=["AFH PDF page 389: Wingdings-Regular U+F0A7 mapped to square bullet U+25AA; rendered page checked"],
                  unresolved_source_defects=["AFH PDF page 169: two PMingLiU U+F020 boxes visibly present in original; preserved, not interpreted"],
                  limitations=["Paragraph-block preparation; full semantic region audit pending", "No OCR or diagram interpretation", "Cross-page procedures and complex tables may require several passages", "Original PDF page numbers, not printed folios", "No answer-accuracy or safety certification"])
    (directory / 'BUILD_REPORT.json').write_bytes(encode(report))
    (directory / 'SHA256SUMS').write_text(f"{report['sha256']}  {output.name}\n")
    print(name, 'documents',len(sources),'pages',len(audit),'chunks',len(chunks),'bytes',report['bytes'],'oversized',len(report['oversized_passages']),'suspicious',len(report['suspicious_character_passages']))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-only', action='store_true', help='Build only the unrestricted AFH source')
    build(parser.parse_args().public_only)
