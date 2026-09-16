"""NumPy Programming Assignment - Session 8 solution."""

import numpy as np


def array_factory(mode, shape, value=None):
    """Generate specific array types quickly using NumPy creation methods.

    Args:
        mode: One of 'zeros', 'ones', 'full', 'identity'.
        shape: Desired shape (tuple/int). For 'identity', square size (int).
        value: Fill value required when mode == 'full'.

    Returns:
        NumPy ndarray.
    """
    if mode == 'zeros':
        return np.zeros(shape)
    elif mode == 'ones':
        return np.ones(shape)
    elif mode == 'full':
        if value is None:
            raise ValueError("value must be provided for mode 'full'")
        return np.full(shape, value)
    elif mode == 'identity':
        # shape is the square matrix size (int). Also accept (n,), (n, n).
        if isinstance(shape, (tuple, list)):
            if len(shape) == 1:
                n = shape[0]
            elif len(shape) == 2 and shape[0] == shape[1]:
                n = shape[0]
            else:
                raise ValueError(
                    "For mode 'identity', shape must be an int n or a square shape (n, n)"
                )
            return np.eye(n)
        return np.eye(shape)
    else:
        raise ValueError(
            f"Invalid mode '{mode}'. Expected one of: 'zeros', 'ones', 'full', 'identity'."
        )


def secure_reshape_and_stack(data1, data2, new_shape):
    """Convert inputs to arrays, reshape arr1, and vertically stack with arr2.

    Args:
        data1: Input data structure to convert and reshape.
        data2: Input data structure to convert and stack with.
        new_shape: Target shape for arr1.

    Returns:
        Vertically stacked matrix (combined_dataset).

    Raises:
        ValueError: With message f"Company-grade Error: {e}" on
            incompatible reshape or stacking.
    """
    try:
        arr1 = np.asarray(data1)
        arr2 = np.asarray(data2)
        reshaped_arr1 = arr1.reshape(new_shape)
        combined_dataset = np.vstack((reshaped_arr1, arr2))
        return combined_dataset
    except ValueError as e:
        raise ValueError(f"Company-grade Error: {e}")


if __name__ == "__main__":
    print(array_factory('zeros', (2, 3)))
    print(array_factory('ones', (2, 2)))
    print(array_factory('full', (2, 2), value=7))
    print(array_factory('identity', 3))

    print(secure_reshape_and_stack([1, 2, 3, 4], [[5, 6], [7, 8]], (2, 2)))
