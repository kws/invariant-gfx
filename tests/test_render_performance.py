import hashlib
import random
import struct
from io import BytesIO

import pytest
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact
from invariant_gfx.ops.composite import _blend_channel, _blend_layer
from PIL import Image


def test_hash_is_versioned_and_does_not_encode_png(monkeypatch):
    image = Image.new("RGBA", (3, 2), (10, 20, 30, 40))
    artifact = ImageArtifact(image)

    def forbidden(*args, **kwargs):
        raise AssertionError("Hashing must not encode PNG")

    monkeypatch.setattr(artifact, "_to_canonical_png", forbidden)
    expected = hashlib.sha256(
        b"invariant-gfx:image:rgba:v2\0"
        + (3).to_bytes(8, "big")
        + (2).to_bytes(8, "big")
        + image.tobytes()
    ).hexdigest()
    assert artifact.get_stable_hash() == expected
    assert (
        artifact.get_stable_hash()
        != ImageArtifact(
            Image.frombytes("RGBA", (2, 3), image.tobytes())
        ).get_stable_hash()
    )


def test_blob_identity_distinguishes_media_types_and_survives_storage():
    a = BlobArtifact(b"content", "image/png")
    b = BlobArtifact(b"content", "image/jpeg")
    assert a.get_stable_hash() != b.get_stable_hash()
    stream = BytesIO()
    a.to_stream(stream)
    stream.seek(0)
    assert BlobArtifact.from_stream(stream).get_stable_hash() == a.get_stable_hash()


@pytest.mark.parametrize(
    "mode", ["multiply", "screen", "overlay", "darken", "lighten", "add"]
)
def test_vectorized_blend_matches_scalar_for_pixels_and_alpha_boundaries(mode):
    rng = random.Random(42)
    base = Image.frombytes("RGBA", (256, 129), rng.randbytes(256 * 129 * 4))
    blend = Image.frombytes("RGBA", base.size, rng.randbytes(256 * 129 * 4))
    for x in range(256):
        base.putpixel((x, 0), (x, 255 - x, x, 0))
        blend.putpixel((x, 0), (255 - x, x, 127, 255))
        blend.putpixel((x, 1), (x, 0, 255, 0))
    expected = []
    for bp, sp in zip(struct.iter_unpack("4B", base.tobytes()), struct.iter_unpack("4B", blend.tobytes()), strict=True):
        if sp[3] == 0:
            expected.append(bp)
        elif sp[3] == 255 and bp[3] == 0:
            expected.append(sp)
        else:
            sa, ba = sp[3] / 255.0, bp[3] / 255.0
            color = tuple(
                round(_blend_channel(b, s, mode) * sa + b * (1 - sa))
                for b, s in zip(bp[:3], sp[:3], strict=True)
            )
            alpha = max(0, min(255, round((sa + ba * (1.0 - sa)) * 255)))
            expected.append((*color, alpha))
    original = base.tobytes(), blend.tobytes()
    result = _blend_layer(base, blend, mode)
    assert list(struct.iter_unpack("4B", result.tobytes())) == expected
    assert (base.tobytes(), blend.tobytes()) == original
