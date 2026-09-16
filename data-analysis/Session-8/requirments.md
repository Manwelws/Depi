NumPy Programming Assignment
Part 1: Smart Array Factory
Description

Create a function that allows users to generate specific array types quickly using built-in NumPy creation methods.
Function Signature
Python

def array_factory(mode, shape, value=None):

Requirements & Behavior

The function must return a NumPy array based on the provided mode argument:

    'zeros': Returns an array of shape shape filled with 0 (e.g., using np.zeros).

    'ones': Returns an array of shape shape filled with 1 (e.g., using np.ones).

    'full': Returns an array of shape shape filled with the specified value (e.g., using np.full).

    'identity': Returns a square identity matrix of size shape (e.g., using np.eye or np.identity).

Part 2: The secure_reshape_and_stack Function
Description

Implement a function demonstrating how to handle data integration by converting input data structures into NumPy arrays, transforming a flat data structure into a matrix, and vertically stacking it with an existing dataset inside an exception-handling block.
Function Signature
Python

def secure_reshape_and_stack(data1, data2, new_shape):

Requirements & Steps

The function must execute the following operations within a try...except block:

    Input Conversion: Convert both input arguments data1 and data2 into NumPy ndarray objects (arr1 and arr2).

    Reshape: Change the dimensions of arr1 to new_shape using NumPy's reshape functionality (e.g., arr1.reshape(new_shape)).

    Vertical Stacking: Combine the reshaped reshaped_arr1 and arr2 into a single matrix vertically using vertical stacking (e.g., np.vstack).

        Constraint: Both matrices must share the same number of columns to successfully stack.

    Return Value: Return the final vertically stacked matrix (combined_dataset).

    Error Handling: Catch any ValueError raised during incompatible reshaping or vertical stacking operations, and re-raise it with the custom message:
    Python

raise ValueError(f"Company-grade Error: {e}")