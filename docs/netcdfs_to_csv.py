import netCDF4 as nc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob

nc_file_path = "C:/Users/tag62/OneDrive/Desktop/precip_data"
csv_file_path = "C:/Users/tag62/Downloads/precip_data.csv"


def nc_to_csv(nc_file_path, csv_file_path, variables=None, target_lat=None, target_lon=None):
    """
    Convert NetCDF file(s) to CSV format.
    
    Parameters:
    -----------
    nc_file_path : str
        Path to a single NetCDF file OR a folder containing multiple .nc files
    csv_file_path : str
        Path to the output CSV file
    variables : list, optional
        List of variable names to extract. If None, extracts all variables.
    target_lat : float, optional
        Target latitude to extract. Will find nearest grid point.
    target_lon : float, optional
        Target longitude to extract. Will find nearest grid point.
    """
    
    # Check if input is a folder or a single file
    if os.path.isdir(nc_file_path):
        nc_files = sorted(glob.glob(os.path.join(nc_file_path, '*.nc')))
        if not nc_files:
            print(f"No .nc files found in folder: {nc_file_path}")
            return None
        print(f"Found {len(nc_files)} NetCDF files in folder")
        print("Files will be processed in order:")
        for f in nc_files:
            print(f"  - {os.path.basename(f)}")
        print()
    else:
        nc_files = [nc_file_path]
    
    # Process each file and collect all rows
    all_rows = []
    time_units, time_calendar = None, 'standard'

    for file_idx, nc_file in enumerate(nc_files):
        print(f"\n{'='*60}")
        print(f"Processing file {file_idx + 1}/{len(nc_files)}: {os.path.basename(nc_file)}")
        print(f"{'='*60}")

        rows_from_file, file_units, file_calendar = process_single_nc_file(
            nc_file, variables, target_lat, target_lon, show_full_info=(file_idx == 0))
        all_rows.extend(rows_from_file)

        # Every yearly file should share one time convention; warn if not.
        if time_units is None:
            time_units, time_calendar = file_units, file_calendar
        elif file_units != time_units:
            print(f"Warning: {os.path.basename(nc_file)} uses time units '{file_units}', "
                  f"expected '{time_units}'")
        print(f"Extracted {len(rows_from_file)} rows from this file")
    
    print(f"\n{'='*60}")
    print(f"TOTAL ROWS COLLECTED: {len(all_rows)}")
    print(f"{'='*60}\n")
    
    # Create DataFrame from all collected rows
    df = pd.DataFrame(all_rows)
    
    # Sort by time if time column exists
    if 'time' in df.columns:
        df = df.sort_values('time').reset_index(drop=True)
    
    # Convert time values to readable dates using the file's own time units
    if 'time' in df.columns:
        if time_units:
            print(f"Converting time values to dates (units: '{time_units}')...")
            dates = nc.num2date(df['time'].values, units=time_units, calendar=time_calendar,
                                only_use_cftime_datetimes=False,
                                only_use_python_datetimes=True)
            df['datetime'] = pd.to_datetime(dates)
            print(f"First date: {df['datetime'].iloc[0]}")
            print(f"Last date: {df['datetime'].iloc[-1]}")
        else:
            print("Time variable has no 'units' attribute; time values left as numbers")

    # Save to CSV
    df.to_csv(csv_file_path, index=False)
    print(f"Successfully saved combined data to {csv_file_path}")
    print(f"Output shape: {df.shape}")
    
    return df


