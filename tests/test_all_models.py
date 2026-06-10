"""Run short test samplers for all combinations of pulsar noise and GWB spectral models.

Usage: python tests/test_all_models.py [combo]
where combo is one of: pl_pl, pl_fs, fs_pl, fs_fs, all (default: all)
"""
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import QuickCW.QuickCW as QCW
from QuickCW.QuickMCMCUtils import ChainParams

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

COMBOS = {
    "pl_pl": ("powerlaw", "powerlaw"),
    "pl_fs": ("powerlaw", "free_spectral"),
    "fs_pl": ("free_spectral", "powerlaw"),
    "fs_fs": ("free_spectral", "free_spectral"),
}


def run_combo(name, psr_noise_model, gwb_noise_model, psrs):
    print("=" * 70)
    print(f"Running combo {name}: psr_noise_model={psr_noise_model}, gwb_noise_model={gwb_noise_model}")
    print("=" * 70)

    chain_params = ChainParams(
        T_max=4.0,
        n_chain=2,
        n_block_status_update=10,
        n_int_block=100,
        n_update_fisher=1_000,
        save_every_n=1_000,
        fisher_eig_downsample=2,
        savefile=os.path.join(DATA_DIR, f"test_chain_{name}.h5"),
        thin=10,
        gwb_comps=5,
        rn_comps=5,
        de_history_size=100,
        thin_de=100,
        verbosity=0,
    )

    pta, mcc = QCW.QuickCW(
        chain_params,
        psrs,
        noise_json=os.path.join(DATA_DIR, "fake_noisedict.json"),
        include_ecorr=False,
        backend_selection=False,
        amplitude_prior="detection",
        psr_noise_model=psr_noise_model,
        gwb_noise_model=gwb_noise_model,
    )

    # cross-check the fast likelihood against enterprise at the starting point
    x = mcc.samples[0, 0, :]
    logL_fast = mcc.FLIs[0].get_lnlikelihood(mcc.x0s[0])
    logL_ent = pta.get_lnlikelihood(x)
    print(f"fast logL = {logL_fast:.6f}, enterprise logL = {logL_ent:.6f}")
    assert np.isclose(logL_fast, logL_ent, rtol=1e-6), "fast likelihood disagrees with enterprise!"

    mcc.advance_N_blocks(20)  # 2000 samples
    print(f"combo {name} finished OK; acceptance fractions computed; final logL = "
          f"{mcc.FLIs[0].get_lnlikelihood(mcc.x0s[0]):.3f}")
    return True


def main():
    sel = sys.argv[1] if len(sys.argv) > 1 else "all"
    with open(os.path.join(DATA_DIR, "fake_psrs.pkl"), "rb") as f:
        psrs = pickle.load(f)

    combos = COMBOS if sel == "all" else {sel: COMBOS[sel]}
    for name, (pnm, gnm) in combos.items():
        run_combo(name, pnm, gnm, psrs)
    print("ALL REQUESTED COMBOS PASSED")


if __name__ == "__main__":
    main()
