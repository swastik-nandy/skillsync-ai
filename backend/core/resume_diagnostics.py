import re
from pathlib import Path
from statistics import median

import pymupdf

from core.schemas import (
    ParsabilityBreakdown,
    ResumeDiagnosticsReport,
    StructureBreakdown,
)


# --------------- CONFIG ---------------

MIN_PAGE_TEXT_CHARS = 20

SECTION_ALIASES = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
    },
    "education": {
        "education",
        "academic background",
        "academic qualifications",
    },
    "skills": {
        "skills",
        "technical skills",
        "core skills",
        "technologies",
        "technical expertise",
    },
    "projects": {
        "projects",
        "personal projects",
        "professional projects",
        "selected projects",
    },
    "certifications": {
        "certifications",
        "certification",
        "licenses",
        "licenses and certifications",
    },
}


# --------------- BASIC HELPERS ---------------

def _clamp(
    value: int,
    minimum: int,
    maximum: int,
) -> int:
    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _clean_text(
    text: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _normalize_heading(
    text: str,
) -> str:
    text = text.strip().lower()

    text = re.sub(
        r"[^a-z0-9+#./& -]",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip(
        " :-|"
    )


# --------------- SECTIONS ---------------

def _detect_sections(
    text: str,
) -> list[str]:
    lines = [
        _normalize_heading(line)
        for line in text.splitlines()
        if line.strip()
    ]

    detected = []

    for section, aliases in SECTION_ALIASES.items():
        for line in lines:
            if (
                1 <= len(line) <= 45
                and line in aliases
            ):
                detected.append(
                    section
                )
                break

    return detected


# --------------- FONT ANALYSIS ---------------

def _normalize_font_family(
    font_name: str,
) -> str:
    font_name = font_name.split(
        "+"
    )[-1]

    font_name = re.sub(
        r"(?i)[-_ ]?(bold|italic|oblique|semibold|medium|regular|light)$",
        "",
        font_name,
    )

    return (
        font_name.strip()
        or "unknown"
    )


def _collect_fonts(
    page: pymupdf.Page,
) -> tuple[
    set[str],
    set[float],
    list[float],
]:
    families = set()
    sizes = set()
    all_sizes = []

    page_dict = page.get_text(
        "dict"
    )

    for block in page_dict.get(
        "blocks",
        [],
    ):
        if block.get("type") != 0:
            continue

        for line in block.get(
            "lines",
            [],
        ):
            for span in line.get(
                "spans",
                [],
            ):
                span_text = span.get(
                    "text",
                    "",
                ).strip()

                if not span_text:
                    continue

                family = (
                    _normalize_font_family(
                        span.get(
                            "font",
                            "unknown",
                        )
                    )
                )

                size = round(
                    float(
                        span.get(
                            "size",
                            0,
                        )
                    )
                    * 2
                ) / 2

                families.add(
                    family
                )

                if size > 0:
                    sizes.add(
                        size
                    )
                    all_sizes.append(
                        size
                    )

    return (
        families,
        sizes,
        all_sizes,
    )


# --------------- BLOCK ANALYSIS ---------------

def _meaningful_blocks(
    page: pymupdf.Page,
) -> list[dict]:
    blocks = []

    for raw_block in page.get_text(
        "blocks"
    ):
        text = _clean_text(
            raw_block[4]
        )

        if len(text) < 12:
            continue

        blocks.append(
            {
                "x0": float(
                    raw_block[0]
                ),
                "y0": float(
                    raw_block[1]
                ),
                "x1": float(
                    raw_block[2]
                ),
                "y1": float(
                    raw_block[3]
                ),
                "text": text,
            }
        )

    return blocks


def _vertical_overlap_ratio(
    first: dict,
    second: dict,
) -> float:
    overlap = max(
        0.0,
        min(
            first["y1"],
            second["y1"],
        )
        - max(
            first["y0"],
            second["y0"],
        ),
    )

    first_height = max(
        first["y1"]
        - first["y0"],
        1.0,
    )

    second_height = max(
        second["y1"]
        - second["y0"],
        1.0,
    )

    return overlap / min(
        first_height,
        second_height,
    )


def _area_overlap_ratio(
    first: dict,
    second: dict,
) -> float:
    overlap_width = max(
        0.0,
        min(
            first["x1"],
            second["x1"],
        )
        - max(
            first["x0"],
            second["x0"],
        ),
    )

    overlap_height = max(
        0.0,
        min(
            first["y1"],
            second["y1"],
        )
        - max(
            first["y0"],
            second["y0"],
        ),
    )

    overlap_area = (
        overlap_width
        * overlap_height
    )

    first_area = max(
        (
            first["x1"]
            - first["x0"]
        )
        * (
            first["y1"]
            - first["y0"]
        ),
        1.0,
    )

    second_area = max(
        (
            second["x1"]
            - second["x0"]
        )
        * (
            second["y1"]
            - second["y0"]
        ),
        1.0,
    )

    return overlap_area / min(
        first_area,
        second_area,
    )


def _page_column_analysis(
    page: pymupdf.Page,
    blocks: list[dict],
) -> tuple[
    int,
    bool,
    float,
    float,
]:
    if not blocks:
        return (
            1,
            False,
            0.0,
            0.0,
        )

    page_width = float(
        page.rect.width
    )

    zone_counts = [
        0,
        0,
        0,
    ]

    full_width_blocks = 0

    for block in blocks:
        width = (
            block["x1"]
            - block["x0"]
        )

        if width >= (
            page_width
            * 0.72
        ):
            full_width_blocks += 1
            continue

        center = (
            block["x0"]
            + block["x1"]
        ) / 2

        zone = min(
            int(
                center
                / page_width
                * 3
            ),
            2,
        )

        zone_counts[zone] += 1

    populated_zones = sum(
        count >= 2
        for count in zone_counts
    )

    if populated_zones >= 3:
        columns = 3
    elif populated_zones >= 2:
        columns = 2
    else:
        columns = 1

    parallel_blocks = set()
    overlapping_blocks = set()

    for first_index in range(
        len(blocks)
    ):
        for second_index in range(
            first_index + 1,
            len(blocks),
        ):
            first = blocks[
                first_index
            ]

            second = blocks[
                second_index
            ]

            vertical_overlap = (
                _vertical_overlap_ratio(
                    first,
                    second,
                )
            )

            horizontal_gap = max(
                second["x0"]
                - first["x1"],
                first["x0"]
                - second["x1"],
                0.0,
            )

            if (
                vertical_overlap >= 0.45
                and horizontal_gap
                >= page_width * 0.025
            ):
                parallel_blocks.add(
                    first_index
                )

                parallel_blocks.add(
                    second_index
                )

            area_overlap = (
                _area_overlap_ratio(
                    first,
                    second,
                )
            )

            if area_overlap >= 0.12:
                overlapping_blocks.add(
                    first_index
                )

                overlapping_blocks.add(
                    second_index
                )

    block_count = max(
        len(blocks),
        1,
    )

    parallel_ratio = (
        len(parallel_blocks)
        / block_count
    )

    overlap_ratio = (
        len(overlapping_blocks)
        / block_count
    )

    mixed_layout = (
        columns > 1
        and full_width_blocks > 0
    )

    return (
        columns,
        mixed_layout,
        parallel_ratio,
        overlap_ratio,
    )


# --------------- ORIENTATION ---------------

def _orientation_stats(
    page: pymupdf.Page,
) -> tuple[
    int,
    int,
]:
    horizontal_chars = 0
    non_horizontal_chars = 0

    page_dict = page.get_text(
        "dict"
    )

    for block in page_dict.get(
        "blocks",
        [],
    ):
        if block.get("type") != 0:
            continue

        for line in block.get(
            "lines",
            [],
        ):
            direction = line.get(
                "dir",
                (
                    1.0,
                    0.0,
                ),
            )

            dx = float(
                direction[0]
            )

            dy = float(
                direction[1]
            )

            char_count = sum(
                len(
                    span.get(
                        "text",
                        "",
                    )
                )
                for span
                in line.get(
                    "spans",
                    [],
                )
            )

            horizontal = (
                dx >= 0.98
                and abs(dy) <= 0.08
            )

            if horizontal:
                horizontal_chars += (
                    char_count
                )
            else:
                non_horizontal_chars += (
                    char_count
                )

    return (
        horizontal_chars,
        non_horizontal_chars,
    )


# --------------- TEXT INTEGRITY ---------------

def _suspicious_character_count(
    text: str,
) -> int:
    suspicious = 0

    for char in text:
        code = ord(
            char
        )

        if char == "\ufffd":
            suspicious += 1

        elif (
            code < 32
            and char
            not in {
                "\n",
                "\r",
                "\t",
            }
        ):
            suspicious += 1

    return suspicious


# --------------- PARSABILITY SCORING ---------------

def _integrity_points(
    percentage: float,
) -> int:
    if percentage <= 0.10:
        return 15

    if percentage <= 0.50:
        return 13

    if percentage <= 1.00:
        return 10

    if percentage <= 3.00:
        return 6

    return 2


def _fragmentation_points(
    blocks_per_100_words: float,
) -> tuple[
    int,
    str,
]:
    if blocks_per_100_words <= 2.5:
        return (
            15,
            "low",
        )

    if blocks_per_100_words <= 4.0:
        return (
            13,
            "low",
        )

    if blocks_per_100_words <= 6.0:
        return (
            10,
            "medium",
        )

    if blocks_per_100_words <= 9.0:
        return (
            6,
            "high",
        )

    return (
        2,
        "very_high",
    )


def _orientation_points(
    percentage: float,
) -> int:
    if percentage <= 1:
        return 10

    if percentage <= 5:
        return 8

    if percentage <= 15:
        return 5

    if percentage <= 30:
        return 2

    return 0


def _reading_order_points(
    multi_column_ratio: float,
    parallel_ratio: float,
    overlap_ratio: float,
    mixed_layout_ratio: float,
) -> int:
    penalty = (
        multi_column_ratio
        * 5
        + parallel_ratio
        * 5
        + overlap_ratio
        * 6
        + mixed_layout_ratio
        * 4
    )

    return _clamp(
        round(
            20 - penalty
        ),
        0,
        20,
    )


def _reading_order_label(
    points: int,
) -> str:
    if points >= 17:
        return "low"

    if points >= 12:
        return "medium"

    return "high"


# --------------- STRUCTURE SCORING ---------------

def _section_score(
    sections: list[str],
) -> int:
    section_set = set(
        sections
    )

    score = 0

    for section in (
        "experience",
        "education",
        "skills",
    ):
        if section in section_set:
            score += 9

    optional_count = sum(
        section in section_set
        for section in (
            "summary",
            "projects",
            "certifications",
        )
    )

    if optional_count >= 1:
        score += 4

    if optional_count >= 2:
        score += 4

    return min(
        score,
        35,
    )


def _layout_score(
    complexity: str,
) -> int:
    return {
        "low": 25,
        "medium": 18,
        "high": 10,
    }[complexity]


def _font_score(
    family_count: int,
    size_count: int,
) -> int:
    if (
        family_count <= 2
        and size_count <= 6
    ):
        return 15

    if (
        family_count <= 3
        and size_count <= 8
    ):
        return 12

    if (
        family_count <= 4
        and size_count <= 10
    ):
        return 8

    return 4


def _density_score(
    average_words_per_page: float,
) -> int:
    if (
        250
        <= average_words_per_page
        <= 750
    ):
        return 10

    if (
        150
        <= average_words_per_page
        <= 900
    ):
        return 7

    if average_words_per_page > 0:
        return 4

    return 0


# --------------- LAYOUT CLASSIFICATION ---------------

def _layout_complexity(
    max_columns: int,
    mixed_layout_pages: int,
    total_pages: int,
    overlap_percentage: float,
    average_blocks: float,
) -> str:
    if (
        max_columns == 1
        and overlap_percentage < 5
        and average_blocks <= 18
    ):
        return "low"

    if (
        max_columns <= 2
        and overlap_percentage < 15
        and average_blocks <= 30
        and mixed_layout_pages
        <= max(
            total_pages // 2,
            1,
        )
    ):
        return "medium"

    return "high"


# --------------- MAIN ANALYSIS ---------------

def inspect_resume_diagnostics(
    file_bytes: bytes,
    filename: str,
) -> ResumeDiagnosticsReport:
    extension = Path(
        filename
    ).suffix.lower()

    if extension != ".pdf":
        raise ValueError(
            "Resume diagnostics currently supports PDF files only."
        )

    if not file_bytes:
        raise ValueError(
            "Uploaded resume is empty."
        )

    try:
        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf",
        )
    except Exception as error:
        raise ValueError(
            "Unable to open the uploaded PDF."
        ) from error

    with document:
        total_pages = len(
            document
        )

        parsed_pages = 0
        scanned_pages = 0

        characters_extracted = 0
        words_extracted = 0

        image_count = 0
        link_count = 0

        block_counts = []
        total_blocks = 0

        max_columns = 1
        multi_column_pages = 0
        mixed_layout_pages = 0

        parallel_ratios = []
        overlap_ratios = []

        horizontal_chars = 0
        non_horizontal_chars = 0

        suspicious_characters = 0

        font_families = set()
        font_sizes = set()
        all_font_sizes = []

        page_sizes = []

        document_text_parts = []

        for page in document:
            raw_text = page.get_text(
                "text"
            )

            cleaned_text = _clean_text(
                raw_text
            )

            document_text_parts.append(
                raw_text
            )

            character_count = len(
                cleaned_text
            )

            word_count = len(
                cleaned_text.split()
            )

            characters_extracted += (
                character_count
            )

            words_extracted += (
                word_count
            )

            suspicious_characters += (
                _suspicious_character_count(
                    raw_text
                )
            )

            if (
                character_count
                >= MIN_PAGE_TEXT_CHARS
            ):
                parsed_pages += 1

            page_images = (
                page.get_images(
                    full=True
                )
            )

            image_count += len(
                page_images
            )

            if (
                character_count
                < MIN_PAGE_TEXT_CHARS
                and page_images
            ):
                scanned_pages += 1

            link_count += len(
                page.get_links()
            )

            blocks = (
                _meaningful_blocks(
                    page
                )
            )

            block_count = len(
                blocks
            )

            total_blocks += (
                block_count
            )

            block_counts.append(
                block_count
            )

            (
                columns,
                mixed_layout,
                parallel_ratio,
                overlap_ratio,
            ) = _page_column_analysis(
                page,
                blocks,
            )

            max_columns = max(
                max_columns,
                columns,
            )

            if columns > 1:
                multi_column_pages += 1

            if mixed_layout:
                mixed_layout_pages += 1

            parallel_ratios.append(
                parallel_ratio
            )

            overlap_ratios.append(
                overlap_ratio
            )

            (
                page_horizontal_chars,
                page_non_horizontal_chars,
            ) = _orientation_stats(
                page
            )

            horizontal_chars += (
                page_horizontal_chars
            )

            non_horizontal_chars += (
                page_non_horizontal_chars
            )

            (
                page_fonts,
                page_font_sizes,
                page_all_font_sizes,
            ) = _collect_fonts(
                page
            )

            font_families.update(
                page_fonts
            )

            font_sizes.update(
                page_font_sizes
            )

            all_font_sizes.extend(
                page_all_font_sizes
            )

            page_sizes.append(
                (
                    round(
                        page.rect.width,
                        1,
                    ),
                    round(
                        page.rect.height,
                        1,
                    ),
                )
            )

        parse_percentage = (
            round(
                parsed_pages
                / total_pages
                * 100
            )
            if total_pages
            else 0
        )

        full_text = "\n".join(
            document_text_parts
        )

        sections = _detect_sections(
            full_text
        )

        average_words_per_page = (
            words_extracted
            / total_pages
            if total_pages
            else 0
        )

        average_blocks = (
            sum(
                block_counts
            )
            / len(
                block_counts
            )
            if block_counts
            else 0
        )

        blocks_per_100_words = (
            total_blocks
            / words_extracted
            * 100
            if words_extracted
            else 0
        )

        total_oriented_chars = (
            horizontal_chars
            + non_horizontal_chars
        )

        non_horizontal_percentage = (
            non_horizontal_chars
            / total_oriented_chars
            * 100
            if total_oriented_chars
            else 0
        )

        suspicious_percentage = (
            suspicious_characters
            / max(
                characters_extracted,
                1,
            )
            * 100
        )

        average_parallel_ratio = (
            sum(
                parallel_ratios
            )
            / len(
                parallel_ratios
            )
            if parallel_ratios
            else 0
        )

        average_overlap_ratio = (
            sum(
                overlap_ratios
            )
            / len(
                overlap_ratios
            )
            if overlap_ratios
            else 0
        )

        overlap_percentage = (
            average_overlap_ratio
            * 100
        )

        multi_column_ratio = (
            multi_column_pages
            / total_pages
            if total_pages
            else 0
        )

        mixed_layout_ratio = (
            mixed_layout_pages
            / total_pages
            if total_pages
            else 0
        )

        extraction_points = round(
            parse_percentage
            / 100
            * 30
        )

        integrity_points = (
            _integrity_points(
                suspicious_percentage
            )
        )

        reading_points = (
            _reading_order_points(
                multi_column_ratio,
                average_parallel_ratio,
                average_overlap_ratio,
                mixed_layout_ratio,
            )
        )

        (
            fragmentation_points,
            fragmentation_label,
        ) = _fragmentation_points(
            blocks_per_100_words
        )

        orientation_points = (
            _orientation_points(
                non_horizontal_percentage
            )
        )

        ocr_points = round(
            (
                1
                - (
                    scanned_pages
                    / total_pages
                    if total_pages
                    else 1
                )
            )
            * 10
        )

        ocr_points = _clamp(
            ocr_points,
            0,
            10,
        )

        parsability_breakdown = (
            ParsabilityBreakdown(
                extraction_coverage=extraction_points,
                text_integrity=integrity_points,
                reading_order=reading_points,
                fragmentation=fragmentation_points,
                orientation=orientation_points,
                ocr_independence=ocr_points,
            )
        )

        technical_parsability = sum(
            (
                extraction_points,
                integrity_points,
                reading_points,
                fragmentation_points,
                orientation_points,
                ocr_points,
            )
        )

        reading_order_complexity = (
            _reading_order_label(
                reading_points
            )
        )

        layout = (
            _layout_complexity(
                max_columns,
                mixed_layout_pages,
                total_pages,
                overlap_percentage,
                average_blocks,
            )
        )

        page_sizes_consistent = (
            len(
                set(
                    page_sizes
                )
            )
            <= 1
        )

        section_points = (
            _section_score(
                sections
            )
        )

        layout_points = (
            _layout_score(
                layout
            )
        )

        font_points = (
            _font_score(
                len(
                    font_families
                ),
                len(
                    font_sizes
                ),
            )
        )

        page_points = (
            10
            if page_sizes_consistent
            else 5
        )

        density_points = (
            _density_score(
                average_words_per_page
            )
        )

        structure_parse_points = (
            round(
                parse_percentage
                / 100
                * 5
            )
        )

        structure_breakdown = (
            StructureBreakdown(
                section_structure=section_points,
                layout=layout_points,
                font_consistency=font_points,
                page_consistency=page_points,
                text_density=density_points,
                parsability=structure_parse_points,
            )
        )

        structure_friendliness = sum(
            (
                section_points,
                layout_points,
                font_points,
                page_points,
                density_points,
                structure_parse_points,
            )
        )

        deterministic_health_index = round(
            technical_parsability * 0.60
            + structure_friendliness * 0.40
        )

        if deterministic_health_index >= 90:
            deterministic_health_label = "excellent"
        elif deterministic_health_index >= 80:
            deterministic_health_label = "strong"
        elif deterministic_health_index >= 70:
            deterministic_health_label = "good"
        elif deterministic_health_index >= 60:
            deterministic_health_label = "fair"
        else:
            deterministic_health_label = "needs_attention"

        observations = []

        observations.append(
            (
                f"Text extraction coverage is "
                f"{parse_percentage}% "
                f"({parsed_pages}/{total_pages} pages)."
            )
        )

        observations.append(
            (
                f"Technical parsability is "
                f"{technical_parsability}/100."
            )
        )

        if scanned_pages:
            observations.append(
                (
                    f"{scanned_pages} page(s) "
                    "appear image-based and may require OCR."
                )
            )
        else:
            observations.append(
                "No OCR-dependent pages were detected."
            )

        if max_columns > 1:
            observations.append(
                (
                    f"Up to {max_columns} text columns "
                    "were detected."
                )
            )
        else:
            observations.append(
                "No multi-column text structure was detected."
            )

        if mixed_layout_pages:
            observations.append(
                (
                    f"{mixed_layout_pages} page(s) contain "
                    "mixed full-width and columnar sections."
                )
            )

        observations.append(
            (
                "Reading-order complexity is "
                f"{reading_order_complexity}."
            )
        )

        observations.append(
            (
                f"Text fragmentation is "
                f"{fragmentation_label} at "
                f"{blocks_per_100_words:.2f} "
                "blocks per 100 words."
            )
        )

        observations.append(
            (
                f"Non-horizontal text accounts for "
                f"{non_horizontal_percentage:.2f}% "
                "of extracted text."
            )
        )

        observations.append(
            (
                f"{overlap_percentage:.2f}% of text blocks "
                "participate in meaningful geometric overlaps."
            )
        )

        observations.append(
            (
                f"Suspicious extracted characters account for "
                f"{suspicious_percentage:.3f}% of text."
            )
        )

        if sections:
            observations.append(
                (
                    "Detected resume sections: "
                    + ", ".join(
                        sections
                    )
                    + "."
                )
            )

        body_font_size = (
            round(
                median(
                    all_font_sizes
                ),
                1,
            )
            if all_font_sizes
            else None
        )

        return ResumeDiagnosticsReport(
            filename=filename,
            file_type="pdf",
            file_size_bytes=len(
                file_bytes
            ),

            total_pages=total_pages,
            parsed_pages=parsed_pages,
            scanned_pages=scanned_pages,

            parse_percentage=parse_percentage,

            text_layer=(
                parsed_pages > 0
            ),

            ocr_required=(
                scanned_pages > 0
            ),

            characters_extracted=characters_extracted,
            words_extracted=words_extracted,

            average_words_per_page=round(
                average_words_per_page,
                1,
            ),

            links=link_count,
            embedded_images=image_count,

            font_families=sorted(
                font_families
            ),

            font_sizes=sorted(
                font_sizes
            ),

            body_font_size=body_font_size,

            page_sizes_consistent=page_sizes_consistent,

            layout_complexity=layout,
            multi_column_pages=multi_column_pages,

            sections_detected=sections,

            structure_friendliness=structure_friendliness,

            technical_parsability=technical_parsability,

            deterministic_health_index=deterministic_health_index,
            deterministic_health_label=deterministic_health_label,

            parsability_breakdown=parsability_breakdown,

            reading_order_complexity=reading_order_complexity,

            fragmentation=fragmentation_label,

            blocks_per_100_words=round(
                blocks_per_100_words,
                2,
            ),

            non_horizontal_text_percentage=round(
                non_horizontal_percentage,
                2,
            ),

            overlapping_block_percentage=round(
                overlap_percentage,
                2,
            ),

            suspicious_character_percentage=round(
                suspicious_percentage,
                3,
            ),

            max_columns_detected=max_columns,

            mixed_layout_pages=mixed_layout_pages,

            structure_breakdown=structure_breakdown,

            observations=observations,
        )
