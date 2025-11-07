# 🌐 IRAS-IoT

This repository describes the **IRAS-IoT** solution and the organisation of its directories.

---

## 📂 01 - IRaS-IoT  
This directory contains the files for running **IRAS-IoT**.  

The solution was developed based on a **fractal component** approach, following the **MAPE-K** model.  

- 📜 **control_loop_battery_MLv08.py** → Executes the full control loop and initialisation of IRAS-IoT.  
- ⚙️ **container_iot_features.py** → Contains features such as automatic container management on Fog devices, instantiating containers to facilitate experiments. Includes the **migration** function, responsible for connecting to the Raspberries and executing start/remove commands.  
- 🔋 **consolida.py** → Captures *power consumption* via **powertop**, along with the `consolidar_cpu` and `consolidar_containere` functions used by the **Monitor** to send data to the **Analyser**.  
- ☁️ **cloud_container_price_ck.py** → Script responsible for collecting VM prices from cloud providers (Google Cloud, Microsoft Azure, AWS, and Contabo).  

---

## 📊 02 - dataset_testing  
Contains the dataset used for **testing** the **MLP Neural Network** model.  
➡️ The corresponding script is in **mlp_testing_algorithm**.  

---

## 🧠 03 - dataset_training  
Contains the dataset used for **training** the **MLP Neural Network** model.  
➡️ The corresponding script is in **mlp_training_algorithm**.  

---

## 🧪 04 - experiments  
Contains the **120 experiment rounds**, divided into:  

- 🚫☁️ **No_cloud_No_IRAS-IoT** → 30 rounds without cloud (Fog only), IRAS-IoT disabled.  
- ✅☁️ **No_cloud_With_IRAS-IoT** → 30 rounds with Fog only, IRAS-IoT enabled.  
- ☁️🚫 **With_cloud_No_IRAS-IoT** → 30 rounds in a Fog-Cloud environment, IRAS-IoT disabled.  
- ☁️✅ **With_cloud_With_IRAS-IoT** → 30 rounds in a Fog-Cloud environment, IRAS-IoT enabled.  


🧪 05 - mlp_testing_algorithm

This directory includes the algorithm used to test the previously trained MLP model, aiming to evaluate the model’s accuracy and predictive performance.

🏋️‍♂️ 06 - mlp_training_algorithm

This directory includes the algorithm used to train the MLP model, selecting and processing the appropriate training data.


⚡ 07 - workload_script

Contains the scripts used to emulate workload generation during container creation and execution.

🧭 08 - greedy_heuristic_algorithm

Contains part the greedy heuristic algorithm used during the experimental phase to generate the dataset for training and testing the MLP model.
This algorithm applies a greedy decision logic to select the best and worst Fog devices based on CPU utilisation and battery level, triggering container migrations between devices as part of its decision process. These migrations are performed locally, without considering global optimisation, providing the empirical data later used to train the neural network model.


⚙️ General Instructions

To execute the IRAS-IoT algorithm, a Python IDE is required, along with essential libraries such as tensorflow.keras.models, shutil, and paramiko.

System tools like Sysstat and Powertop (Linux) were used to measure key metrics including CPU usage and power consumption.

