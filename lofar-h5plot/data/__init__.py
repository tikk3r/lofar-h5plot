import logging
import numpy as np

LOGGER = logging.getLogger('H5plot_logger')

def get_axis_permutation(st) -> list:
    order_current = st.getAxesNames()
    if ('phase_offset' in st.name):
        LOGGER.debug('Not reordering phase_offset as it is a single number.')
    if ('rotationmeasure' in st.name) or ('RMextract'in st.name) or ('clock' in st.name) or ('faraday' in st.name) or ('tec' in st.name and 'freq' not in order_current):
        order_wanted = ['time', 'ant']
    else:
        order_wanted = ['time', 'freq', 'ant']
    if 'pol' in order_current:
        order_wanted += ['pol']
    if 'dir' in order_current:
        order_wanted += ['dir']
    permutation = [order_wanted.index(axis) for axis in order_current]
    return permutation


def read_values_from_soltab(st, idx_time: int, idx_ant: int, idx_freq: int, idx_pol: int = 0, idx_dir: int = 0):
    """ Reorder a soltab in the order H5plot expects.

    The expected order in the plotter is time, frequency, antenna, polarization, direction.

    Args:
        st (SolTab): soltab instance to reorder the axes of.
    Returns:
        st_new (tuple): tuple of (values, weights, axes) reodered to the expected order.
        order_new (ndarray): array containing the reordered order of the axes.
    """
    LOGGER.debug('Reading values from soltab ' + st.name)
    permutation = get_axis_permutation(st)
    order_current = st.getAxesNames()
    order_wanted = []
    if ('phase_offset' in st.name):
        LOGGER.debug('Not reordering phase_offset as it is a single number.')
    if ('rotationmeasure' in st.name) or ('RMextract'in st.name) or ('clock' in st.name) or ('faraday' in st.name) or ('tec' in st.name and 'freq' not in order_current):
        order_wanted = [idx_time, idx_ant]
    else:
        order_wanted = [idx_time, idx_freq, idx_ant]
    if 'pol' in order_current:
        order_wanted += [idx_pol]
    if 'dir' in order_current:
        order_wanted += [idx_dir]
    permuted_idx = [order_wanted[p] for p in permutation]
    values = np.transpose(st.getValues()[0], permutation)
    return values