def process_single_nc_file(nc_file_path, variables=None, target_lat=None, target_lon=None, show_full_info=True):
    """
    Extract rows from one NetCDF file (optionally at a single grid point).

    Parameters:
    -----------
    nc_file_path : str
        Path to the input NetCDF file
    variables : list, optional
        List of variable names to extract. If None, extracts all variables.
    target_lat : float, optional
        Target latitude to extract. Will find nearest grid point.
    target_lon : float, optional
        Target longitude to extract. Will find nearest grid point.
    """
    # Open the NetCDF file
    dataset = nc.Dataset(nc_file_path, 'r')
    
    # Print dataset information
    print("=" * 60)
    print("NETCDF DATASET INFORMATION")
    print("=" * 60)
    print("\nDimensions:")
    for dim_name, dim in dataset.dimensions.items():
        print(f"  {dim_name}: {len(dim)}")
    
    print("\nVariables:")
    for var_name, var in dataset.variables.items():
        print(f"  {var_name}:")
        print(f"    Shape: {var.shape}")
        print(f"    Dimensions: {var.dimensions}")
        print(f"    Data type: {var.dtype}")
        if hasattr(var, 'long_name'):
            print(f"    Description: {var.long_name}")
        if hasattr(var, 'units'):
            print(f"    Units: {var.units}")
    
    print("\n" + "=" * 60)
    print("Available variables:", list(dataset.variables.keys()))
    print("=" * 60 + "\n")
    
    # If no variables specified, use all non-dimension variables
    if variables is None:
        # Filter out coordinate/dimension variables
        dimensions = set(dataset.dimensions.keys())
        variables = [var for var in dataset.variables.keys() 
                    if var not in dimensions or len(dataset.variables[var].dimensions) > 1]
    
    # Find nearest lat/lon indices if specified
    lat_idx, lon_idx = None, None
    actual_lat, actual_lon = None, None
    
    if target_lat is not None or target_lon is not None:
        print("\n" + "=" * 60)
        print("FILTERING BY LOCATION")
        print("=" * 60)
        
        # Try to find latitude variable (various naming conventions)
        lat_var_name = None
        for name in ['lat', 'latitude', 'LAT', 'LATITUDE', 'y', 'Y']:
            if name in dataset.variables:
                lat_var_name = name
                break
        
        # Try to find longitude variable
        lon_var_name = None
        for name in ['lon', 'longitude', 'LON', 'LONGITUDE', 'x', 'X']:
            if name in dataset.variables:
                lon_var_name = name
                break
        
        if target_lat is not None and lat_var_name:
            lats = dataset.variables[lat_var_name][:]
            lat_idx = np.abs(lats - target_lat).argmin()
            actual_lat = float(lats[lat_idx])
            print(f"Target latitude: {target_lat}°")
            print(f"Nearest grid point: {actual_lat}° (index {lat_idx})")
            print(f"Using latitude variable: '{lat_var_name}'")
        
        if target_lon is not None and lon_var_name:
            lons = dataset.variables[lon_var_name][:]
            # Handle longitude wrapping (0-360 vs -180 to 180)
            if target_lon < 0 and lons.min() >= 0:
                target_lon_adjusted = target_lon + 360
                print(f"Adjusting longitude from {target_lon}° to {target_lon_adjusted}° (0-360 range)")
                lon_idx = np.abs(lons - target_lon_adjusted).argmin()
            else:
                lon_idx = np.abs(lons - target_lon).argmin()
            actual_lon = float(lons[lon_idx])
            print(f"Target longitude: {target_lon}°")
            print(f"Nearest grid point: {actual_lon}° (index {lon_idx})")
            print(f"Using longitude variable: '{lon_var_name}'")
        
        print("=" * 60 + "\n")
    
    # List to store all rows
    all_rows = []
    
    # Extract each variable
    for var_name in variables:
        if var_name in dataset.variables:
            var = dataset.variables[var_name]
            var_data = var[:]
            
            # Handle multi-dimensional arrays
            if var_data.ndim > 1:
                print(f"Processing {var_name} with shape {var_data.shape}")
                print(f"  Dimensions: {var.dimensions}")
                
                # Get coordinate variables
                dim_names = var.dimensions
                coords = {}
                for dim in dim_names:
                    if dim in dataset.variables:
                        coords[dim] = dataset.variables[dim][:]
                    else:
                        # Create indices if coordinate variable doesn't exist
                        coords[dim] = np.arange(dataset.dimensions[dim].size)
                
                # Map dimension names to standard names for filtering
                dim_name_map = {}
                for dim in dim_names:
                    if dim.lower() in ['lat', 'latitude', 'y']:
                        dim_name_map['lat'] = dim
                    elif dim.lower() in ['lon', 'longitude', 'x']:
                        dim_name_map['lon'] = dim
                
                # Slice data if lat/lon filtering is requested
                if lat_idx is not None and 'lat' in dim_name_map:
                    actual_dim = dim_name_map['lat']
                    lat_pos = dim_names.index(actual_dim)
                    var_data = np.take(var_data, lat_idx, axis=lat_pos)
                    dim_names = list(dim_names)
                    dim_names.pop(lat_pos)
                    dim_names = tuple(dim_names)
                    print(f"  Filtered to lat index {lat_idx}, new shape: {var_data.shape}")
                
                if lon_idx is not None and 'lon' in dim_name_map:
                    actual_dim = dim_name_map['lon']
                    lon_pos = dim_names.index(actual_dim)
                    var_data = np.take(var_data, lon_idx, axis=lon_pos)
                    dim_names = list(dim_names)
                    dim_names.pop(lon_pos)
                    dim_names = tuple(dim_names)
                    print(f"  Filtered to lon index {lon_idx}, new shape: {var_data.shape}")
                
                # Create a row for each data point
                if var_data.ndim == 1:
                    # After filtering, we have 1D data (e.g., just time series)
                    dim = dim_names[0]
                    coord_vals = coords[dim]
                    for i, val in enumerate(var_data):
                        row = {}
                        row[dim] = float(coord_vals[i])
                        row[var_name] = float(val)
                        if actual_lat is not None:
                            row['lat'] = actual_lat
                        if actual_lon is not None:
                            row['lon'] = actual_lon
                        all_rows.append(row)
                else:
                    # Still multi-dimensional after filtering
                    indices = np.ndindex(var_data.shape)
                    for idx in indices:
                        row = {}
                        # Add coordinate values
                        for i, dim in enumerate(dim_names):
                            row[dim] = float(coords[dim][idx[i]])
                        # Add filtered lat/lon values
                        if actual_lat is not None:
                            row['lat'] = actual_lat
                        if actual_lon is not None:
                            row['lon'] = actual_lon
                        # Add the variable value
                        row[var_name] = float(var_data[idx])
                        all_rows.append(row)
            else:
                # 1D data - simpler case
                print(f"Processing 1D variable {var_name}")
                for i, val in enumerate(var_data):
                    all_rows.append({var_name: val, 'index': i})
        else:
            print(f"Warning: Variable '{var_name}' not found in dataset")
    
    # Read the time axis's own units (e.g. "hours since 1900-01-01 00:00:00")
    # so dates are decoded exactly as the file defines them, instead of guessing
    # a reference date.
    time_units, time_calendar = None, 'standard'
    if 'time' in dataset.variables:
        time_units = getattr(dataset.variables['time'], 'units', None)
        time_calendar = getattr(dataset.variables['time'], 'calendar', 'standard')

    # Close the NetCDF file
    dataset.close()

    # Return the raw rows; nc_to_csv() combines every file and writes one CSV.
    return all_rows, time_units, time_calendar


# Example usage
if __name__ == "__main__":
    
    nc_file_path = "C:/Users/tag62/OneDrive/Desktop/precip_data"
    csv_file_path = "C:/Users/tag62/Downloads/precip_data.csv"

    # Process a folder of NetCDF files at a specific location
    nc_to_csv(nc_file_path, csv_file_path, target_lat=-0.9, target_lon=282.7)
    
    # Or process a single file
    # nc_to_csv('single_file.nc', 'output.csv', target_lat=-0.9, target_lon=-77.3)
    
    # Or specify specific variables
    # nc_to_csv('path/to/folder/', 'output.csv', variables=['precip'], 
    #           target_lat=-0.9, target_lon=-77.3)