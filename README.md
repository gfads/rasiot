# 🌐 rasiot

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




