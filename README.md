# Intelligent Component Failure Forecasting
> Stay Ahead of Breakdowns
## About The Dataset And The Model
### Dataset
The LSTM model has been built and run seperately and not integrated within the application. The results of the model were interpreted by knowledge from the domain. The given dataset contains two files,
* The dataset itself
* Threshold values for the dataset
The dataset has been preprocessed and split into 5 subsequent datasets namely
  * Articulated_Truck
  * Asphalt_Paver
  * Backhoe_Loader
  * Dozer
  * Excavator
Each subsequent dataset has been further normalized. The normalized datasets can be found under ``` /static/normal.xlsx ```

The threshold file contains the threshold limit for each component and parameter individually, which are mapped and learned in the model.

### LSTM Model

LSTM models are particularly useful for predicting machine failures.<br><br>
**Time-Series Nature of Machine Data**: The data from heavy machinery typically involves time-series data, where the sequence and timing of events are crucial. LSTM models excel at capturing temporal dependencies, meaning they can understand how previous states influence future states.<br><br>
**Long-Term Dependencies**: Machinery failure can be influenced by patterns and events that occur over long periods.<br><br>
**Non-linear and Complex Relationships**: The relationship between different parameters and the likelihood of failure can be complex and non-linear.<br><br>
**Detecting Anomalies**: LSTMs can be trained to recognize normal operating patterns and detect deviations from these patterns, which can indicate potential failures.<br><br>
**Noise Handling**: LSTM models can handle noisy data better than traditional methods, which is often the case with sensor data from heavy machinery.

## Run Locally

Clone the project

```bash
  git clone https://github.com/lohithgsk/intelligent-component-failure-forecasting.git
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  flask run
```

## Feedback

If you have any feedback, please reach out to us at fake@fake.com



