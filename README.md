# IPARO Implementation with IPFS

This repository contains a basic implementation of InterPlanetary Archival Record Objects (IPAROs) using IPFS based on a [proposal](https://github.com/johnnguyenn77/iparo/blob/main/proposal.pdf) by Dr. Sawood Alam. The implementation demonstrates the creation, storage, linking, and retrieval of IPAROs with different linking strategies.

## Prerequisites

1. **Python**: Ensure Python is installed on your system. This repository uses Python 3. For best results with testing, Python 3.11 or newer is recommended.
2. **Virtual Environment**: Create a virtual environment and activate it

    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    ```

3. **Prerequisites**: Install the prerequisites listed in the `requirements.txt` file.

   ```bash
   pip install -r requirements.txt
   ```

## Getting Started

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

4. **Running the Jupyter Notebook**

    Ensure you have Jupyter Notebook installed. If not, you can install it using:

    ```bash
    pip install notebook
    ```

5. **Launch the Jupyter Notebook**

    ```bash
    jupyter notebook
    ```

Open the `iparo.ipynb` notebook and follow the instructions to run the cells.

### Frontend Setup

The frontend provides an interactive implementation of the IPARO web archival system where users can view snapshots of archived website data or submit URLs for tracking.

1. **Navigate to Frontend Directory**

    ```bash
    cd frontend
    ```

2. **Install Dependencies and Start Server**

    ```bash
    npm install
    npm start
    ```

After a moment, the frontend server will be running on `localhost:3000`.

### Testing

1. **Navigate to Root Directory**

    ```bash
    cd iparo
    ```

2. **Install Dependecies and Run Test**

    ```
    pip install pytest
    PYTHONPATH=backend/src pytest backend/test/SysIPAROTest.py
    ```

## Contributors

### Stakeholders
Professor Mat Kelly [@machawk1](https://github.com/machawk1)\
Dr. Sawood Alam [@ibnesayeed](https://github.com/ibnesayeed)\
John Nguyen [@johnnguyenn77](https://github.com/johnnguyenn77)

### Team
Benji Bui [@qvbui02](https://github.com/qvbui02)
Alex Grigorian [@Alex651907](https://github.com/Alex651907)
Alexey Kuraev [@dg-off](https://github.com/dg-off)
Patrick Le [@21pxle](https://github.com/21pxle)
Thiyazan Qaissi [@tqdrex](https://github.com/tqdrex)


## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/johnnguyenn77/iparo#MIT-1-ov-file) file for details.
