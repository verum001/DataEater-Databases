# Survival 0.1.0 preparation

The three original PDFs are retained unchanged and identified by SHA-256. Original PDF page numbers are used for citations; these may differ from printed page labels.

Text comes from PDF text blocks. The two-column NWSS pages are ordered by column within bands separated by full-width text blocks. Other pages follow vertical text-block order. PDF bookmarks provide navigation metadata, separate from passage text. No generated factual text, automatic translation, medical updates, OCR or diagram interpretation is included.

Complete text blocks are packed into passages with a target of 1,800 UTF-8 bytes. A larger block remains intact and is recorded as oversized rather than truncated. Cross-page procedures can require multiple passages. A source-block coverage check requires every extracted block to appear exactly once. This checks extraction coverage, not correctness of the PDF's own text layer or semantic completeness of each passage.

Rendered sample pages checked: PDF pages 2, 36 and 101 of each manual, plus AFH pages 169 and 389. AFH page 389's Wingdings square bullets were verified against the rendering and converted to Unicode square bullets. Two box characters visibly present on AFH page 169 remain unresolved and preserved.

The package uses format version 1, with manifest first, source records and passage records. Validation checks ZIP readability, unique passage IDs, valid source IDs, original page bounds, complete block coverage and all manifest SHA-256 fingerprints. A second build checks deterministic artifact bytes. These checks do not certify survival advice, diagram fidelity, complete table relationships or AI answer accuracy.

The preparation method reflects preliminary retrieval findings: source encoding and column order can affect retrieval, while complete retrieved passages can still produce incorrect model answers. No measured accuracy improvement is claimed for this collection. Further revisions should audit complete warnings, numbered procedures and table regions against original pages.
