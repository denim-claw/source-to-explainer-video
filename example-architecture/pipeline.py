"""Build the QM architecture review in Korean and English.

    python example-architecture/pipeline.py              both languages
    python example-architecture/pipeline.py --lang en    one language

Source files are fetched at the pinned commit and checked against their Git blob
hashes. Needs GEMINI_API_KEY only for scenes without matching cached speech.
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

RAW = 'https://raw.githubusercontent.com/yc-software/qm/{commit}/{path}'


def git_blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def verify_source():
    """Every cited file must be byte-identical to the blob recorded in the plan."""
    files = []
    for path, blob in plan.FILES.items():
        local = ROOT / 'build' / 'source' / path
        local.parent.mkdir(parents=True, exist_ok=True)
        if not local.exists():
            local.write_bytes(urllib.request.urlopen(RAW.format(commit=plan.COMMIT, path=path), timeout=60).read())
        got = git_blob(local.read_bytes())
        assert got == blob, f'{path}: blob {got} differs from pinned {blob}'
        files.append(dict(path=path, git_blob=blob, sha256=hashlib.sha256(local.read_bytes()).hexdigest()))
    return dict(repository=plan.REPO, commit=plan.COMMIT, license='MIT (Copyright 2026 QM contributors)',
                files=files, tests_run=plan.TESTS,
                fetched_copies='build/source/ (not packaged; cite the repository instead)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['ko', 'en'], action='append')
    args = parser.parse_args()
    record = verify_source()
    for lang in args.lang or ['ko', 'en']:
        variant.build_variant(ROOT, lang, plan.PLAN, plan.CONFIG, record, plan.REVIEW,
                              plan.VOICE, plan.STYLE, gif_scene=3)


if __name__ == '__main__':
    main()
