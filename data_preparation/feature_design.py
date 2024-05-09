import os
import pandas as pd
from datetime import date


## @Dilli what type of join to use in pd.merge
# For successive counts do we need to perform time step aggregates
# is it necessary to also filter by specific months (to control start/end of crop season)



def get_fortnight(date_str):
    month = date_str[4:6]
    day_of_month = int(date_str[6:])
    fortnight_number = (int(month) -1) * 2 
    if (day_of_month <= 15):
        return fortnight_number + 1
    else:
        return fortnight_number + 2


def get_dekad(date_str):
    day_= int(date_str[6:])
    if (day_ <= 10):
        return 1
    elif (day_ > 10) & (day_ <=20):
        return 2
    else:
        return 3



def temporal_resample(df, date_col, start_year, end_year, filter_months, time_step = "FORTNIGHT"):

    df = df.astype({date_col : str })
    df['YEAR'] = df[date_col].str[:4].astype(int)

    # convert to date and filter date
    df = df[(df['YEAR'] >= start_year) & (df['YEAR'] <= end_year)]

    if len(filter_months)> 0:
        df = df[df[date_col].str[4:6].astype(int).isin(filter_months)]

    if (time_step == "MONTH"):
        df["PERIOD"] = int(df[date_col].str[4:6])
    elif(time_step == "FORTNIGHT"):
        df["PERIOD"] = df.apply(lambda r: get_fortnight(r[date_col]), axis=1)
    elif (time_step == "DEKAD"):
        df["PERIOD"] = df.apply(lambda r: get_dekad(r[date_col]), axis=1)

    return df



def design_features(csv_path, 
                    date_col='DATE',
                    start_year=2010,
                    end_year=2015,
                    filter_months = [1,2,3],
                    time_step = 'FORTNIGHT', 
                    group_cols = ["IDREGION", "YEAR"],
                    max_feature_cols = ["FAPAR"], 
                    avg_feature_cols = ["FAPAR"],
                    count_threshold_cols = ['FAPAR'],
                    threshold=0.5,
                    threshold_exceed=True
                    ):

    """
    csv_path(str): path to time series table
    time_step(str): temporal span to perform aggregation
    group_col(list): cols to hold in grouping
    max_feature_cols(list): cols to generate max features acc. to timestep
    avg_feature_cols(list): cols to generate mean features acc. to timestep
    """

    df = pd.read_csv(csv_path, header=0)

    df = temporal_resample(df, date_col, start_year, end_year, filter_months, time_step)

    # designing features
    time_series_list = []
    count_threshold_list = []

    # time step aggregates
    group_cols = group_cols + ['PERIOD']
    if len(max_feature_cols)> 0:
        max_df = df.groupby(group_cols)[max_feature_cols].max().reset_index().rename(
            columns={col: col + '_max' for col in max_feature_cols})
        time_series_list.append(max_df)
        
    if len(avg_feature_cols) > 0:
        avg_df = df.groupby(group_cols)[avg_feature_cols].mean().reset_index().rename(
            columns={col: col + '_avg' for col in avg_feature_cols})
        time_series_list.append(avg_df)

    time_series_agg = pd.merge(time_series_list[0], pd.concat(time_series_list[1:]), on=group_cols)


    # # count the number of times values are greater than the threshold
    # if len(count_threshold_cols):
    #     for i in count_threshold_cols:
    #         filter_condition = (df[i] >= threshold) if threshold_exceed else (df[i] < threshold)
    #         count_threshold_df = df[filter_condition].groupby(group_cols)[count_threshold_cols].count().reset_index().rename(
    #                     columns={col: col + '_count' for col in count_threshold_cols})
    #         count_threshold_list.append(count_threshold_df)

    #     count_agg = pd.merge(count_threshold_list[0], pd.concat(count_threshold_list[1:]), on=group_cols)
            
    
    # return time_series_agg, count_agg

    return time_series_agg



# test
# rs_path = '/app/dev/AgML/feature_design/REMOTE_SENSING_NUTS2_NL.csv'#os.path.join("data", "REMOTE_SENSING_NUTS2_NL.csv")
# design_features(rs_path)

