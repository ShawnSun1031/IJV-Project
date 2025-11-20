# Installation Instructions
To install the IJV-Project, follow these steps:
1. Clone the repository:
   ```
   git clone https://github.com/ShawnSun1031/IJV-Project.git && \
   cd IJV-Project && \
   git switch refactor_v2
   ```
2. Install the required dependencies:
   ```
   uv sync --locked
   ```
3. Activate virtual environment:
   ```
   source .venv/bin/activate  
   ```  
4. Install PMCX:
   ```
   make install-pmcx
   ```

# Run MCX Simulation
To run the MCX simulation, execute the following command:
```
PYTHONPATH=src python src/ijv_project/mcx_simulation/main.py
```

# TODO
1. refactor mcx:  
    a. na for mcx runner [done]
    b. wmc (cupy implementation)  
    c. ultrasound image processing --> vol  
    d. optical parameter fitting from paper  
2. refactor surrogate modal
3. refactor prediction modal
4. refactor in-vivo exp
5. update readme
6. update docs
7. github ci/cd pipeline build up