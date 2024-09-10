import sys
import pandas as pd
from neuralprophet import NeuralProphet
# import matplotlib.pyplot as plt

# Read command-line arguments
input_file = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

# Define the forecast period
forecast_start_date = "2024-07-01 00:00"
forecast_end_date = "2024-08-20 23:00"

print(f"Loading dataset from {input_file}...")
# Load the dataset
df = pd.read_csv(input_file)

# Convert the 'ds' column to datetime format
df['ds'] = pd.to_datetime(df['Date']).dt.round('h')
df['y'] = df['PriceHU']
df = df.drop(columns=['Date', 'PriceHU'])
print(f"Dataset loaded with {len(df)} rows.")

# Filter the dataset based on the provided training date range
print(f"Filtering data for training from {start_date} to {end_date}...")
df_filtered = df[(df['ds'] >= start_date) & (df['ds'] <= end_date)]
print(f"Training dataset prepared with {len(df_filtered)} rows.")

# Initialize the NeuralProphet model with customized parameters
print("Initializing NeuralProphet model...")
model = NeuralProphet(
    growth="linear",
    n_changepoints=40,
    changepoints_range=0.95,
    trend_reg=0.1,
    trend_global_local="global",
    yearly_seasonality="auto",
    weekly_seasonality="auto",
    daily_seasonality="auto",
    seasonality_mode="additive",
    seasonality_reg=0.1,
    n_forecasts=504,
    learning_rate=0.005,
    epochs=1000,
    batch_size=1024,
    optimizer="AdamW",
    impute_missing=True,
    normalize="auto",
)

# Add future regressors and lagged regressors
print("Adding future regressors and lagged regressors to the model...")
# for col in df_filtered.columns:
#     if col not in ['ds', 'y']:
#         if 'lag_' in col:  # Identifying lagged columns
#             model = model.add_lagged_regressor(names=col)
#         else:
#             model = model.add_future_regressor(names=col)
for col in df_filtered.columns:
    if col not in ['ds', 'y']:
        model = model.add_future_regressor(names=col)

print("All future and lagged regressors added.")

# Train the model
print("Training the model...")
model.fit(df_filtered, freq='h')
print("Model training complete.")

# Prepare future dataframe for predictions
print(f"Preparing future dataframe for predictions from {forecast_start_date} to {forecast_end_date}...")
df_future = df[(df['ds'] >= forecast_start_date) & (df['ds'] <= forecast_end_date)].copy()
print(f"Future dataframe prepared with {len(df_future)} rows.")

# Ensure future regressors are available in df_future
if 'is_weekend' in df_future.columns:
    print("'is_weekend' values are correctly loaded for future dates.")

# Make predictions
print("Making predictions...")
forecast = model.predict(df_future)
print("Predictions completed.")

# Save the forecast to a CSV file
forecast_output_file = 'nProphet_forecast.csv'
forecast.to_csv(forecast_output_file, index=False)
print(f"Forecast results saved to {forecast_output_file}.")

print("Forecasting process completed successfully.")