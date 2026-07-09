from app.services.occupation_lookup import (
    get_job_zone_baseline,
    get_occupation,
    is_supervisory_occupation,
    search_occupations,
)


def test_get_occupation_known_soc_code():
    occ = get_occupation("15-1252.00")
    assert occ is not None
    assert occ.title == "Software Developers"
    assert occ.job_zone == 4


def test_get_occupation_unknown_soc_code_returns_none():
    assert get_occupation("00-0000.00") is None


def test_get_occupation_accepts_plain_soc_code_without_onet_suffix():
    occ = get_occupation("15-1252")
    assert occ is not None
    assert occ.soc_code == "15-1252.00"
    assert occ.title == "Software Developers"


def test_get_job_zone_baseline_all_five_zones_present():
    for zone in range(1, 6):
        baseline = get_job_zone_baseline(zone)
        assert baseline["experience_min_years"] < baseline["experience_max_years"]


def test_search_occupations_finds_software_titles():
    results = search_occupations("software")
    assert len(results) > 0
    assert all("software" in occ.title.lower() for occ in results)


def test_search_occupations_empty_query_returns_empty():
    assert search_occupations("") == []


def test_is_supervisory_occupation():
    assert is_supervisory_occupation("General and Operations Managers") is True
    assert is_supervisory_occupation("Software Developers") is False
