"""Command-line interface."""

from __future__ import annotations

from pathlib import Path

import click
import yaml

from .detector import HLLMapDetector
from .downloader import download_youtube_video
from .processor import VideoMapProcessor

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATES = PACKAGE_ROOT / "templates"
DEFAULT_OUTPUT = PACKAGE_ROOT / "output"
DEFAULT_CACHE = PACKAGE_ROOT / ".cache"


def _load_config(config_path: Path | None) -> dict:
    if config_path is None:
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _resolve_path(value: str | Path, base: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


@click.command()
@click.argument("source")
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Optional YAML config file.",
)
@click.option("--output", "output_dir", type=click.Path(path_type=Path), default=str(DEFAULT_OUTPUT))
@click.option("--templates", "templates_dir", type=click.Path(path_type=Path), default=str(DEFAULT_TEMPLATES))
@click.option("--speed", "speed_factor", type=int, default=None, help="Frame skip factor (higher = faster scan).")
@click.option("--cache-dir", type=click.Path(path_type=Path), default=str(DEFAULT_CACHE))
@click.option("--keep-download/--no-keep-download", default=True, show_default=True)
@click.option("--debug", is_flag=True, help="Print each saved screenshot path.")
def main(
    source: str,
    config_path: Path | None,
    output_dir: Path,
    templates_dir: Path,
    speed_factor: int | None,
    cache_dir: Path,
    keep_download: bool,
    debug: bool,
) -> None:
    """Capture HLL map screenshots from a YouTube URL or local video file.

    Examples:

      python -m hll_map_capture "https://www.youtube.com/watch?v=VIDEO_ID"

      python -m hll_map_capture ./my_hll_stream.mp4 --speed 8
    """
    config = _load_config(config_path)
    detection_cfg = config.get("detection", {})
    processing_cfg = config.get("processing", {})
    crop_cfg = config.get("map_crop", {})
    output_cfg = config.get("output", {})

    resolved_output = _resolve_path(output_cfg.get("directory", output_dir), PACKAGE_ROOT)
    resolved_templates = _resolve_path(templates_dir, PACKAGE_ROOT)
    resolved_cache = _resolve_path(cache_dir, PACKAGE_ROOT)

    detector = HLLMapDetector(
        templates_dir=resolved_templates,
        template_height=int(detection_cfg.get("template_resolution", 1080)),
        num_features=int(detection_cfg.get("num_features", 500)),
        min_good_matches=int(detection_cfg.get("min_good_matches", 12)),
    )

    source_path = Path(source)
    downloaded_path: Path | None = None
    if source_path.exists():
        video_path = source_path
        video_stem = source_path.stem
    else:
        click.echo("Downloading YouTube video...")
        downloaded_path = download_youtube_video(source, resolved_cache)
        video_path = downloaded_path
        video_stem = downloaded_path.stem
        click.echo(f"Downloaded: {video_path}")

    processor = VideoMapProcessor(
        detector,
        resolved_output,
        speed_factor=speed_factor or int(processing_cfg.get("speed_factor", 4)),
        min_capture_interval_sec=float(processing_cfg.get("min_capture_interval_sec", 2.0)),
        closed_frames_required=int(processing_cfg.get("closed_frames_required", 3)),
        map_crop=crop_cfg or None,
        image_format=str(output_cfg.get("image_format", "png")),
        video_stem=video_stem,
    )

    click.echo(f"Scanning {video_path.name} at {processor.speed_factor}x frame skip...")
    stats = processor.process(video_path)

    click.echo("")
    click.echo(f"Frames scanned: {stats.frames_scanned}")
    click.echo(f"Map-open frames: {stats.map_open_frames}")
    click.echo(f"Map screenshots saved: {len(stats.captures)}")
    click.echo(f"Output folder: {resolved_output}")

    if debug:
        for event in stats.captures:
            click.echo(
                f"  {event.output_path.name} @ {event.timestamp_sec:.1f}s "
                f"({event.good_matches} matches)"
            )

    if downloaded_path is not None and not keep_download:
        downloaded_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
