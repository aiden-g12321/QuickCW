"""Generate a very small artificial PTA dataset for testing QuickCW.

Creates par/tim files for a few pulsars with white noise only residuals
using PINT, plus a noise dictionary JSON and a pickle of enterprise Pulsar objects.
"""
import json
import os
import pickle

import numpy as np

import pint.models as pm
import pint.simulation as ps
from enterprise.pulsar import Pulsar

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

PSRS = [
    # name, RAJ, DECJ, F0
    ("J0000+0000", "00:00:00", "00:00:00", 500.0),
    ("J0600+3000", "06:00:00", "30:00:00", 400.0),
    ("J1200-3000", "12:00:00", "-30:00:00", 300.0),
]

NTOA = 80
TOAERR_US = 1.0  # microseconds
MJD_START, MJD_END = 53000, 56500  # ~9.6 yr


def make_par(name, raj, decj, f0):
    par = f"""PSR      {name}
RAJ      {raj}   1
DECJ     {decj}  1
F0       {f0}    1
F1       -1e-15  1
PEPOCH   54750
POSEPOCH 54750
DM       10.0
EPHEM    DE421
UNITS    TDB
"""
    path = os.path.join(DATA_DIR, f"{name}.par")
    with open(path, "w") as f:
        f.write(par)
    return path


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    rng = np.random.default_rng(42)
    psrs = []
    noisedict = {}
    for name, raj, decj, f0 in PSRS:
        parfile = make_par(name, raj, decj, f0)
        model = pm.get_model(parfile)
        toas = ps.make_fake_toas_uniform(
            MJD_START, MJD_END, NTOA, model=model, error=TOAERR_US * 1e-6 * 1e6 * 0 + TOAERR_US,
            add_noise=True, name="fake", obs="gbt",
        )
        timfile = os.path.join(DATA_DIR, f"{name}.tim")
        toas.write_TOA_file(timfile, format="tempo2")

        psr = Pulsar(parfile, timfile, ephem="DE421", timing_package="pint")
        psrs.append(psr)

        noisedict[f"{name}_efac"] = 1.0
        noisedict[f"{name}_log10_t2equad"] = -8.0

    with open(os.path.join(DATA_DIR, "fake_psrs.pkl"), "wb") as f:
        pickle.dump(psrs, f)
    with open(os.path.join(DATA_DIR, "fake_noisedict.json"), "w") as f:
        json.dump(noisedict, f, indent=2)
    print("Wrote", len(psrs), "pulsars to", DATA_DIR)


if __name__ == "__main__":
    main()
