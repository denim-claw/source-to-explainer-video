"""Build the book-section explainer in Korean and English.

    python example-concept/pipeline.py              both languages
    python example-concept/pipeline.py --lang ko    one language

Needs GEMINI_API_KEY only for scenes without matching cached speech.
"""
import argparse
import hashlib
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'example'))
sys.path.insert(0, str(ROOT))

import plan  # noqa: E402
import variant  # noqa: E402


def verify_source():
    """Fetch the pinned section and fail if it is not byte-identical to the planned source."""
    cache = ROOT / 'build' / 'source.html'
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        cache.write_bytes(urllib.request.urlopen(plan.SOURCE['url'], timeout=60).read())
    got = hashlib.sha256(cache.read_bytes()).hexdigest()
    assert got == plan.SOURCE['html_sha256'], f'source changed: {got}'
    return dict(plan.SOURCE, verified_sha256=got, fetched_copy='build/source.html (not packaged)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['ko', 'en'], action='append')
    args = parser.parse_args()
    record = verify_source()
    for lang in args.lang or ['ko', 'en']:
        variant.build_variant(ROOT, lang, plan.PLAN, plan.CONFIG, record, plan.REVIEW,
                              plan.VOICE, plan.STYLE, gif_scene=5)


if __name__ == '__main__':
    main()
