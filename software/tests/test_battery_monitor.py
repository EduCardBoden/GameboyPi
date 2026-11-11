"""Tests für battery_monitor.py ohne Pi-Hardware.

Ausführen (Repo-Wurzel):  python -m pytest software/tests -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "configuration"))
import battery_monitor as bm  # noqa: E402


def test_divider_factor_includes_adc_load():
    # 100k / (100k || 6M) -> 2,0167; ohne Last wäre es genau 2
    assert abs(bm.divider_factor() - 2.0167) < 0.0005
    assert abs(bm.divider_factor(r_adc=float("inf")) - 2.0) < 1e-12


def test_raw_to_vbat_full_and_typical():
    # 4,2 V Akku -> AIN0 = 4,2 / 2,0167 = 2,0826 V -> Rohwert 16660
    raw = round(4.2 / bm.DIVIDER / 4.096 * 32768)
    assert abs(bm.raw_to_vbat(raw) - 4.2) < 0.001
    assert bm.raw_to_vbat(0) == 0
    assert bm.raw_to_vbat(0xFFFF) < 0          # Zweierkomplement


def test_percent_curve_bounds_and_monotonic():
    assert bm.percent(4.3) == 100
    assert bm.percent(4.2) == 100
    assert bm.percent(3.3) == 0
    assert bm.percent(3.0) == 0
    vals = [bm.percent(3.30 + i * 0.01) for i in range(91)]
    assert vals == sorted(vals)


def test_lbo_needs_consecutive_hits():
    m = bm.Monitor()
    assert m.step(3.7, True, 0) is None
    assert m.step(3.7, False, 5) is None      # Einbruch vorbei -> Zähler zurück
    assert m.step(3.7, True, 10) is None
    assert m.step(3.7, True, 15) is None
    assert m.step(3.7, True, 20) == "Akku leer (LBO)"


def test_low_voltage_shutdown_after_delay():
    m = bm.Monitor()
    t = 0
    reason = None
    while reason is None and t < 200:
        reason = m.step(3.20, False, t)
        t += 5
    assert reason is not None and reason.startswith("Akku leer (3.")
    assert bm.SHUTDOWN_DELAY_S < t <= bm.SHUTDOWN_DELAY_S + 60


def test_short_dip_does_not_shut_down():
    m = bm.Monitor()
    for t in range(0, 100, 5):
        v = 3.25 if t in (20, 25) else 3.80      # zwei Messungen Lastspitze
        assert m.step(v, False, t) is None


def test_adc_failure_keeps_lbo_watch():
    m = bm.Monitor()
    assert m.step(None, False, 0) is None and m.avg is None
    for t in (5, 10):
        assert m.step(None, True, t) is None
    assert m.step(None, True, 15) == "Akku leer (LBO)"
