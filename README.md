# Blockchain Cloud Computing Simulation

This repository contains a simulation framework for blockchain-based cloud storage systems. The project is structured to include the simulator, agent logic, and various simulation scenarios.

## Repository Structure

### 1. **Simulator**
   - **Location**: `ns-allinone-3.35/ns-3.35`
   - **Description**: This directory contains the NS-3 simulator, which is the core of the simulation framework. NS-3 is a discrete-event network simulator used to model and simulate network protocols and systems.

### 2. **Agents**
   - **Location**: `ns-allinone-3.35/ns-3.35/ParametrosNao_Aleatorios/Teoria_Racional_integrada/rust`
   - **Description**: This directory contains the logic for the agents participating in the simulation. Agents represent buyers and providers in the blockchain-based cloud storage system. Their behavior is defined in Python and Rust scripts.

### 3. **Simulations**
   - **Location**: `ns-allinone-3.35/ns-3.35/scratch`
   - **Description**: This directory contains the simulation scenarios. Each scenario is implemented as a script that defines the parameters and interactions between agents in the simulated environment.

## Installation Guide

### Prerequisites
- **Operating System**: Linux (recommended)
- **Dependencies**:
  - Python 3.8+
  - NS-3 simulator
  - Rust (for agent logic)
  - Required Python libraries: `pandas`, `matplotlib`, `seaborn`, `numpy`

### Steps to Install

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/GabD-S/Blockchain_CloudComputing.git
   cd Blockchain_CloudComputing
   ```

2. **Install NS-3 Simulator**:
   - Navigate to the NS-3 directory:
     ```bash
     cd ns-allinone-3.35
     ./build.py
     ```
   - Verify the installation:
     ```bash
     ./test.py
     ```

3. **Install Python Dependencies**:
   - Use `pip` to install the required libraries:
     ```bash
     pip install pandas matplotlib seaborn numpy
     ```

4. **Install Rust**:
   - Install Rust using `rustup`:
     ```bash
     curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     source $HOME/.cargo/env
     ```
   - Verify the installation:
     ```bash
     rustc --version
     ```

## Running the Simulations

1. **Prepare the Environment**:
   - Ensure all dependencies are installed.
   - Navigate to the NS-3 directory:
     ```bash
     cd ns-allinone-3.35/ns-3.35
     ```

2. **Run a Simulation**:
   - Use the `waf` tool to run a specific simulation script:
     ```bash
     ./waf --run scratch/<simulation_script>
     ```
     Replace `<simulation_script>` with the name of the desired script.

3. **Analyze Results**:
   - Use the Python scripts in `ParametrosNao_Aleatorios/Teoria_Racional_integrada/rust/Resultados` to analyze the output data:
     ```bash
     python analyze_racional_combined.py --all
     ```

## Notes
- Ensure that all paths are correctly set up before running the simulations.
- For detailed documentation on NS-3, refer to the [official NS-3 documentation](https://www.nsnam.org/documentation/).

---

Feel free to open an issue or contribute to the repository if you encounter any problems or have suggestions for improvement.