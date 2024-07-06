import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout # type: ignore
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import tensorflow as tf


def prepare_data(data, look_back=30):
    data['DateTime'] = pd.to_datetime(data['Date'].astype(str) + ' ' + data['Time'].astype(str))
    data = data.sort_values('DateTime')

    pivot_data = data.pivot_table(index='DateTime', columns=['Component', 'Parameter'], values='Value', aggfunc='first')
    pivot_data.columns = [f'{col[0]}_{col[1]}' for col in pivot_data.columns]

    print("Columns with NaN values:", pivot_data.columns[pivot_data.isna().any()].tolist())
    print("NaN count before handling:", pivot_data.isna().sum().sum())

    pivot_data = pivot_data.fillna(method='ffill').fillna(method='bfill')

    print("NaN count after handling:", pivot_data.isna().sum().sum())

    relevant_columns = ['Engine_Speed', 'Engine_Oil Pressure', 'Engine_Temparature',
                        'Drive_Brake Control', 'Drive_Transmission Pressure', 'Drive_Pedal Sensor',
                        'Fuel_Water in Fuel', 'Fuel_Level', 'Fuel_Pressure', 'Fuel_Temparature',
                        'Misc_System Voltage', 'Misc_Exhaust Gas Temparature',
                        'Misc_Hydraulic Pump Rate', 'Misc_Air Filter Pressure']
    pivot_data = pivot_data[relevant_columns]

    if pivot_data.isna().sum().sum() > 0:
        print("Warning: There are still NaN values in the data.")
        print(pivot_data.isna().sum())
        pivot_data = pivot_data.dropna()

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(pivot_data)

    X, y = [], []
    for i in range(len(scaled_data) - look_back):
        X.append(scaled_data[i:(i + look_back), :])
        y.append(scaled_data[i + look_back, :])

    return np.array(X), np.array(y), scaler, pivot_data.columns

def predict_breakdown(model, last_sequence, scaler, thresholds, column_names, days_to_predict=30):
    predictions = []
    d = []
    col1 = []
    current_sequence = last_sequence.copy()

    for _ in range(days_to_predict):
        prediction = model.predict(current_sequence.reshape(1, current_sequence.shape[0], current_sequence.shape[1]))
        predictions.append(prediction[0])
        current_sequence = np.roll(current_sequence, -1, axis=0)
        current_sequence[-1] = prediction

    predictions = scaler.inverse_transform(np.array(predictions))

    breakdown_occurred = False


    for day, prediction in enumerate(predictions):
        if breakdown_occurred:
            break
        for i, col in enumerate(column_names):
            if col in thresholds:
                low, high = thresholds[col]
                if prediction[i] < low or prediction[i] >= high:
                    print(f"Potential breakdown on day {day+3} due to {col}: {prediction[i]}")
                    pred = prediction[i]
                    breakdown_occurred = True
                    return day, pred
    

def create_model(input_shape):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(input_shape[1])
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def train_and_evaluate_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = create_model((X.shape[1], X.shape[2]))
    history = model.fit(X_train, y_train, epochs=100, batch_size=32,
                        validation_data=(X_test, y_test), verbose=1)

    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    
    train_mse = mean_squared_error(y_train, train_predictions)
    test_mse = mean_squared_error(y_test, test_predictions)
    train_mae = mean_absolute_error(y_train, train_predictions)
    test_mae = mean_absolute_error(y_test, test_predictions)

    print(f"Train MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")
    print(f"Train MAE: {train_mae:.4f}, Test MAE: {test_mae:.4f}")

    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.show()

    return model,test_predictions

def perform_cross_validation(X, y, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_scores = []

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        model = create_model((X.shape[1], X.shape[2]))
        model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=0)

        score = model.evaluate(X_test, y_test, verbose=0)
        cv_scores.append(score)

    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV score: {np.mean(cv_scores):.4f}")

def sensitivity_analysis(model, X, scaler, thresholds, column_names):
    sensitivity = {}
    baseline_pred = model.predict(X[-1].reshape(1, X.shape[1], X.shape[2]))

    for i, col in enumerate(column_names):
        X_perturbed = X[-1].copy()
        X_perturbed[:, i] *= 1.2  # Increase by 10%
        perturbed_pred = model.predict(X_perturbed.reshape(1, X.shape[1], X.shape[2]))
        sensitivity[col] = np.mean(np.abs(perturbed_pred - baseline_pred))
    print("Feature sensitivities:")
    for col, sens in sorted(sensitivity.items(), key=lambda x: x[1], reverse=True):
        print(f"{col}: {sens:.4f}")

def check_feature_scaling(data):
    numerical_cols = data.select_dtypes(include=[np.number]).columns
    numerical_data = data[numerical_cols]

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(numerical_data)

    print("Scaled Data Statistics:")
    print(pd.DataFrame(scaled_data, columns=numerical_data.columns).describe())


data = pd.read_excel('Articulated_Truck_1.xlsx')
X, y, scaler, column_names = prepare_data(data)

print("X shape:", X.shape)
print("y shape:", y.shape)

print("NaN in X:", np.isnan(X).any())
print("NaN in y:", np.isnan(y).any())

if np.isnan(X).any() or np.isnan(y).any():
    print("Warning: There are still NaN values in X or y.")

model,test_predictions = train_and_evaluate_model(X, y)

#perform_cross_validation(X, y)
thresholds = { 'Engine_Oil Pressure': (25, 65),
    'Engine_Speed': (0, 1800),
    'Engine_Temparature': (0, 105),
    'Drive_Brake Control': (1, 9),
    'Drive_Pedal Sensor': (0, 4.7),
    'Fuel_Water in Fuel': (0, 1800),
    'Fuel_Level': (1, 10),
    'Fuel_Pressure': (35, 75),
    'Fuel_Temparature': (-1, 400),
    'Misc_System Voltage': (12, 15), #ed
    'Misc_Exhaust Gas Temparature': (0, 220), #ed
    'Misc_Hydraulic Pump Rate': (0, 125),
    'Misc_Air Filter Pressure': (15, 40)}

check_feature_scaling(data)
# Sensitivity analysis


# Define thresholds (as before)


# Predict breakdown
last_sequence = X[-1]
days_until_breakdown, failing_parameter = predict_breakdown(model, last_sequence, scaler, thresholds, column_names)



