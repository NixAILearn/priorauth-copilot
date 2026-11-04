"""Code-derived fields (spec fields with evaluator=code). The model never computes these.

Each function reads verified observations and adds derived ones that cite their sources, so
a derived value's evidence is the quotes it was computed from. A missing input leaves the
derived field absent, which the evaluator reads as insufficient evidence.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from priorauth.extractor import Obs
from priorauth.spec import Window

Store = dict[tuple[str, str | None], list[Obs]]


def window_start(request_date: date, window: Window) -> date:
    """First day inside a look-back window, inclusive (D-019, D-022).

    Written independently of case_spec.window_start so the label oracle and the pipeline do
    not share code (D-030).
    """
    import calendar
    from datetime import timedelta

    if window.days is not None:
        return request_date - timedelta(days=window.days)
    total = request_date.year * 12 + (request_date.month - 1) - (window.months or 0)
    y, m = divmod(total, 12)
    return date(y, m + 1, min(request_date.day, calendar.monthrange(y, m + 1)[1]))


def in_window(d: date | None, request_date: date, window: Window) -> bool:
    return d is not None and window_start(request_date, window) <= d <= request_date


def completed_years(born: date, on: date) -> int:
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


def round1(x: float) -> float:
    """One decimal, 0.05 rounds up (NHP-MP-021 7.6)."""
    return float(Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def _num(o: Obs) -> float | None:
    return o.value if isinstance(o.value, float) else None


def _derived(name: str, unit_id, value, unit, on, sources, record=None) -> Obs:
    return Obs(
        field=name,
        unit_id=unit_id,
        value=value,
        unit=unit,
        on=on,
        record=record or f"derived:{name}@{on}",
        doc_id="DERIVED",
        quote="",
        sources=tuple(sources),
    )


def _get(store: Store, name: str, unit_id: str | None) -> list[Obs]:
    return store.get((name, unit_id), [])


def _add(store: Store, o: Obs) -> None:
    store.setdefault((o.field, o.unit_id), []).append(o)


def _by(obs: list[Obs], key: Callable[[Obs], object]) -> dict[object, list[Obs]]:
    out: dict[object, list[Obs]] = {}
    for o in obs:
        out.setdefault(key(o), []).append(o)
    return out


# --- NHP-MP-021 -------------------------------------------------------------------------------


def age_years(store: Store, unit, ctx) -> None:
    dobs = _get(store, "date_of_birth", unit)
    request = [o for o in dobs if o.doc_id == "REQUEST"]  # eligibility data wins
    for o in request or dobs[-1:]:
        if isinstance(o.value, date):
            age = completed_years(o.value, ctx.request_date)
            _add(store, _derived("age_years", unit, float(age), "years", ctx.request_date, [o]))


_HEIGHT_M = {"cm": 0.01, "m": 1.0, "in": 0.0254}
_WEIGHT_KG = {"kg": 1.0, "lb": 0.45359237, "lbs": 0.45359237}


def bmi(store: Store, unit, ctx) -> None:
    recorded = _get(store, "bmi_recorded", unit)
    for o in recorded:
        if _num(o) is not None:
            _add(store, _derived("bmi", unit, o.value, "kg/m2", o.on, [o], record=o.record))
    dates_with_bmi = {o.on for o in recorded}
    heights = _by(_get(store, "height", unit), lambda o: o.on)
    for w in _get(store, "weight", unit):
        if w.on in dates_with_bmi or w.on not in heights:
            continue
        for h in heights[w.on]:
            hu, wu = (h.unit or "").strip().lower(), (w.unit or "").strip().lower()
            if hu in _HEIGHT_M and wu in _WEIGHT_KG and _num(h) and _num(w):
                metres = h.value * _HEIGHT_M[hu]  # type: ignore[operator]
                value = round1(w.value * _WEIGHT_KG[wu] / metres**2)  # type: ignore[operator]
                _add(store, _derived("bmi", unit, value, "kg/m2", w.on, [h, w]))
                break


def central_mixed_share_pct(store: Store, unit, ctx) -> None:
    # Unrounded: the policy (7.9) gives no rounding rule for this share.
    parts = {
        k: _by(_get(store, k, unit), lambda o: o.on)
        for k in ("central_apneas", "mixed_apneas", "total_apneas_hypopneas")
    }
    for on, totals in parts["total_apneas_hypopneas"].items():
        c, m = parts["central_apneas"].get(on), parts["mixed_apneas"].get(on)
        t = totals[0]
        if c and m and _num(t):
            share = (c[0].value + m[0].value) / t.value * 100  # type: ignore[operator]
            _add(store, _derived("central_mixed_share_pct", unit, share, "%", on, [c[0], m[0], t]))


def pap_report_days(store: Store, unit, ctx) -> None:
    for o in _get(store, "pap_pct_nights_4h", unit):
        if o.start and o.end and o.end >= o.start:
            days = float((o.end - o.start).days + 1)  # consecutive days, both ends included
            _add(store, _derived("pap_report_days", unit, days, "days", o.end, [o], o.record))


# --- NHP-MP-034 (per target ulcer) ------------------------------------------------------------

_LEN_CM = {"cm": 1.0, "mm": 0.1}
_AREA_CM2 = {
    "cm2": 1.0,
    "cm^2": 1.0,
    "cm²": 1.0,
    "sq cm": 1.0,
    "mm2": 0.01,
    "mm^2": 0.01,
    "mm²": 0.01,
}


def _pair_by_document(groups: dict[tuple, dict[str, Obs]]) -> None:
    """D-064: a length and a width with different record labels still pair when they are the
    only unpaired length and width from the same document on the same date."""
    loose: dict[tuple, list[tuple[tuple, dict[str, Obs]]]] = {}
    for key, g in groups.items():
        if len(g) == 1 and next(iter(g)) in ("wound_length", "wound_width"):
            o = next(iter(g.values()))
            loose.setdefault((o.on, o.doc_id), []).append((key, g))
    for (on, _doc), items in loose.items():
        lens = [g for _, g in items if "wound_length" in g]
        wids = [g for _, g in items if "wound_width" in g]
        if on is None or len(lens) != 1 or len(wids) != 1:
            continue  # ambiguous: leave unpaired rather than guess
        lens[0]["wound_width"] = wids[0]["wound_width"]
        for key, g in items:
            if g is wids[0]:
                del groups[key]


def wound_area_cm2(store: Store, unit, ctx) -> None:
    keys = ("wound_length", "wound_width", "wound_area_recorded")
    groups: dict[tuple, dict[str, Obs]] = {}
    for k in keys:
        for o in _get(store, k, unit):
            groups.setdefault((o.on, o.record), {}).setdefault(k, o)
    _pair_by_document(groups)
    for (on, record), g in groups.items():
        area = g.get("wound_area_recorded")
        if area and (area.unit or "").strip().lower() in _AREA_CM2 and _num(area) is not None:
            value = area.value * _AREA_CM2[area.unit.strip().lower()]  # type: ignore[union-attr,operator]
            _add(store, _derived("wound_area_cm2", unit, value, "cm2", on, [area], record))
            continue
        ln, wd = g.get("wound_length"), g.get("wound_width")
        if ln and wd and _num(ln) is not None and _num(wd) is not None:
            lu, wu = (ln.unit or "").strip().lower(), (wd.unit or "").strip().lower()
            if lu in _LEN_CM and wu in _LEN_CM:
                value = ln.value * _LEN_CM[lu] * wd.value * _LEN_CM[wu]  # type: ignore[operator]
                _add(
                    store,
                    _derived("wound_area_cm2", unit, round(value, 4), "cm2", on, [ln, wd], record),
                )


def _measurement_dates(store: Store, unit, request_date: date) -> dict[date, list[Obs]]:
    out: dict[date, list[Obs]] = {}
    for k in ("measurement_date", "wound_length", "wound_area_recorded"):
        for o in _get(store, k, unit):
            if o.on and o.on <= request_date:
                out.setdefault(o.on, []).append(o)
    return out


def wound_course(store: Store, unit, ctx) -> None:
    """current_measurement_date, baseline/current area, reduction, care days, largest gap."""
    dates = _measurement_dates(store, unit, ctx.request_date)
    if not dates:
        return
    current = max(dates)
    cur_src = dates[current][:1]
    _add(store, _derived("current_measurement_date", unit, current, None, current, cur_src))
    areas = _by(_get(store, "wound_area_cm2", unit), lambda o: o.on)
    if current in areas:
        a = areas[current][0]
        _add(store, _derived("current_area_cm2", unit, a.value, "cm2", current, [a]))
    baselines = [o for o in _get(store, "baseline_date", unit) if isinstance(o.value, date)]
    if not baselines:
        return
    b = max(baselines, key=lambda o: o.value)  # type: ignore[arg-type,return-value]
    bdate: date = b.value  # type: ignore[assignment]
    if bdate in areas:
        ba = areas[bdate][0]
        _add(store, _derived("baseline_area_cm2", unit, ba.value, "cm2", bdate, [b, ba]))
        if current in areas and ba.value:
            ca = areas[current][0]
            pct = (ba.value - ca.value) / ba.value * 100  # type: ignore[operator]
            _add(store, _derived("area_reduction_pct", unit, pct, "%", current, [ba, ca]))
    _add(
        store,
        _derived(
            "standard_care_days",
            unit,
            float((current - bdate).days),
            "days",
            current,
            [b, *cur_src],
        ),
    )
    span = sorted(d for d in dates if bdate <= d <= current)
    if bdate not in span:
        span = [bdate, *span]
    gap = (
        max((b2 - b1).days for b1, b2 in zip(span, span[1:], strict=False)) if len(span) > 1 else 0
    )
    _add(
        store,
        _derived("max_measurement_gap_days", unit, float(gap), "days", current, [b, *cur_src]),
    )


def _side(o: Obs) -> str | None:
    q = o.quote.lower()
    r, lft = bool(re.search(r"\bright\b", q)), bool(re.search(r"\bleft\b", q))
    return "right" if r and not lft else "left" if lft and not r else None


def _one(cands: list[Obs], v: Obs) -> Obs | None:
    """The single candidate, or the single one on the value's side; never a guess."""
    if len(cands) == 1:
        return cands[0]
    side = _side(v)
    same = [c for c in cands if side and _side(c) == side]
    return same[0] if len(same) == 1 else None


