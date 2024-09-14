import logging
import time

from losoto.lib_operations import reorderAxes
LOGGER = logging.getLogger('H5plot_logger')

def reorder_soltab(st):
    """ Reorder a soltab in the order H5plot expects.

    The expected order in the plotter is time, frequency, antenna, polarization, direction.

    Args:
        st (SolTab): soltab instance to reorder the axes of.
    Returns:
        st_new (tuple): tuple of (values, weights, axes) reodered to the expected order.
        order_new (ndarray): array containing the reordered order of the axes.
    """
    LOGGER.info('Reordering soltab ' + st.name)
    order_old = st.getAxesNames()
    if ('phase_offset' in st.name):
        LOGGER.info('Not reordering phase_offset as it is a single number.')
    if ('rotationmeasure' in st.name) or ('RMextract'in st.name) or ('clock' in st.name) or ('faraday' in st.name) or ('tec' in st.name and 'freq' not in order_old):
        order_new = ['time', 'ant']
    else:
        order_new = ['time', 'freq', 'ant']
    if 'pol' in order_old:
        order_new += ['pol']
    if 'dir' in order_old:
        order_new += ['dir']
    t1 = time.time()
    reordered = reorderAxes(st.getValues()[0], order_old, order_new)
    reordered_weights = reorderAxes(st.getValues(weight=True)[0], order_old, order_new)
    t2 = time.time()
    LOGGER.info('Reordering took {:f} seconds'.format(t2 - t1))
    reordered2 = {}
    for k in order_new:
        reordered2[k] = st.axes[k]
    st.axes = reordered2
    st.axesNames = order_new
    st_new = (reordered, st.getValues()[1])
    return st_new, reordered_weights, order_new
