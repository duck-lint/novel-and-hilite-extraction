from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .stage1 import CliError, run_stage1_visual_extract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m novel_and_hilite_extraction",
        description="Local proof CLI for stage-1 visual extraction evidence.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    stage1_parser = subparsers.add_parser(
        "stage1-visual-extract",
        help="Rasterize selected PDF pages and retain raw OCR evidence.",
    )
    stage1_parser.add_argument("--pdf-input", required=True, help="Source PDF path.")
    stage1_parser.add_argument(
        "--page-range",
        required=True,
        help="Selected PDF pages, for example 20-28 or 20,24,28.",
    )
    stage1_parser.add_argument(
        "--output-root",
        required=True,
        help="Directory that will receive the run-scoped output tree.",
    )
    stage1_parser.add_argument(
        "--run-label",
        required=True,
        help="Run-scoped folder name beneath the output root.",
    )
    stage1_parser.add_argument(
        "--scan-layout",
        required=True,
        help="Operator-declared scan layout label retained in manifests.",
    )
    stage1_parser.add_argument(
        "--spread-handling",
        choices=("auto", "keep-whole", "split-halves"),
        default="auto",
        help=(
            "How to derive OCR surfaces from each rasterized PDF page. "
            "'auto' maps two-page-spreads to split-halves and other layouts to keep-whole."
        ),
    )
    stage1_parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Rasterization DPI for PDF-to-PNG prep evidence.",
    )
    stage1_parser.add_argument(
        "--outer-crop-px",
        type=int,
        default=0,
        help="Pixels cropped from the outer edge of each derived surface.",
    )
    stage1_parser.add_argument(
        "--gutter-crop-px",
        type=int,
        default=0,
        help="Pixels cropped from the gutter edge of each derived surface when splitting spreads.",
    )
    stage1_parser.add_argument(
        "--top-crop-px",
        type=int,
        default=0,
        help="Pixels cropped from the top edge of each derived surface.",
    )
    stage1_parser.add_argument(
        "--bottom-crop-px",
        type=int,
        default=0,
        help="Pixels cropped from the bottom edge of each derived surface.",
    )
    stage1_parser.add_argument(
        "--tesseract-cmd",
        help="Explicit Tesseract executable path or command name.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "stage1-visual-extract":
        parser.error(f"unsupported command: {args.command}")

    if args.dpi <= 0:
        parser.error("--dpi must be a positive integer")

    for flag_name in (
        "outer_crop_px",
        "gutter_crop_px",
        "top_crop_px",
        "bottom_crop_px",
    ):
        if getattr(args, flag_name) < 0:
            parser.error(f"--{flag_name.replace('_', '-')} must be zero or greater")

    try:
        result = run_stage1_visual_extract(
            pdf_input=Path(args.pdf_input),
            page_range_spec=args.page_range,
            output_root=Path(args.output_root),
            run_label=args.run_label,
            scan_layout=args.scan_layout,
            spread_handling=args.spread_handling,
            dpi=args.dpi,
            outer_crop_px=args.outer_crop_px,
            gutter_crop_px=args.gutter_crop_px,
            top_crop_px=args.top_crop_px,
            bottom_crop_px=args.bottom_crop_px,
            tesseract_cmd=args.tesseract_cmd,
        )
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
