# etl/column_mapper.py

def map_columns(df):
    """
    Auto-maps any uploaded dataset columns to a standard EV schema.

    Example:
        'brand' or 'manufacturer' → 'Manufacturer'
        'battery' or 'battery_size' → 'BatterykWh'
    """
    mapping = {
        "vehicleid": "VehicleID",
        "brand": "Manufacturer",
        "manufacturer": "Manufacturer",
        "model": "Model",
        "segment": "Segment",
        "battery": "BatterykWh",
        "battery_size": "BatterykWh",
        "range": "Rangekm",
        "price": "ExShowroomPriceINR",
        "cost": "OperatingCostINR",
        "revenue": "RevenueINR",
        "city": "City",
        "usage": "UsageType"
    }

    rename_cols = {}
    for col in df.columns:
        key = col.lower().replace(" ", "").replace("_", "")
        if key in mapping:
            rename_cols[col] = mapping[key]

    df.rename(columns=rename_cols, inplace=True)
    return df
