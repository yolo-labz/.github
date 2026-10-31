"""PNG metadata helpers shared by the model scripts.

Blender stamps `tEXt Date` and `tEXt RenderTime` into every PNG, and imagemagick
or rsvg-convert can add their own ancillary chunks. Those change on every run
even when the pixels are identical, which would make a byte-level determinism
contract unverifiable for no benefit. Dropping them is what lets "identical
pixels" mean "identical file".
"""

import struct

#: Chunks that carry no pixel data and vary between runs.
VOLATILE_PNG_CHUNKS = {b"tEXt", b"zTXt", b"iTXt", b"tIME", b"eXIf", b"oFFs"}


def normalise_png(path):
    """Rewrite ``path`` without its volatile metadata chunks."""
    with open(path, "rb") as handle:
        blob = handle.read()
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    kept = []
    offset = 8
    while offset < len(blob):
        length = struct.unpack(">I", blob[offset : offset + 4])[0]
        kind = blob[offset + 4 : offset + 8]
        end = offset + 12 + length
        if kind not in VOLATILE_PNG_CHUNKS:
            kept.append(blob[offset:end])
        offset = end
        if kind == b"IEND":
            break
    with open(path, "wb") as handle:
        handle.write(blob[:8] + b"".join(kept))
