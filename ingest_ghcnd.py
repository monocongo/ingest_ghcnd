import glob
import pandas as pd
import os

#-----------------------------------------------------------------------------------------------------------------------
def _generate_file_name(station_id):

    return str(station_id).ljust(23, '_') + '.txt'

#-----------------------------------------------------------------------------------------------------------------------
def _generate_ncmp_inventory(ghcnd_inventory_file):
    """
    Generates a NCMP station inventory file, returns a list of corresponding station file names.
    """
    
    # read the file into a pandas DataFrame
    column_specs = [(0, 12),     # ID
                    (12, 21),    # lat
                    (21, 31),    # lon
                    (31, 38),    # elevation
                    (39, 41),    # state
                    (41, 72)]    # name
    column_names = ['station_id',
                    'lat',
                    'lon',
                    'elev',
                    'state',
                    'name']
    df = pd.read_fwf(ghcnd_inventory_file, 
                     header=None,
                     colspecs=column_specs,
                     names=column_names,
                     usecols=['station_id', 'lat', 'lon', 'name'])
    
    station_files = []
    with open('C:/home/rstudio/wmo_ncmp/P0_Station_List.txt', 'w') as stations_file:
        for index, row in df.iterrows():
            station_file_name = _generate_file_name(row['station_id'])
            if len(station_file_name) != 27:
                raise ValueError('Incorrect file name length')
            stations_file.write(station_file_name + '   ' + str(row['lat']) + '  ' + str(row['lon']) + '\n')
            
#-----------------------------------------------------------------------------------------------------------------------
def _read_ghcnd(station_file,
                variable_name):
        
    # specify the fixed-width fields of a single line of data
    # these GHCN-D fields are described at https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
    column_specs = [(11, 15),    # year
                    (15, 17),    # month
                    (21, 26),    # value for day 1
                    (29, 34),    # value for day 2
                    (37, 42),    # value for day 3
                    (45, 50),    # value for day 4
                    (53, 58),    # value for day 5
                    (61, 66),    # value for day 6
                    (69, 74),    # value for day 7
                    (77, 82),    # value for day 8
                    (85, 90),    # value for day 9
                    (93, 98),    # value for day 10
                    (101, 106),  # value for day 11
                    (109, 114),  # value for day 12
                    (117, 122),  # value for day 13
                    (125, 130),  # value for day 14
                    (133, 138),  # value for day 15
                    (141, 146),  # value for day 16
                    (149, 154),  # value for day 17
                    (157, 162),  # value for day 18
                    (165, 170),  # value for day 19
                    (173, 178),  # value for day 20
                    (181, 186),  # value for day 21
                    (189, 194),  # value for day 22
                    (197, 202),  # value for day 23
                    (205, 210),  # value for day 24
                    (213, 218),  # value for day 25
                    (221, 226),  # value for day 26
                    (229, 234),  # value for day 27
                    (237, 242),  # value for day 28
                    (245, 250),  # value for day 29
                    (253, 258),  # value for day 30
                    (261, 266)]  # value for day 31
    
    # give some meaningful column names
    column_names = ['year', 'month',
                    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',  
                    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',  
                    '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',  '31']
       
    # read the file into a pandas DataFrame
    df = pd.read_fwf(station_file, 
                     header=None,
                     colspecs=column_specs,
                     names=column_names,
                     na_values=-9999)
    
    # melt the individual day columns into a single day column
    df = pd.melt(df,
                 id_vars=['year', 'month'],
                 value_vars=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                             '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                             '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'],
                 var_name='day', 
                 value_name=variable_name)

    # GHCND values are in tenths of mm for precipitation, and in tenths of degree Celsius for temperature
    # NCMP requires units in whole mm and degrees C so we divide the original GHCND values by 10
    df[variable_name] = df[variable_name] / 10.0
    
    return df
    
#-----------------------------------------------------------------------------------------------------------------------
def _write_ncmp_file(station_id, 
                     file_prcp, 
                     file_tmin, 
                     file_tmax):

    # get Pandas DataFrames for each variable
    df_prcp = _read_ghcnd(file_prcp, 'prcp')
    df_tmin = _read_ghcnd(file_tmin, 'tmin')
    df_tmax = _read_ghcnd(file_tmax, 'tmax')
        
    interim_df = pd.merge(df_prcp, df_tmax, on=['year', 'month', 'day'])
    final_df = pd.merge(interim_df, df_tmin, on=['year', 'month', 'day'])
              
    # write the data from the three DataFrames on each line of the output file
    file_name = 'C:/home/rstudio/wmo_ncmp/AO_Input_Data/' +_generate_file_name(station_id)
    
    final_df.to_csv(file_name, index=False, na_rep='-99.9', sep=' ', header=False)
        
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # get sorted list of GHCN-D station files for the three variables    
    files_prcp = sorted(glob.glob('C:/home/data/ghcnd/prcp/USW*.precip.dly'))
    files_tmin = sorted(glob.glob('C:/home/data/ghcnd/tmin/USW*.mintmp.dly'))
    files_tmax = sorted(glob.glob('C:/home/data/ghcnd/tmax/USW*.maxtmp.dly'))
    
    # write the station inventory file
    _generate_ncmp_inventory('C:/home/data/ghcnd/metadata/ghcn-d_short_jb.inv')
    
    if (len(files_prcp) != len(files_tmin)) or (len(files_prcp) != len(files_tmax)):
        raise ValueError('Non-matching sets of files')

    # loop over each station    
    for i in range(len(files_prcp)):
        
        file_prcp = files_prcp[i]
        file_tmin = files_tmin[i]
        file_tmax = files_tmax[i]
        
        # get the station IDs, make sure they're all in sync
        id_prcp = os.path.splitext(os.path.basename(file_prcp))[0].split('.')[0]
        id_tmin = os.path.splitext(os.path.basename(file_tmin))[0].split('.')[0]
        id_tmax = os.path.splitext(os.path.basename(file_tmax))[0].split('.')[0]
        if (id_prcp != id_tmin) or (id_prcp != id_tmax):
            raise ValueError('Non-matching files in file lists')
 
        # write the station's data into a single file suitable as input for WMO's NCMP software       
        _write_ncmp_file(id_prcp, file_prcp, file_tmin, file_tmax)