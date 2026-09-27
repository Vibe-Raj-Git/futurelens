from futurelens.models.upagraha import UpagrahaName
from futurelens.upagraha.sun_chain import compute_sun_chain, validate_sun_chain


def _angsep(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def test_chain_closes_back_to_sun():
    sun = 123.456
    chain = compute_sun_chain(sun)
    upaketu = chain[UpagrahaName.UPAKETU].longitude
    assert abs(_angsep(upaketu, sun) - 30.0) < 1e-9


def test_invariants_hold_for_many_suns():
    for sun in range(0, 360, 7):
        chain = compute_sun_chain(float(sun))
        validate_sun_chain(chain)
