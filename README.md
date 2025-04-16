# IPARO Implementation with IPFS

This repository contains a basic implementation of InterPlanetary Archival Record Objects (IPAROs) using IPFS based on a [proposal](https://github.com/johnnguyenn77/iparo/blob/main/proposal.pdf) by Dr. Sawood Alam. The implementation demonstrates the creation, storage, linking, and retrieval of IPAROs with different linking strategies.

## Prerequisites

1. **Python**: Ensure Python is installed on your system. This repository uses Python 3.
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

1. **Clone the Repository**

```bash
git clone https://github.com/johnnguyenn77/iparo.git
cd iparo
```

2. **Running the Jupyter Notebook**

Ensure you have Jupyter Notebook installed. If not, you can install it using:

```bash
pip install notebook
```

3. **Launch the Jupyter Notebook**

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

## Contributors

Professor Mat Kelly [@machawk1](https://github.com/machawk1)
Dr. Sawood Alam [@ibnesayeed](https://github.com/ibnesayeed)
John Nguyen [@johnnguyenn77](https://github.com/johnnguyenn77)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/johnnguyenn77/iparo#MIT-1-ov-file) file for details.
