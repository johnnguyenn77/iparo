# IPARO Implementation with IPFS

This repository contains a basic implementation of InterPlanetary Archival Record Objects (IPAROs) using IPFS. The implementation demonstrates the creation, storage, linking, and retrieval of IPAROs with two variations of linkages:

1. Each node links to all preceding nodes.
2. Each node only links to the prior node.

## Prerequisites

1. **IPFS**: Install IPFS and ensure it's running on your system. Follow the [IPFS installation guide](https://docs.ipfs.io/install/) for instructions (we recommend [IPFS Kubo](https://docs.ipfs.tech/install/command-line/)).
2. **Python**: Ensure Python is installed on your system. This repository uses Python 3.
3. **Virtual Environment**: Create a virtual environment and activate it

    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    ```

4. **Requests Library**: Install the prerequisites listed in the `requirements.txt` file.

   ```bash
   pip install -r requirements.txt
   ```

## Getting Started

### Clone the Repository

#### Clone this repository to your local machine

```bash
git clone https://github.com/johnnguyenn77/iparo.git
cd iparo
```

#### Running the Jupyter Notebook

Ensure you have Jupyter Notebook installed. If not, you can install it using:

```bash
pip install notebook
```

#### Launch the Jupyter Notebook

```bash
jupyter notebook
```

Open the `iparo.ipynb` notebook and follow the instructions to run the cells

## Contributors

Professor Mat Kelly [@machawk1](https://github.com/machawk1)\
Professor Sawood Alam [@ibnesayeed](https://github.com/ibnesayeed)\
John Nguyen [@johnnguyenn77](https://github.com/johnnguyenn77)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/johnnguyenn77/iparo#MIT-1-ov-file) file for details.