def _pair_tests(types: dict[str, Obs], values: dict[str, Obs], dates: dict[str, Obs]) -> None:
    """D-067: a test value whose record label matches no test type pairs with the type (and date)
    from the same document, as D-064 does for wound length and width. Same date when both have
    one; when a report has several tests, the right/left side in the quotes must match."""
    used = {r for r in values if r in types}
    for rec, v in list(values.items()):
        if rec in types:
            continue
        cands = [
            t
            for r, t in types.items()
            if r not in used
            and r not in values
            and t.doc_id == v.doc_id
            and (t.on is None or v.on is None or t.on == v.on)
        ]
        t = _one(cands, v)
        if t is None:
            continue
        used.add(t.record)
        types[rec] = t
        if rec not in dates:
            ds = [d for r, d in dates.items() if r not in values and d.doc_id == v.doc_id]
            if len({d.value for d in ds}) == 1:
                dates[rec] = ds[0]
            elif (d := _one(ds, v)) is not None:
                dates[rec] = d


def perfusion(store: Store, unit, ctx) -> None:
    """counted_tests, best counted ABI / toe pressure / TcPO2 and ulcer type (7.11 to 7.13)."""
    types = {o.record: o for o in _get(store, "perfusion_test_type", unit)}
    values = {o.record: o for o in _get(store, "perfusion_test_value", unit)}
    dates = {o.record: o for o in _get(store, "perfusion_test_date", unit)}
    _pair_tests(types, values, dates)
    revasc = [
        o.value
        for o in _get(store, "revascularization_date", unit)
        if isinstance(o.value, date) and o.value <= ctx.request_date
    ]
    last_revasc = max(revasc) if revasc else None
    noncomp = [o for o in _get(store, "abi_reported_noncompressible", unit) if o.value is True]
    three_months = Window(months=3)
    counted: list[tuple[str, float, Obs, Obs]] = []
    for rec, t in types.items():
        val = values.get(rec)
        if val is None or _num(val) is None:
            continue
        on = dates[rec].value if rec in dates else (val.on or t.on)
        if not isinstance(on, date) or not in_window(on, ctx.request_date, three_months):
            continue
        if last_revasc and on <= last_revasc:
            continue  # a test on or before the revascularization does not count (7.11)
        counted.append((str(t.value), val.value, t, val))  # type: ignore[arg-type]
    if not counted:
        return
    srcs = [o for _, _, t, v in counted for o in (t, v)]
    summary = "; ".join(f"{k} {v:g} on {t.on or v.on}" for k, v, t, _ in counted)
    _add(store, _derived("counted_tests", unit, summary, None, ctx.request_date, srcs))

    def is_noncompressible(t: Obs, v: Obs) -> bool:
        if v.value > 1.30:  # type: ignore[operator]
            return True
        return any(
            n.record == v.record or (n.doc_id == v.doc_id and n.on == (v.on or t.on))
            for n in noncomp
        )

    abis = [(v, t) for k, _, t, v in counted if k == "abi" and not is_noncompressible(t, v)]
    toes = [(v, t) for k, _, t, v in counted if k == "toe_pressure"]
    tcpo2 = [(v, t) for k, _, t, v in counted if k == "tcpo2"]
    for name, items in (
        ("best_counted_abi", abis),
        ("best_counted_toe_pressure", toes),
        ("best_counted_tcpo2", tcpo2),
    ):
        if items:
            v, t = max(items, key=lambda p: p[0].value)  # type: ignore[arg-type,return-value]
            _add(store, _derived(name, unit, v.value, v.unit, v.on or t.on, [t, v]))
    ischemic = (
        [(v, t) for v, t in abis if v.value < 0.90]  # type: ignore[operator]
        + [(v, t) for v, t in toes if v.value < 70]  # type: ignore[operator]
        + [(v, t) for v, t in tcpo2 if v.value < 40]  # type: ignore[operator]
    )
    kind = "neuro_ischemic" if ischemic else "neuropathic"
    src = [o for v, t in (ischemic or [*abis, *toes, *tcpo2]) for o in (t, v)] or srcs
    _add(store, _derived("ulcer_type", unit, kind, None, ctx.request_date, src))


