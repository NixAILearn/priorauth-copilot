"""Quote checks and code-derived values (D-046, D-050)."""

from datetime import date
from types import SimpleNamespace

from priorauth.derive import (
    bmi,
    in_window,
    kl_grade_highest,
    perfusion,
    round1,
    window_start,
    wound_area_cm2,
    wound_course,
)
from priorauth.extractor import Obs
from priorauth.quotes import date_in, number_in, quote_in
from priorauth.spec import Window

DOCS = {"D01": "**Vitals:** BP 130/80. Wt 198 lb.  Ht 70 in.\nThe patient said “it locks”."}


def test_quote_normalization_is_whitespace_quotes_and_asterisks_only():
    assert quote_in(DOCS, "D01", "Vitals: BP 130/80.")
    assert quote_in(DOCS, "D01", 'The patient said "it locks".')
    assert quote_in(DOCS, "D01", "Wt 198 lb. Ht 70 in.")
    assert not quote_in(DOCS, "D01", "Weight 198 lb.")  # paraphrase
    assert not quote_in(DOCS, "D02", "Wt 198 lb.")  # wrong document
    assert not quote_in(DOCS, "D01", "198 lb")  # too short to be a citation


def test_values_must_appear_in_their_quote():
    assert number_in("BMI 31.20 kg/m2", 31.2)
    assert not number_in("BMI 31.2 kg/m2", 31.0)
    assert date_in("Study date: 03/12/2026", date(2026, 3, 12))
    assert date_in("NSTEMI 05/2023", date(2023, 5, 31))
    assert date_in("seen on March 4, 2026", date(2026, 3, 4))
    assert not date_in("Study date: 03/12/2026", date(2026, 12, 3))


def test_windows_are_inclusive_calendar_months_or_days():
    rd = date(2026, 10, 15)
    assert window_start(rd, Window(months=24)) == date(2024, 10, 15)
    assert window_start(date(2026, 3, 31), Window(months=1)) == date(2026, 2, 28)
    assert in_window(date(2024, 10, 15), rd, Window(months=24))
    assert not in_window(date(2024, 10, 14), rd, Window(months=24))
    assert window_start(rd, Window(days=14)) == date(2026, 10, 1)
    assert not in_window(date(2026, 10, 16), rd, Window(days=14))  # after the request


def o(field, value, on=None, unit=None, record="r", doc="D01", unit_id=None):
    return Obs(
        field=field,
        unit_id=unit_id,
        value=value,
        unit=unit,
        on=on,
        record=record,
        doc_id=doc,
        quote="q",
    )


CTX = SimpleNamespace(request_date=date(2026, 10, 15), unit_ids=["U1"])


def test_bmi_from_height_and_weight_rounds_half_up():
    d = date(2026, 9, 11)
    store = {
        ("height", None): [o("height", 70.0, d, "in")],
        ("weight", None): [o("weight", 198.0, d, "lb")],
    }
    bmi(store, None, CTX)
    assert store[("bmi", None)][0].value == 28.4
    assert round1(34.95) == 35.0


def test_recorded_bmi_wins_over_height_and_weight_on_the_same_date():
    d = date(2026, 9, 11)
    store = {
        ("bmi_recorded", None): [o("bmi_recorded", 34.9, d)],
        ("height", None): [o("height", 60.0, d, "in")],
        ("weight", None): [o("weight", 250.0, d, "lb")],
    }
    bmi(store, None, CTX)
    assert [x.value for x in store[("bmi", None)]] == [34.9]


