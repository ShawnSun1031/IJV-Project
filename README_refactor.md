# Installation Instructions
To install the IJV-Project, follow these steps:
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/IJV-Project.git
   ```
2. Navigate to the project directory:
   ```
   cd IJV-Project
   ```
3. Install the required dependencies:
   ```
   uv sync --locked
   ```
4. Activate virtual environment:
   ```
   source .venv/bin/activate  
   ```  

# Run MCX Simulation
To run the MCX simulation, execute the following command:
```
python src/ijv_project/mcx_simulation/main.py --config config/mcx_config.yaml
```