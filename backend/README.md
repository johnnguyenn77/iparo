# Run Instructions
## Backend
### Backend Setup

1. **Clone the Repository and Install Requirements**

    ```bash
    git clone https://github.com/johnnguyenn77/iparo.git
    cd iparo
    ```

    Ensure that all prerequisites as listed in the `requirements.txt` file are installed.

   ```bash
   pip install -r requirements.txt
   ```

3. **Running the Backend**

   To run the backend, install [Kubo IPFS](docs.ipfs.tech/install/command-line/#install-official-binary-distributions) and then use
    ```
    ipfs daemon
    ```
    for setting up IPFS.

   Then, run `app.py` in `src` to get the server running:

   ```
   cd backend
   python src/app.py
   ```

    **NOTE:** First time setup may take up to 15-20 minutes. This is to be expected and is normal, as the backend must cache all of the archived sites and each snapshot, cached locally.
## Tests
For all the tests besides `SysIPFSDateTest` and `IPAROStrategyTest`, you can
run:
```
sh run.sh
```
Please note that this is only possible in the `backend` directory. To run an
individual test (including `SysIPFSDateTest` and `IPAROStrategyTest`), use
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

Note: The system tests are only supported on Python 3.11+ and you will need to install `warcio` to run them:
```
pip install warcio
```
## Changelog
**6-4-2025**: Renamed tests with systems to start with `Sys`.
