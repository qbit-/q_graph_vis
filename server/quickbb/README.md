# QuickBB and tools
This is a convenience repository of the QuickBB program by Vibhav Gogate.
The original binary version is available [here](http://www.hlt.utdallas.edu/~vgogate/quickbb.html).
This repository provides a Dockerfile to build a minimal container to run quickbb on Mac OS X.
The script run_quickbb.sh can be used in the same way as the original binary.
The script starts a container of the image called qbit271/quickbb and passes all command line
arguments to it. The limitation is that the script expects all inputs and outputs to be written
in the current workdir.
The test file test.cnf is an input example of the SAT format. A more detailed description is
given in the file satformat.ps.

