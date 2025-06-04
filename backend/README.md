# Run Instructions
## Backend
To run the backend, install Kubo IPFS and then use
```
ipfs daemon
```
for setting up the backend. Then, run `app.py` in `src` to get the server running.
## Tests
For all the tests besides `IPFSDateTest` and `IPAROStrategyTest`, you can
run:
```
sh run.sh
```
Please note that this is only possible in the `backend` directory. To run an
individual test (including `IPFSDateTest` and `IPAROStrategyTest`), use
```
python -m unittest [module_name]
```
where `module_name` refers to the test module name which starts with `test` and
then the module name would be the name of the file, minus the `.py` extension.
For instance, if you want to run the tests in `SysIPFSDateTest.py`, then you would
use 

```
python -m unittest test.SysIPFSDateTest
```

Note: The `test.SysIPFSDateTest` tests are only supported on Python 3.11+.