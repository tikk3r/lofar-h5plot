class SoltabCache:
    '''Simple class just to store temporarily reordered soltab data.'''
    def __init__(self, values, axes, weights=None):
        """ Initialize a new SoltabCache instance.

        Args:
            values (ndarray): values to cache.
            axes (ndarray): axes to store.
            weights (ndarray or None): weights to cache.
        Returns:
            None
        """
        self.values = values
        self.axes = axes
        self.weights = weights

    def update(self, nvalues, naxes, weights=None):
        """ Update the data in the cache.

        Args:
            nvalues (ndarray): new values to store in the cache.
            naxes (ndarray): new axes to store in the cache.
            weights (ndarray or None): new weghts to store in the cache.
        Returns:
            None
        """
        self.values = nvalues
        self.axes = naxes
        self.weights = weights


