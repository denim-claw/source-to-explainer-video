#!/usr/bin/env python3
"""Verify bundled atlas hashes/dimensions/licenses; no downloads or credentials."""
# SPDX-License-Identifier: MIT
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'assets/hybrid-3d/textures'

def inspect_png(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{path.name}: not PNG'
    offset, dimensions, ended = 8, None, False
    while offset < len(data):
        assert offset + 12 <= len(data), f'{path.name}: truncated chunk'
        length = struct.unpack('>I', data[offset:offset+4])[0]
        kind = data[offset+4:offset+8]
        start, end = offset+8, offset+8+length
        assert end+4 <= len(data), f'{path.name}: truncated chunk payload'
        assert zlib.crc32(data[offset+4:end]) & 0xffffffff == struct.unpack('>I', data[end:end+4])[0], f'{path.name}: PNG CRC failure'
        if kind == b'IHDR':
            assert length == 13
            width,height,depth,color = struct.unpack('>IIBB', data[start:start+10])
            assert depth == 8 and color == 6, f'{path.name}: expected RGBA8'
            dimensions = (width,height)
        offset = end+4
        if kind == b'IEND':
            assert length == 0 and offset == len(data)
            ended = True
            break
    assert ended and dimensions, f'{path.name}: incomplete PNG'
    return data,dimensions

def main():
    manifest = json.loads((TEXTURES/'manifest.json').read_text())
    assert manifest['license'] == 'CC0-1.0'
    assert 'CC0 license' in manifest['evidence_quote']
    assert (TEXTURES/'CC0-1.0.txt').is_file()
    assert 'Statement of Purpose' in (TEXTURES/'CC0-1.0.txt').read_text()
    assets = manifest['textures']
    assert len(assets) == 4 and {a['id'] for a in assets} == {'Flame02','Flame03','WispySmoke01','WispySmoke02'}
    assert {a['file'] for a in assets} == {p.name for p in TEXTURES.glob('*.png')}
    total = 0
    for asset in assets:
        name = asset['file']
        assert name == Path(name).name and name.endswith('.png'), 'unsafe asset path'
        assert asset['license'] == 'CC0-1.0'
        assert asset['source_url'] == f"https://unity3d.com/files/labs/downloads/vfx/assets01/{asset['id']}/{asset['id']}-flipbooks.zip"
        assert all(re.fullmatch('[0-9a-f]{64}',asset[k]) for k in ['sha256','tga_sha256','zip_sha256'])
        data,(width,height) = inspect_png(TEXTURES/name)
        assert hashlib.sha256(data).hexdigest() == asset['sha256'], f'{name}: hash mismatch'
        assert len(data) == asset['bytes']
        assert (width,height) == (asset['width'],asset['height'])
        assert width % asset['columns'] == height % asset['rows'] == 0
        assert asset['columns'] * asset['rows'] == asset['frames'] == 64
        total += len(data)
    print(json.dumps({'status':'pass','pngs':len(assets),'bytes':total,'checks':['SHA256','RGBA8 PNG dimensions/CRC','atlas grids','explicit CC0 provenance/notice']},indent=2))

if __name__ == '__main__':
    main()
