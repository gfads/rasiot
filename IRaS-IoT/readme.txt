This directory contains the files for running IRAS-IoT.

The solution was developed based on a fractal component approach, following the MAPE-K model.

📜 control_loop_battery_MLv08.py → Executes the full control loop and initialisation of IRAS-IoT.
⚙️ container_iot_features.py → Contains features such as automatic container management on Fog devices, instantiating containers to facilitate experiments. Includes the migration function, responsible for connecting to the Raspberries and executing start/remove commands.
🔋 consolida.py → Captures power consumption via powertop, along with the consolidar_cpu and consolidar_containere functions used by the Monitor to send data to the Analyser.
☁️ cloud_container_price_ck.py → Script responsible for collecting VM prices from cloud providers (Google Cloud, Microsoft Azure, AWS, and Contabo).

