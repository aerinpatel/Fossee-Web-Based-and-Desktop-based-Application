import pandas as pd
import os

def analyze_csv(file_path):
    """
    Parses a telemetry CSV file and computes analytical summaries.
    
    This service performs the following operations:
    1. Validates presence of required industrial parameters.
    2. Handles missing values by applying safe procedural defaults.
    3. Calculates an 'Equipment Health Score' based on deviations from ideal operating parameters.
       - Ideal Flowrate: 50 | Pressure: 10 | Temperature: 60
    4. Aggregates data for distribution charts and telemetry correlation.
    
    Args:
        file_path (str): Absolute system path to the CSV file.
        
    Returns:
        dict: A structured dictionary containing mean values, distribution counts, 
              calculated health scores, and serialized equipment data.
              
    Raises:
        FileNotFoundError: If the provided path is invalid.
        ValueError: If mandatory columns are missing from the CSV.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
        
        # Standardize column names if needed or validate them
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        # Check if columns exist (case insensitive maybe?) - For now strict
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
             # Basic fallback or error, but let's assume valid for now or return error dict
             raise ValueError(f"Missing columns: {missing_cols}")

        # Fill missing numeric values with safe defaults to avoid NaN in calculations/JSON
        df['Flowrate'] = df['Flowrate'].fillna(50)
        df['Pressure'] = df['Pressure'].fillna(10) 
        df['Temperature'] = df['Temperature'].fillna(60)

        # Calculate Health Score (Mock Logic)
        # Assume ideal: Flowrate=50, Pressure=10, Temp=60
        df['Health_Score'] = 100 - (
            abs(df.get('Flowrate', 50) - 50) * 0.5 + 
            abs(df.get('Pressure', 10) - 10) * 2 + 
            abs(df.get('Temperature', 60) - 60) * 0.5
        )
        df['Health_Score'] = df['Health_Score'].clip(lower=0, upper=100).fillna(0)

        # Prepare equipment data with renamed columns
        renamed_df = df.rename(columns={
            'Equipment Name': 'name', 
            'Flowrate': 'flowrate', 
            'Pressure': 'pressure', 
            'Temperature': 'temperature',
            'Health_Score': 'health_score',
            'Type': 'type'
        })

        summary = {
            "total_equipment": len(df),
            "avg_flowrate": float(df["Flowrate"].mean()) if not df["Flowrate"].isnull().all() else 0.0,
            "avg_pressure": float(df["Pressure"].mean()) if not df["Pressure"].isnull().all() else 0.0,
            "avg_temperature": float(df["Temperature"].mean()) if not df["Temperature"].isnull().all() else 0.0,
            "avg_health_score": float(df['Health_Score'].mean()),
            "equipment_type_distribution": df["Type"].value_counts().to_dict(),
            "health_scores": df[['Equipment Name', 'Health_Score']].rename(columns={'Equipment Name': 'name', 'Health_Score': 'health_score'}).to_dict('records'),
            "equipment_data": renamed_df.where(pd.notnull(renamed_df), None).to_dict('records')
        }
        
        # Ensure numpy types are converted to python native types for JSON serialization
        # (Pandas to_dict handles most, but let's be safe for aggregations if passed raw)
        return summary
    except Exception as e:
        # Re-raise or handle gracefully
        raise e
