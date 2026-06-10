"""Run the NANOGrav 15-year QuickCW CW analysis with a free spectral model
for the per-pulsar red noise and a power law for the GWB.

Mirrors the settings of running_quickcw.ipynb in nanograv/15yr_cw_analysis,
with psr_noise_model='free_spectral'. Intended to be run from the NG15 folder
(e.g. inside a tmux session):

    cd NG15 && python run_ng15_free_spectral.py

Samples are saved to SAVEFILE; plot them with plot_ng15_free_spectral.ipynb.
"""
import bz2
import glob
import pickle
from time import perf_counter

import numpy as np

import QuickCW.QuickCW as QuickCW
from QuickCW.QuickMCMCUtils import ChainParams

###############################################################################
# Settings
###############################################################################

# number of iterations (increase to 100 million - 1 billion for actual analysis)
N = 5_000_000

n_int_block = 10_000    # iterations per block (one shape update + projection updates)
save_every_n = 100_000  # iterations between saving intermediate results (integer multiple of n_int_block)
fisher_eig_downsample = 2000  # how much less often to update fisher eigendirections

n_status_update = 100   # number of status update printouts

# parallel tempering parameters
T_max = 3.0
n_chain = 4

# data files
NOISEFILE = 'data/v1p1_all_dict.json'
PSR_DIST_FILE = 'data/pulsar_distances_15yr.pkl'

# RN empirical distributions are defined for the powerlaw (log10_A, gamma)
# parameters, so they cannot be used with the free spectral pulsar noise model
RN_EMP_DIST_FILE = None

# where results will be saved
SAVEFILE = 'quickCW_ng15_free_spectral_rn.h5'

###############################################################################
# Setup
###############################################################################

N_blocks = np.int64(N // n_int_block)
n_block_status_update = np.int64(N_blocks // n_status_update)

assert N_blocks % n_status_update == 0  # or we won't print status updates
assert N % save_every_n == 0            # or we won't save a complete block
assert N % n_int_block == 0             # or we won't execute the right number of blocks

ti = perf_counter()

# load data from BZ2 compressed pickle files
psrs = []
for psrfile in sorted(glob.glob('data/jar/*.bz2.pkl')):
    with bz2.BZ2File(psrfile, 'rb') as f:
        psr = pickle.load(f)
        print(psr.name)
        psrs.append(psr)
print(len(psrs), 'pulsars loaded in %.1f s' % (perf_counter() - ti))

chain_params = ChainParams(T_max, n_chain, n_block_status_update,
                           freq_bounds=np.array([np.nan, 3e-7]),  # GW frequency prior (np.nan -> 1/T_obs)
                           n_int_block=n_int_block,
                           save_every_n=save_every_n,
                           fisher_eig_downsample=fisher_eig_downsample,
                           rn_comps=30,   # frequency bins in the per-pulsar free spectral red noise model
                           gwb_comps=14,  # frequency components in the powerlaw GWB model
                           rn_emp_dist_file=RN_EMP_DIST_FILE,
                           savefile=SAVEFILE,
                           thin=100,  # save every `thin`th sample to file
                           prior_draw_prob=0.2, de_prob=0.6, fisher_prob=0.3,
                           dist_jump_weight=0.2, rn_jump_weight=0.3, gwb_jump_weight=0.1,
                           common_jump_weight=0.2, all_jump_weight=0.2,
                           fix_rn=False, zero_rn=False, fix_gwb=False, zero_gwb=False)

pta, mcc = QuickCW.QuickCW(chain_params, psrs,
                           amplitude_prior='detection',      # uniform in log-amplitude
                           psr_distance_file=PSR_DIST_FILE,  # parallax+DM pulsar distance priors
                           noise_json=NOISEFILE,
                           psr_noise_model='free_spectral',  # free spectral per-pulsar red noise
                           gwb_noise_model='powerlaw')       # power-law GWB

print('total number of parameters:', len(mcc.par_names))
print('setup done in %.1f s' % (perf_counter() - ti))

###############################################################################
# Run MCMC
###############################################################################

mcc.advance_N_blocks(N_blocks)

print('finished %d iterations in %.1f s; samples saved to %s' % (N, perf_counter() - ti, SAVEFILE))
