import pytest

from aggregate import (
    clean_description,
    detect_vertical_and_description,
    github_anchor_slug,
    normalize_title,
)


class TestCleanDescription:
    def test_strips_http_urls(self):
        raw = "Check out https://example.com/podcast for more info"
        assert clean_description(raw) == "Check out for more info"

    def test_strips_www_fragments(self):
        raw = "Visit www.example.com today"
        assert clean_description(raw) == "Visit today"

    def test_strips_domain_names(self):
        raw = "Listen on spotify.com/show/123 or example.io"
        assert clean_description(raw) == "Listen on or"

    def test_collapses_double_spaces(self):
        raw = "Too   many    spaces here"
        assert clean_description(raw) == "Too many spaces here"

    def test_collapses_spaces_left_by_url_removal(self):
        raw = "Before https://example.com after"
        assert clean_description(raw) == "Before after"

    def test_escapes_pipe_characters(self):
        assert clean_description("foo | bar") == "foo &#124; bar"

    def test_normalizes_newlines(self):
        assert clean_description("line one\nline two") == "line one line two"


class TestDetectVerticalAndDescription:
    def test_default_vertical_without_tag(self):
        vertical, desc = detect_vertical_and_description("A plain podcast description")
        assert vertical == "Software Engineering & Development"
        assert desc == "A plain podcast description"

    def test_gtm_tag_stays_uppercase(self):
        vertical, desc = detect_vertical_and_description("**[GTM]** Growth marketing tips")
        assert vertical == "GTM"
        assert desc == "Growth marketing tips"

    def test_gtm_tag_case_insensitive(self):
        vertical, desc = detect_vertical_and_description("**[gtm]** Growth marketing tips")
        assert vertical == "GTM"
        assert desc == "Growth marketing tips"

    @pytest.mark.parametrize(
        "tag",
        [
            "Software Engineering & General Tech",
            "software engineering and general tech",
        ],
    )
    def test_software_engineering_general_tech_maps_to_development(self, tag):
        vertical, desc = detect_vertical_and_description(f"**[{tag}]** Backend topics")
        assert vertical == "Software Engineering & Development"
        assert desc == "Backend topics"

    def test_unknown_tag_is_title_cased(self):
        vertical, desc = detect_vertical_and_description("**[cloud computing]** AWS deep dives")
        assert vertical == "Cloud Computing"
        assert desc == "AWS deep dives"

    def test_tag_prefix_is_stripped_from_description(self):
        vertical, desc = detect_vertical_and_description("**[DevOps]** CI/CD best practices")
        assert vertical == "Devops"
        assert desc == "CI/CD best practices"


class TestGithubAnchorSlug:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("Software Engineering & Development", "software-engineering--development"),
            ("GTM", "gtm"),
            ("Cloud Computing", "cloud-computing"),
            ("AI & Machine Learning", "ai--machine-learning"),
        ],
    )
    def test_generates_github_compatible_anchors(self, name, expected):
        assert github_anchor_slug(name) == expected


class TestNormalizeTitle:
    def test_collapses_punctuation_and_case(self):
        assert normalize_title("Syntax.fm") == normalize_title("Syntax.Fm")
        assert normalize_title("Syntax fm ") == normalize_title("Syntax.fm")
