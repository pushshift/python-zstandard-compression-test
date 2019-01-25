#!/usr/bin/env python3

import zstandard as zstd
import time

# zstandard module info: https://pypi.org/project/zstandard/

# Load binary compressed test file
compressed_file_data = open("compression_test_100MB.txt.zst","rb").read()

# This is how to decompress the file
dctx = zstd.ZstdDecompressor()
uncompressed_file_data = dctx.decompress(compressed_file_data) # uncompressed_file_data is now a bytes string.

# Printing the type will show "<class 'bytes'>"
print ("Object type is {}".format(type(uncompressed_file_data)))

# To convert to a UTF-8 string, use the decode method
uncompressed_file_data = uncompressed_file_data.decode()

# Printing the type will now show "<class 'str'>"
print ("Object type is {}".format(type(uncompressed_file_data)))

print("\nTesting Zstandard Compression Levels 0-22\n")
for x in range(0,23):
    params = zstd.ZstdCompressionParameters(compression_level=x) # Set compression parameters here
    cctx = zstd.ZstdCompressor(compression_params=params)       # Set compression_params to the parameters defined previously
    time_start = time.time()                                    # Start time before compression begins
    compressed = cctx.compress(uncompressed_file_data.encode()) # When compressing a string, the string needs to be a bytes object. encode() converts to bytes.
    time_end = time.time() - time_start                         # Total time taken to compress
    uncompressed_length = len(uncompressed_file_data)           # Calculate uncompressed length
    compressed_length = len(compressed)                         # Calculate the compressed length

    print("Compression Level: {} - Uncompressed: {} - Compressed: {} - Ratio: {}% - Compression Time: {}ms".format(str(x).rjust(2),"{:,}".format(uncompressed_length),"{:,}".format(compressed_length),"{:5.2f}".format(compressed_length*100/uncompressed_length),"{:8.2f}".format((time_end)*1000)))

# Let's pull the first and last JSON object
first_json_string = uncompressed_file_data.split("\n")[0]
last_json_string = uncompressed_file_data.split("\n")[-2] # This is the second to last string because the last string is incomplete in the test file
ljs_length = len(first_json_string)

# Generally, if you compress small strings, the compression ratio is usually very poor
params = zstd.ZstdCompressionParameters(compression_level=3)
cctx = zstd.ZstdCompressor(compression_params=params)
compressed = cctx.compress(last_json_string.encode())
print("\nCompression Level without using a dictionary")
print("Uncompressed Length: {} - Compressed Length: {} - Compression Ratio: {}%".format(ljs_length,len(compressed),"{0:.3f}".format(len(compressed)*100/ljs_length)))

# This is why custom dictionaries are great for compressing smaller objects. We will create a dictionary using the first JSON string and use it to compress
# the last JSON string

dictionary = zstd.ZstdCompressionDict(first_json_string.encode()) # Remember, we need to encode to convert the string to a bytes string
params = zstd.ZstdCompressionParameters(compression_level=3)
cctx = zstd.ZstdCompressor(dict_data=dictionary,compression_params=params)
compressed = cctx.compress(last_json_string.encode())
print("\nCompression Level using a dictionary")
print("Uncompressed Length: {} - Compressed Length: {} - Compression Ratio: {}%".format(ljs_length,len(compressed),"{0:.3f}".format(len(compressed)*100/ljs_length)))

# When compressing small strings, it is always better to use a dictionary. The dictionary used should be a similar JSON object to the objects you are compressing
# In this example, using a dictionary gave over 2x the compression ratio compared to not using a dictionary.
