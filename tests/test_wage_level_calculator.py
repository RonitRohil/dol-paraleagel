import pytest

from app.services.wage_level_calculator import UnknownOccupationError, calculate_wage_level

SOFTWARE_DEVELOPER_SOC = "15-1252.00"  # Job Zone 4: bachelors baseline, 2-4 years experience


def test_level_i_entry_level_role():
    result = calculate_wage_level(
        soc_code=SOFTWARE_DEVELOPER_SOC,
        required_education="bachelors",
        required_experience_years=0,
        supervises_others=False,
    )
    assert result.wage_level == "Level I"
    assert result.total_points == 1


def test_level_ii_low_end_experience():
    result = calculate_wage_level(
        soc_code=SOFTWARE_DEVELOPER_SOC,
        required_education="bachelors",
        required_experience_years=3,
        supervises_others=False,
    )
    assert result.wage_level == "Level II"
    assert result.total_points == 2


def test_level_iii_high_end_experience():
    result = calculate_wage_level(
        soc_code=SOFTWARE_DEVELOPER_SOC,
        required_education="bachelors",
        required_experience_years=3.5,
        supervises_others=False,
    )
    assert result.wage_level == "Level III"
    assert result.total_points == 3


def test_level_iv_exceeds_experience_and_education_and_supervisory():
    result = calculate_wage_level(
        soc_code=SOFTWARE_DEVELOPER_SOC,
        required_education="masters",
        required_experience_years=5,
        supervises_others=True,
        special_skills=["Kubernetes", "Terraform"],
        number_supervised=3,
    )
    assert result.wage_level == "Level IV"
    # total is capped at 4 even though raw points would sum higher
    assert result.total_points == 4


def test_experience_alone_exceeding_range_caps_at_level_iv():
    result = calculate_wage_level(
        soc_code=SOFTWARE_DEVELOPER_SOC,
        required_education="bachelors",
        required_experience_years=10,
        supervises_others=False,
    )
    assert result.wage_level == "Level IV"


def test_supervisory_point_skipped_for_customary_supervisory_occupation():
    # General and Operations Managers - supervision is customary for this title
    result = calculate_wage_level(
        soc_code="11-1021.00",
        required_education="bachelors",
        required_experience_years=0,
        supervises_others=True,
        number_supervised=5,
    )
    assert result.factor_breakdown["supervisory"].points == 0


def test_special_skills_and_foreign_language_cap_at_two_points():
    result = calculate_wage_level(
        soc_code=SOFTWARE_DEVELOPER_SOC,
        required_education="bachelors",
        required_experience_years=0,
        supervises_others=False,
        special_skills=["AWS Certification"],
        foreign_language_required=True,
    )
    assert result.factor_breakdown["special_skills"].points == 2


def test_unknown_soc_code_raises():
    with pytest.raises(UnknownOccupationError):
        calculate_wage_level(
            soc_code="00-0000.00",
            required_education="bachelors",
            required_experience_years=0,
            supervises_others=False,
        )