def test_wound_area_reduction_gap_and_care_days():
    u = "U1"
    m = [
        (date(2026, 9, 1), 30.0, 20.0, "mm"),
        (date(2026, 9, 8), 2.8, 2.0, "cm"),
        (date(2026, 9, 29), 2.4, 2.0, "cm"),
    ]
    store = {}
    for d, ln, wd, unit in m:
        rec = f"m{d}"
        store.setdefault(("wound_length", u), []).append(
            o("wound_length", ln, d, unit, rec, unit_id=u)
        )
        store.setdefault(("wound_width", u), []).append(
            o("wound_width", wd, d, unit, rec, unit_id=u)
        )
    store[("baseline_date", u)] = [
        o("baseline_date", date(2026, 9, 1), date(2026, 9, 1), unit_id=u)
    ]
    wound_area_cm2(store, u, CTX)
    wound_course(store, u, CTX)
    get = lambda k: store[(k, u)][0].value  # noqa: E731
    assert get("baseline_area_cm2") == 6.0
    assert get("current_area_cm2") == 4.8
    assert round(get("area_reduction_pct"), 6) == 20.0
    assert get("standard_care_days") == 28.0
    assert get("max_measurement_gap_days") == 21.0


def test_noncompressible_abi_does_not_count_and_toe_pressure_sets_type():
    u, d = "U1", date(2026, 9, 1)
    store = {
        ("perfusion_test_type", u): [
            o("perfusion_test_type", "abi", d, record="a", unit_id=u),
            o("perfusion_test_type", "toe_pressure", d, record="t", unit_id=u),
        ],
        ("perfusion_test_value", u): [
            o("perfusion_test_value", 1.42, d, record="a", unit_id=u),
            o("perfusion_test_value", 65.0, d, "mmHg", "t", unit_id=u),
        ],
    }
    perfusion(store, u, CTX)
    assert ("best_counted_abi", u) not in store
    assert store[("best_counted_toe_pressure", u)][0].value == 65.0
    assert store[("ulcer_type", u)][0].value == "neuro_ischemic"  # toe pressure under 70


def test_tests_before_a_revascularization_do_not_count():
    u = "U1"
    store = {
        ("perfusion_test_type", u): [
            o("perfusion_test_type", "abi", date(2026, 8, 1), record="a", unit_id=u)
        ],
        ("perfusion_test_value", u): [
            o("perfusion_test_value", 0.5, date(2026, 8, 1), record="a", unit_id=u)
        ],
        ("revascularization_date", u): [o("revascularization_date", date(2026, 8, 20), unit_id=u)],
    }
    perfusion(store, u, CTX)
    assert ("ulcer_type", u) not in store


def test_kl_grade_only_from_a_standing_report():
    d = date(2026, 9, 1)
    store = {
        ("kl_grade_reported", None): [o("kl_grade_reported", 2.0, d, doc="D02")],
        ("xray_weight_bearing", None): [o("xray_weight_bearing", "not_stated", d, doc="D02")],
    }
    kl_grade_highest(store, None, CTX)
    assert ("kl_grade_highest", None) not in store
    store[("xray_weight_bearing", None)] = [o("xray_weight_bearing", "stated", d, doc="D02")]
    kl_grade_highest(store, None, CTX)
    assert store[("kl_grade_highest", None)][0].value == 2.0


def test_quote_may_differ_only_in_first_letter_case():  # D-061
    from priorauth.quotes import quote_in

    docs = {"D01": "Scoring followed AASM rules; hypopneas scored using the 4% rule."}
    assert quote_in(docs, "D01", "Hypopneas scored using the 4% rule.")
    assert not quote_in(docs, "D01", "Hypopneas Scored using the 4% rule.")
    assert not quote_in(docs, "D01", "HYPOPNEAS scored using the 4% rule.")


def test_number_field_takes_a_single_number_from_prose():  # D-061
    from priorauth.extractor import parse_value
    from priorauth.spec import FieldDef

    fd = FieldDef(
        name="bmi_recorded", type="number", unit="kg/m2", evaluator="model", description="x"
    )
    assert parse_value(fd, "31.6") == 31.6
    assert parse_value(fd, "BMI 31.6 kg/m2.") == 31.6
    assert parse_value(fd, "22%") == 22
    assert parse_value(fd, "5'10\"") is None  # two numbers: refused, never guessed
    assert parse_value(fd, "not reported") is None