# --- NHP-MP-047 -------------------------------------------------------------------------------


def kl_grade_highest(store: Store, unit, ctx) -> None:
    """Grade from a report that meets 3.4: only reports that state standing views count."""
    standing = {
        (o.on, o.doc_id) for o in _get(store, "xray_weight_bearing", unit) if o.value == "stated"
    }
    grades = _by(_get(store, "kl_grade_reported", unit), lambda o: (o.on, o.doc_id))
    grades = {k: v for k, v in grades.items() if k in standing}
    for (on, _doc), obs in grades.items():
        best = max(obs, key=lambda o: o.value)  # type: ignore[arg-type,return-value]
        _add(
            store,
            _derived(
                "kl_grade_highest", unit, best.value, "grade 0-4", on, [best], f"kl:{_doc}@{on}"
            ),
        )
    graded = set(grades)
    for o in _get(store, "joint_space_description", unit):
        key = (o.on, o.doc_id)
        if o.value == "complete_loss_or_bone_on_bone" and key not in graded and key in standing:
            _add(store, _derived("kl_grade_highest", unit, 4.0, "grade 0-4", o.on, [o]))


def conservative_care_days(store: Store, unit, ctx) -> None:
    starts = [
        o for o in _get(store, "conservative_care_start_date", unit) if isinstance(o.value, date)
    ]
    ends = [o for o in _get(store, "conservative_care_end_date", unit) if isinstance(o.value, date)]
    if starts and ends:
        s = min(starts, key=lambda o: o.value)  # type: ignore[arg-type,return-value]
        e = max(ends, key=lambda o: o.value)  # type: ignore[arg-type,return-value]
        days = float((e.value - s.value).days)  # type: ignore[operator]
        _add(store, _derived("conservative_care_days", unit, days, "days", e.value, [s, e]))


