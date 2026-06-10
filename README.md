# QuickCW
Fast continuous wave (CW) analysis for pulsar timing array data

See [arXiv:2204.07160](https://arxiv.org/abs/2204.07160) for details on the method, and the [Quick-start Guide](https://github.com/nanograv/QuickCW/blob/main/docs/how_to_run_QuickCW.md) for details on how to run the code yourself!

**This fork** adds the option to model the per-pulsar red noise and/or the GWB with a free spectral model (the PSD in every frequency bin is a free `log10_rho` parameter) instead of a power law, selected via `QuickCW(..., psr_noise_model='powerlaw'|'free_spectral', gwb_noise_model='powerlaw'|'free_spectral')`. See [demo_free_spectral.ipynb](demo_free_spectral.ipynb) for a demonstration, and `tests/` for short test samplers covering all model combinations on a tiny simulated dataset. The `NG15/` folder contains the NANOGrav 15-year dataset (from [nanograv/15yr_cw_analysis](https://github.com/nanograv/15yr_cw_analysis)) along with a demo notebook ([NG15/ng15_cw_free_spectral.ipynb](NG15/ng15_cw_free_spectral.ipynb)), a standalone run script for long runs in e.g. tmux ([NG15/run_ng15_free_spectral.py](NG15/run_ng15_free_spectral.py)), and a plotting notebook ([NG15/plot_ng15_free_spectral.ipynb](NG15/plot_ng15_free_spectral.ipynb)) for the NG15 CW analysis with a free spectral model for the per-pulsar red noise and a power law for the GWB.

Citation:
```
@ARTICLE{2022PhRvD.105l2003B,
       author = {{B{\'e}csy}, Bence and {Cornish}, Neil J. and {Digman}, Matthew C.},
        title = "{Fast Bayesian analysis of individual binaries in pulsar timing array data}",
      journal = {\prd},
     keywords = {General Relativity and Quantum Cosmology, Astrophysics - High Energy Astrophysical Phenomena},
         year = 2022,
        month = jun,
       volume = {105},
       number = {12},
          eid = {122003},
        pages = {122003},
          doi = {10.1103/PhysRevD.105.122003},
archivePrefix = {arXiv},
       eprint = {2204.07160},
 primaryClass = {gr-qc},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2022PhRvD.105l2003B},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```
