"""Optional renderer-independent time groups, layout slots and raster QA.
No engine/default replacement; integers are decoded mono PCM sample indices.
"""
from dataclasses import dataclass, replace
from PIL import ImageChops, Image

@dataclass(frozen=True)
class Event:
    name: str
    start: int
    end: int

@dataclass(frozen=True)
class TimeGroup:
    start: int
    duration: int
    events: tuple[Event, ...]
    def __post_init__(self):
        assert self.start >= 0 and self.duration > 0
        assert len({e.name for e in self.events}) == len(self.events)
        assert all(0 <= e.start < e.end <= self.duration for e in self.events)
    def absolute(self):
        return {e.name: (self.start + e.start, self.start + e.end) for e in self.events}
    def moved(self, start):
        return replace(self, start=start)

@dataclass(frozen=True)
class Slot:
    x: float
    y: float
    width: float
    height: float
    def __post_init__(self):
        assert self.width > 0 and self.height > 0
    def child(self, x, y):
        """Normalized local motion child; parent owns layout only."""
        return self.x + x*self.width, self.y + y*self.height
    def contains(self, b):
        return self.x <= b[0] <= b[2] <= self.x+self.width and self.y <= b[1] <= b[3] <= self.y+self.height

def intersects(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])

def validate_semantics(actors, props, transfers):
    """Require explicit owners; advisor offers advice, never silently becomes lead."""
    assert all(a['role'] in {'worker','lead','advisor','solo'} for a in actors.values())
    assert all(p['owner'] in actors for p in props.values())
    for t in transfers:
        assert t['prop'] in props and t['from'] in actors and t['to'] in actors
        assert props[t['prop']]['owner'] == t['from']
        assert t['from'] != t['to'] and t['meaning']
        if actors[t['from']]['role'] == 'advisor':
            assert t['meaning'] == 'advice', 'advisor is not the decision-maker'
    return True

def composite_checked(base, layer, xy, slot, exclusion=(), later_text_boxes=()):
    """Full painted alpha bounds, not just actor anchors. Paint actors before labels."""
    assert base.mode == layer.mode == 'RGBA'
    alpha = layer.getchannel('A'); hist = alpha.histogram(); b = alpha.getbbox()
    assert b and hist[0] > 0 and sum(hist[1:255]) > 0, 'real antialiased RGBA required'
    bbox = (b[0]+xy[0], b[1]+xy[1], b[2]+xy[0], b[3]+xy[1])
    assert slot.contains(bbox), (bbox, slot)
    assert not any(intersects(bbox, e) for e in exclusion), ('painted exclusion', bbox)
    # Fail closed on opaque overpainting of earlier labels; callers can supply those
    # boxes as exclusions. Later labels are safe only when not colliding with actors.
    for e in later_text_boxes:
        local = (max(0, int(e[0]-xy[0])), max(0, int(e[1]-xy[1])),
                 min(layer.width, int(e[2]-xy[0])+1), min(layer.height, int(e[3]-xy[1])+1))
        if local[0] < local[2] and local[1] < local[3]:
            assert not alpha.crop(local).getbbox(), ('actor-label painted pixels', e)
    before = base.copy(); base.alpha_composite(layer, xy)
    region = (xy[0], xy[1], xy[0]+layer.width, xy[1]+layer.height)
    diff = ImageChops.difference(base.crop(region).convert('RGB'), before.crop(region).convert('RGB'))
    zero = alpha.point(lambda v: 255 if v == 0 else 0)
    assert not ImageChops.multiply(diff, Image.merge('RGB',(zero,zero,zero))).getbbox()
    return {'bbox': bbox, 'transparent': hist[0], 'partial': sum(hist[1:255]), 'zero_alpha_changes': 0}
