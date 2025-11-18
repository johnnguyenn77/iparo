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
sh run-tests.sh
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

## Simulation

The simulation allows researchers to compare linking strategies and version densities to find the most efficient solutions for IPARO storage and retrieval.

To run the simulation, first ensure the proper pre-requisites are installed: 

```
pip install streamlit altair
```

To prepare the simulation, you must run `IPAROSimulationWriter.py`.

```
cd backend/src
python IPAROSimulationWriter.py [options]
```

To see the options for this command, run:
```
python IPAROSimulationWriter.py -h
```

If you want to run simulations, you should run:
```
sh run.sh
```
This should require no more than around 8 GB of RAM.
For the more memory-intensive simulations, you should run
```
sh run-huge.sh
```

**Please note that it will use a lot of memory (32 GB of RAM allocated to Linux is recommended). Both of the previous
two commands above will take a very long time to run.**

To start the simulation:
```
cd backend/src
streamlit run IPAROSimulation.py
```

## Changelog
**7-9-2025**: Renamed `tests.sh` to `run-tests.sh` and added a batch script `run.sh` for the simulation.
**6-4-2025**: Renamed tests with systems to start with `Sys`.
