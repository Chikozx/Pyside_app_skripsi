# import tensorflow as tf
import numpy as np
matrix = np.array([
    [ 1, -1,  1,  1, -1, -1,  1, -1, 1, 1],
    [-1, -1,  1, -1,  1,  1, -1,  1, 1, -1]
])

bits = (matrix == 1).astype(np.uint8)

n, m = bits.shape
pad_len = (-m) % 8
if pad_len > 0:
    bits = np.pad(bits, ((0,0), (0,pad_len)), constant_values=0)

print(bits)
bytes_array = np.packbits(bits, axis=1)
# bytes_array2 = np.packbits(bits, axis=0)
bytes_obj = bytes_array.tobytes()

print(bytes_array)
print(len(bytes_obj))
for i in range(len(bytes_obj)):
    print(bytes_obj[i])