# Order matters: later steps read what earlier ones add.
DERIVATIONS: list[tuple[set[str], Callable]] = [
    ({"age_years"}, age_years),
    ({"bmi"}, bmi),
    ({"central_mixed_share_pct"}, central_mixed_share_pct),
    ({"pap_report_days"}, pap_report_days),
    ({"wound_area_cm2"}, wound_area_cm2),
    (
        {
            "current_measurement_date",
            "baseline_area_cm2",
            "current_area_cm2",
            "area_reduction_pct",
            "standard_care_days",
            "max_measurement_gap_days",
        },
        wound_course,
    ),
    (
        {
            "counted_tests",
            "best_counted_abi",
            "best_counted_toe_pressure",
            "best_counted_tcpo2",
            "ulcer_type",
        },
        perfusion,
    ),
    ({"kl_grade_highest"}, kl_grade_highest),
    ({"conservative_care_days"}, conservative_care_days),
]

KNOWN = set().union(*(names for names, _ in DERIVATIONS))


def derive_all(store: Store, spec, ctx) -> None:
    """Run every derivation the spec needs, once per unit (request, or each target ulcer)."""
    code_fields = {f.name: f for f in spec.fields if f.evaluator == "code"}
    unknown = set(code_fields) - KNOWN
    if unknown:
        raise NotImplementedError(f"no derivation for code field(s) {sorted(unknown)}")
    for names, fn in DERIVATIONS:
        hit = names & set(code_fields)
        if not hit:
            continue
        per = {code_fields[n].per for n in hit}
        units = [None] if per == {"request"} else ctx.unit_ids
        for unit in units:
            fn(store, unit, ctx)
