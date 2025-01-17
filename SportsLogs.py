## Import libraries:
## NOTE: 
## 20250109: Heart Rate (Real-Time) data-viz is retracted (commented)
##    due to the limited space. We'll proceed with the rest of vizzes
    
### Data Processing
import pandas as pd
import numpy as np
from functools import reduce
from datetime import date

### Data Visualization
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.patches import Patch

## Web-App Dashboarding
import streamlit as st

## Set the default:
    ## Web-app: Wide layout
    ## Viz style: Dark background
# st.set_page_config(layout='wide')
plt.style.use('dark_background')

## Putting list of players available right at beginning
id_players = ['p' + str(player).zfill(2) for player in np.arange(1, 17)]

# Functions:
    # @st.cache_data
    # <Function: Data Cleaning>
    
    # <Function: Data Visualization>
    ## Some changes: All data-viz function will end with 
    ##   st.pyplot(plt.gcf()) or st.pyplot(fig)
    
## Features available to: All and individual players
   
### `calories`: 
    ### Calories Burned per Month, Bar Chart

missing_file_lists = []

@st.cache_data
def clean_data_calories_per_month():

    df_calories = pd.DataFrame()

    for pXX in id_players:

        calories_pXX = pd.read_json(f"{pXX}/fitbit/calories.json")
        calories_pXX['pXX'] = pXX
        df_calories = pd.concat([df_calories, calories_pXX])

    df_calories['date']  = df_calories['dateTime'].dt.date
    df_calories['yearmonth'] = df_calories['dateTime'].dt.month + df_calories['dateTime'].dt.year * 100
    df_calories = df_calories.rename(columns={'value': 'calories'})
    df_calories['calories'] /= 1000 # Convert distances from cal to kcal

    df_cals = df_calories.groupby(['pXX', 'yearmonth'])['calories'].sum().reset_index()
    df_cals['yearmonth'] = pd.to_datetime(df_cals['yearmonth'], format="%Y%m") #.strftime('%Y-%m-%d')

    return df_cals

def calories_per_month_bar_chart_pXX(player='all'):
    
    if player == 'all':
        sns.catplot(data=df_cals, x='pXX', y='calories', hue='yearmonth', 
        kind='bar', height=8.27, aspect=11.7/8.27) #._legend.remove()
        plt.grid(alpha=0.4)
        plt.title('Calories Burned per Month (in kcal), All Players',
            fontsize=20, fontweight='bold')
        st.pyplot(plt.gcf())
    
    else:
        sns.catplot(data=df_cals.loc[df_cals['pXX'] == player], 
        x='pXX', y='calories', hue='yearmonth', kind='bar', 
        height=3.2, aspect=8/8)
        plt.grid(alpha=0.4)
        plt.title(f'Calories Burned per Month (in kcal), {player}',
            fontsize=15, fontweight='bold')
        st.pyplot(plt.gcf())
        
### `distance`: 
    ### Distances per Month, Bar Chart

@st.cache_data
def clean_data_distances_per_month():

    df_distances = pd.DataFrame()

    for pXX in id_players:

        distance = pd.read_json(f"{pXX}/fitbit/distance.json")
        distance['pXX'] = pXX
        df_distances = pd.concat([df_distances, distance])

    df_distances['yearmonth'] = df_distances['dateTime'].dt.month + df_distances['dateTime'].dt.year * 100
    df_distances = df_distances.rename(columns={'value': 'distances'})
    df_distances['distances'] /= 100000 # Convert distances from cm to km
    
    df_dists = df_distances.groupby(['pXX', 'yearmonth'])['distances'].sum().reset_index()
    df_dists['yearmonth'] = pd.to_datetime(df_dists['yearmonth'], format="%Y%m")

    return df_dists

def distance_per_month_bar_chart_pXX(player='all'):
    
    if player == 'all':
        sns.catplot(data=df_dists, x='pXX', y='distances', hue='yearmonth', 
            kind='bar', height=8.27, aspect=11.7/8.27) #._legend.remove()
        plt.grid(alpha=0.4)
        plt.title('Distances Walked per Month (in km), the Whole Team',
            fontsize=20, fontweight='bold')
        st.pyplot(plt.gcf())
        
    else:    
        sns.catplot(data=df_dists.loc[df_dists['pXX'] == player], 
        x='pXX', y='distances', hue='yearmonth', kind='bar', 
        height=3.2, aspect=8/8)
        plt.grid(alpha=0.4)
        plt.title(f'Distances Walked per Month (in km), {player}',
            fontsize=15, fontweight='bold')
        st.pyplot(plt.gcf())
 
        
### `sleep_score`: 
    ### Sleep Quality, Pie Chart

@st.cache_data
def clean_data_sleep_score():
    
    df_sleep_score = pd.DataFrame()
    
    for pXX in id_players:
        sleep_score_pXX = pd.read_csv(f"{pXX}/fitbit/sleep_score.csv")
        sleep_score_pXX['pXX'] = pXX
        df_sleep_score = pd.concat([df_sleep_score, sleep_score_pXX])
    
    ## After more exploring, the typical ranges of sleep quality include:
    ## Excellent: 90-100, Good: 80-89, Fair: 60-79, Poor: <60
    ## Most users on average score between 72 and 83.

    conditions = [(df_sleep_score['overall_score'] >= 90), 
        (df_sleep_score['overall_score']  < 90) & (df_sleep_score['overall_score'] >= 80),
        (df_sleep_score['overall_score']  < 80) & (df_sleep_score['overall_score'] >= 60),
        (df_sleep_score['overall_score']  < 60)]

    choices = ['Excellent', 'Good', 'Fair', 'Poor']
    
    df_sleep_score['sleep_quality'] = np.select(conditions, choices, default='Unknown')
    
    return df_sleep_score


def sleep_quality_pie_chart_pXX(player='all'):
    
    if player == 'all':
        sleep_quality_grouped_pXX = pd.DataFrame(
            df_sleep_score.value_counts(
                'sleep_quality')).reset_index()        
        
    else:    
        sleep_quality_grouped_pXX = pd.DataFrame(
            df_sleep_score[df_sleep_score['pXX'] == player]
            .value_counts('sleep_quality')).reset_index()
    
    explode = (0, 0.05, 0.1, 0.15)
    sq_colors = {'Excellent': '#FFC000', 
                 'Good': '#018230',
                 'Fair': '#015482',  
                 'Poor': '#FE251B'}
    fmt_title = ('The Whole Team' if player == 'all' else player)

    fig, ax = plt.subplots(figsize=(12, 7.5))
    n_sq = sleep_quality_grouped_pXX.shape[0]

    ax.pie(sleep_quality_grouped_pXX['count'], explode=explode[:n_sq],
        labels=sleep_quality_grouped_pXX['sleep_quality'], 
        textprops={'fontsize': 15}, autopct='%1.2f%%', 
        startangle=-135, colors=[sq_colors[key] for key in 
               sleep_quality_grouped_pXX['sleep_quality']])
    
    ax.axis('equal')
    ax.set_title(f'Sleep Quality of {fmt_title}',
        fontsize=20, fontweight='bold')
    st.pyplot(fig)


### `exercise`: 
    ### Sports Activities, Pie Chart

@st.cache_data
def clean_data_exercise():

    df_exercises = pd.DataFrame()

    for pXX in id_players:
        exercises_team = pd.read_json(f"{pXX}/fitbit/exercise.json")
        exercises_team['pXX'] = pXX
        df_exercises = pd.concat([df_exercises, exercises_team])
        
    act_level = pd.json_normalize(df_exercises['activityLevel'])    

    act_level_prefixes = [
        'sedentary_', 'lightly_active_', 
        'moderately_active_', 'very_active_']

    for i in range(4):
        act_level = act_level.join(
            pd.json_normalize(act_level[i])
              .drop('name', axis=1)
              .add_prefix(f'{act_level_prefixes[i]}')
        ).drop(columns=[i])

    ## Flattening `manualValuesSpecified`
    manual_values_check = pd.json_normalize(df_exercises['manualValuesSpecified'])
    manual_values_check = manual_values_check.add_prefix('manual_check_')

    hrz = pd.json_normalize(df_exercises['heartRateZones'])

    hrz_prefixes = ['oor', 'fb', 'cardio', 'peak']

    for i in range(4):
        hrz = (hrz.join(
                pd.json_normalize(hrz[i])
                  .drop('name', axis=1)
                  .add_prefix(f'{hrz_prefixes[i]}_HR_')
              )).drop(columns=[i])

    col_sequences = (
        list(df_exercises.columns[0:2]) + 
        list(act_level.columns) + 
        list(df_exercises.columns[4:9]) + 
        list(manual_values_check.columns) +
        list(hrz.columns) +
        list(df_exercises.columns[12:]))

    ## Combining flattened columns
    df_exercises = (df_exercises
        .join([act_level, manual_values_check, hrz]))

    df_exercises = df_exercises.drop(
        ['activityLevel', 'manualValuesSpecified', 'heartRateZones'], axis=1)
    df_exercises = df_exercises.reindex(columns = col_sequences)

    df_exercises['dateTime'] = pd.to_datetime(pd.to_datetime(df_exercises['startTime']).dt.date)
        
    return df_exercises


## Sequence colors from dataframe, mapped by the sports

# explode = (0, 0.1, 0.15)
sa_colors = {
    'Walk': '#32CD32', 
    'Run': '#FF4500', 
    'Treadmill': '#FFA500',
    'Outdoor Bike': '#1E90FF', 
    'Sport': '#FFD700',
    'Weights': '#8B4513', 
    'Workout': '#FF69B4', 
    'Aerobic Workout': '#EE82EE', 
    'Hike': '#228B22',
    'Bike': '#87CEEB',
    'Spinning': '#6A5ACD',
    'Elliptical': '#4682B4',
    'Cross Country Skiing': '#B0E0E6',
    'Swim': '#40E0D0',
    'Circuit Training': '#FFDAB9',
    'Interval Workout': '#FF6347',
    'Yoga': '#800080',
    'Hockey': '#A9A9A9',
    'Skiing': '#F0F8FF',
    'Tennis': '#FFFF00',
    'Dancing': '#FF1493'
}

sports_activities = pd.DataFrame()

def sport_activities_pie_chart_pXX(player='all'):

    fig, ax = plt.subplots(figsize=(12, 7.5))
    autopct = lambda v: f'{v:.2f}%' if v > 3 else None
    
    if player == 'all':
        title = 'Sport Activities, the Whole Team'
        sports_activities = pd.DataFrame(df_exercises
            .value_counts(['activityName'])).reset_index()
    else:
        title = f'Sport Activities of Player {player}'
        sports_activities = pd.DataFrame(
            df_exercises.loc[df_exercises['pXX'] == player]
            .value_counts(['activityName'])).reset_index()

    ax.pie(sports_activities['count'], pctdistance=0.55,
        textprops={'fontsize': 16}, autopct=autopct, 
        startangle=-112.5, colors=[sa_colors[key] for key in 
           sports_activities['activityName']])
    ax.axis('equal')
        
    ax.set_title(title, fontsize=20, fontweight='bold')
    ax.legend(sports_activities['activityName'], 
        bbox_to_anchor=(0.825, 1.025))#, loc='center right')

    st.pyplot(fig)


## FEATURES AVAILABLE TO: ONLY INDIVIDUAL PLAYERS


### `resting_heart_rate`:
    ### Resting Heart Rate per Player, Line Chart

@st.cache_data
def clean_data_resting_heart_rate():
    '''
    Note: Several players had a late start and
          missing values, visualized by value of 0
    '''
    
    df_RHR = pd.DataFrame()
    
    for pXX in id_players:
        try:        
            
            RHR_pXX = pd.read_json(f"{pXX}/fitbit/resting_heart_rate.json")
            RHR_pXX = RHR_pXX.rename(columns={"value": "rhr"})

            RHR_pXX = (RHR_pXX.join(pd.json_normalize(RHR_pXX['rhr']))
              .drop(["rhr", "date"], axis=1).rename(columns={
                  "value": "resting_hr","error": "error_std"}))
            RHR_pXX['pXX'] = pXX

            df_RHR = pd.concat([df_RHR, RHR_pXX])
            
        except FileNotFoundError:
            miss = f"File not found: {pXX}/fitbit/resting_heart_rate.json -- Skipping..."
            print(miss)
            missing_file_lists.append(miss)
    
    return df_RHR


def resting_heart_rate_line_chart_pXX(player='p01'):

    if player == 'p12' or player == 'p13':
        print(f"Resting heart rate data for {player} is not found.")
    
    else:
        fig, ax = plt.subplots(figsize=(12, 6))

        RHR_pXX = df_RHR.loc[df_RHR['pXX'] == player]

        ax.plot(RHR_pXX['dateTime'], RHR_pXX['resting_hr'], 
            label='Average Resting HR', 
            color='salmon', linewidth=2)
        ax.fill_between(RHR_pXX['dateTime'],
            RHR_pXX['resting_hr'] - RHR_pXX['error_std'],
            RHR_pXX['resting_hr'] + RHR_pXX['error_std'],
            color='lightcoral', alpha=0.2, label='Standard Deviation')

        ax.set_title(f'Resting Heart Rate, {player}', 
            fontsize=15, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Resting Heart Rate (bpm)', fontsize=12)
        ax.grid(alpha=0.2)
        ax.legend(loc='best', fontsize=12)
        ax.set_ylim(0, 100)

        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
        

### `exercise`: 
    ### Active Metrics per Sport, Stacked Bar Chart

def active_metrics_per_sport_stacked_bar_chart_pXX(player):

    df_exercises_selected_cols = (
        ['pXX', 'dateTime', 'activityName'] +
        list(df_exercises.columns[
          df_exercises.columns.str
            .endswith('_minutes')])
    )

    df_e_stats = df_exercises.loc[:, df_exercises_selected_cols]
    df_e_stats['yearmonth'] = pd.to_datetime(
        df_e_stats['dateTime'].dt.year * 100 + 
        df_e_stats['dateTime'].dt.month, format="%Y%m")

    df_active_mins_cols = list(df_e_stats.columns[3:7])
    df_HR_zones_cols    = list(df_e_stats.columns[7:11])

    metrics_pXX = (df_e_stats[df_e_stats['pXX'] == player]
         .drop(['pXX', 'dateTime'], axis=1)
         .groupby(['activityName', 'yearmonth']).agg('sum')
    )

    ## Reindex the df so that every data per month
    ## includes all sports of one player, as in general
    ## a player does some sports in one month, but not the other.
    ## We'll fill the empty values (^) with 0.
    new_index = pd.MultiIndex.from_product(
        iterables=metrics_pXX.index.levels,
            names=metrics_pXX.index.names)

    metrics_pXX = (metrics_pXX.reindex(new_index, fill_value=0))

    ## Unstack the df for data-viz purposes, and 
    ## sort columns of sports to order the stacked bar descendingly
    ## Side note: Choosing February '20 instead of March '20 since
    ##    some players have missing values on the last month
    metrics_pXX = metrics_pXX.unstack().sort_values(
        [('very_active_minutes', '2020-02-01')], ascending=False).T

    metrics_pXX = (metrics_pXX.reset_index(level=0)
        .rename(columns={'level_0': 'metrics'}))

    metrics_pXX.index = metrics_pXX.index.strftime('%Y-%m-%d')

    ## Visualize: 1x4 stacked bar chart, 
    ## each metric displayed with color as sport

    active_titles = [
                'Sedentary Minutes', 'Lightly Active Minutes', 
        'Moderately Active Minutes', 'Very Active Minutes'
    ]             
    HRZ_titles    = [
        'HR Zones 0: Out of Range', 'HR Zones 1: Fat Burn', 
        'HR Zones 2: Cardio'      , 'HR Zones 3: Peak'
    ]

    fig1 = plt.figure(figsize=(12, 6))
    gs1  = fig1.add_gridspec(1, 4, wspace=0)
    axs1 = gs1.subplots(sharex=False, sharey=True)
    fig1.suptitle(
        f'Active Minutes in All Sports, {player}', 
        fontsize=15, fontweight='bold')

    for i, col in enumerate(df_active_mins_cols):
        metrics_pXX.loc[metrics_pXX['metrics'] == col].plot(
            kind='bar', stacked=True, ax=axs1[i], width=0.8,
            color=[sa_colors[key] for key in metrics_pXX.columns[1:]])

        axs1[i].set_title(active_titles[i])
        axs1[i].set_xlabel('')

        ## Put legend only at first axes to put up some space
        if i == len(df_active_mins_cols) - 1:
            axs1[i].legend(bbox_to_anchor=(1.8, 1), frameon=False)
        else:
            axs1[i].legend().set_visible(False)

    fig1.autofmt_xdate()    
    st.pyplot(fig1)

    fig2 = plt.figure(figsize=(12, 6))
    gs2  = fig2.add_gridspec(1, 4, wspace=0)
    axs2 = gs2.subplots(sharex=False, sharey=True)
    fig2.suptitle(
        f'HR Zones Duration in All Sports, {player}',
        fontsize=15, fontweight='bold')

    for i, col in enumerate(df_HR_zones_cols):
        metrics_pXX.loc[metrics_pXX['metrics'] == col].plot(
        kind='bar', stacked=True, ax=axs2[i], width=0.8,
        color=[sa_colors[key] for key in metrics_pXX.columns[1:]])

        axs2[i].set_title(HRZ_titles[i])
        axs2[i].set_xlabel('')

        ## Put legend only at first axes to put up some space
        if i == len(df_HR_zones_cols) - 1:
            axs2[i].legend(bbox_to_anchor=(1.8, 1), frameon=False)
        else:
            axs2[i].legend().set_visible(False)
    
    fig2.autofmt_xdate() 
    st.pyplot(fig2)
    
    
### `srpe`:
    ### Session Rating of Perceived Exertion in All Sports of a Player, Boxplot
    
@st.cache_data
def clean_data_srpe():

    df_srpe = pd.DataFrame()

    for pXX in id_players:

        srpe_pXX = pd.read_csv(f"{pXX}/pmsys/srpe.csv")
        srpe_pXX['pXX'] = pXX
        df_srpe = pd.concat([df_srpe, srpe_pXX])

    df_srpe['date'] = pd.to_datetime(df_srpe['end_date_time']).dt.date
    df_srpe['srpe'] = df_srpe['perceived_exertion'] * df_srpe['duration_min']

    activity = pd.DataFrame(df_srpe['activity_names']
        .str.split(', ', n=1, expand=True)
            .replace("'|\[|\]| {}", "", regex=True))
    activity.columns = ['type_of_activity', 'activity_name']

    for col in activity.columns:
        activity[col] = activity[col].str.title()

    df_srpe = pd.concat([df_srpe, activity], axis=1)

    return df_srpe

## p16 has no data. We'll put notice in the data-viz function.

def srpe_per_sport_boxplot_pXX(player):
    
    if player == 'p16':
        with st.container(height=50):
            st.write('p16 has no data of SRPE.')
    
    else:
        df_srpe_cleaned_pXX = df_srpe.loc[
            df_srpe['pXX'] == player, df_srpe.columns[-4:]]
        
        fig, ax = plt.subplots(figsize=(12, 6))
                
        df_srpe_cleaned_pXX.drop('date', axis=1).boxplot(
            column='srpe', by=['type_of_activity', 'activity_name'],
            patch_artist=True, ax=ax, medianprops=dict(
                linestyle='-', linewidth=2.5, color='chocolate'),
                whiskerprops=dict(linewidth=3.5))
                
        ax.set_title(f'SRPE by Sport Activities, {player}',
            fontsize=15, fontweight='bold') 
        ax.get_figure().suptitle('')
        
        ax.grid(alpha=0.2)
        ax.set_xlabel('(Type of Activity, Activity Name)')
        ax.set_ylabel('Session Rating of Perceived Exertion (SRPE)')
        ax.set_xticklabels(ax.get_xticklabels(),
            rotation=30, ha='right')
            
        st.pyplot(plt.gcf())
        
    
### `hrz`:
    ### Heart Rate Zones in Real-Time, Stacked Bar Chart

@st.cache_data
def clean_data_hrz():

    df_hrz_in_mins = pd.DataFrame()

    for pXX in id_players:
        hrz_in_mins_pXX = pd.read_json(f"{pXX}/fitbit/time_in_heart_rate_zones.json")
        hrz_in_mins_pXX['pXX'] = pXX
        df_hrz_in_mins = pd.concat(
            [df_hrz_in_mins, hrz_in_mins_pXX])
        
    ## Column names following the sequence
    df_hrz_col_names = ['dateTime', 'pXX',
        'HRZ_oor_in_minutes', 'HRZ_fb_in_minutes', 
        'HRZ_cardio_in_minutes', 'HRZ_peak_in_minutes']
    
    ## Dropping new columns on the block
    df_hrz_cols_to_drop = ['value',
        'valuesInZones.ABOVE_CUSTOM_ZONE',
        'valuesInZones.BELOW_CUSTOM_ZONE',
        'valuesInZones.IN_CUSTOM_ZONE']
    
    df_hrz_in_mins = df_hrz_in_mins.join(
        pd.json_normalize(df_hrz_in_mins['value']))
       
    df_hrz_in_mins = df_hrz_in_mins.drop(
        df_hrz_cols_to_drop, axis=1).sort_index(axis=1)
    df_hrz_in_mins.columns = df_hrz_col_names

    # df_hrz_in_mins = df_hrz_in_mins.set_index('dateTime')
    return df_hrz_in_mins

def hrz_bar_chart_pXX(player='p01', startfromzone=0):
    
    ''' Options of 'startfromzone': 
           0: 'oor', 1: 'fb', 2: 'cardio', 3: 'peak' '''
    
    hrz_weekly_pXX = (df_hrz_in_mins[
        df_hrz_in_mins['pXX'] == player].groupby([pd.Grouper
        (key='dateTime', freq='W-Thu')]).agg('sum'))
    hrz_weekly_pXX.index = hrz_weekly_pXX.index.strftime('%Y-%m-%d')
    
    HR_zones_color = [
        '#FFFF7D', '#FF9D1C', '#FF6D1C', '#FE251B']
    
    fig, ax = plt.subplots(figsize=(12, 6))

    hrz_labels = [
        'HR Zone 0: Out of Range', 'HR Zone 1: Fat Burn',
        'HR Zone 2: Cardio'      , 'HR Zone 3: Peak'
    ]

    hrz_cols_to_drop = (['pXX'] + hrz_weekly_pXX.columns
                        .to_list()[:startfromzone+1])
    
    hrz_labels_loc = 'lower left' if startfromzone == 0 else 'best'
    
    hrz_weekly_pXX.drop(hrz_cols_to_drop, axis=1).plot(
        kind='bar', stacked=True, width=0.8, ax=ax, 
        color=HR_zones_color[startfromzone:])
    ax.set_title(f'HR Zones per Week, {player} (updated every Thursday)',
        fontsize=15, fontweight='bold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Duration (mins)')
    ax.legend(labels=hrz_labels[startfromzone:], loc=hrz_labels_loc)
    ax.grid(alpha=0.4)
    fig.autofmt_xdate()
    
    st.pyplot(fig)
    
    
### `active_mins`:
    ### Count Missing Values in Data, Styled Table
    ### Active Minutes in Real-Time, Stacked Bar Chart

@st.cache_data
def clean_data_active_minutes():
    
    df_sms = pd.DataFrame()
    df_lams = pd.DataFrame()
    df_mams = pd.DataFrame()
    df_vams = pd.DataFrame()
    df_steps = pd.DataFrame()
    df_steps_per_day = pd.DataFrame()
    
    df_active_steps_pXX = pd.DataFrame()

    for pXX in id_players:

        try:
            sms_pXX = pd.read_json(f"{pXX}/fitbit/sedentary_minutes.json")
            sms_pXX = sms_pXX.rename(columns={'value': 'sedentary_minutes'})
            sms_pXX['pXX'] = pXX
            df_sms = pd.concat([df_sms, sms_pXX])
        except FileNotFoundError:
            miss = f"File not found: {pXX}/fitbit/sedentary_minutes.json -- Skipping..."
            print(miss)
            missing_file_lists.append(miss)
            
        try:
            lams_pXX = pd.read_json(f"{pXX}/fitbit/lightly_active_minutes.json")
            lams_pXX = lams_pXX.rename(columns={'value': 'lightly_active_minutes'})
            lams_pXX['pXX'] = pXX
            df_lams = pd.concat([df_lams, lams_pXX])
        except FileNotFoundError:
            miss = f"File not found: {pXX}/fitbit/lightly_active_minutes.json -- Skipping..."
            print(miss)
            missing_file_lists.append(miss)

        try:
            mams_pXX = pd.read_json(f"{pXX}/fitbit/moderately_active_minutes.json")
            mams_pXX = mams_pXX.rename(columns={'value': 'moderately_active_minutes'})
            mams_pXX['pXX'] = pXX
            df_mams = pd.concat([df_mams, mams_pXX])
        except FileNotFoundError:
            miss = f"File not found: {pXX}/fitbit/moderately_active_minutes.json -- Skipping..."
            print(miss)
            missing_file_lists.append(miss)

        try:
            vams_pXX = pd.read_json(f"{pXX}/fitbit/very_active_minutes.json")
            vams_pXX = vams_pXX.rename(columns={'value': 'very_active_minutes'})
            vams_pXX['pXX'] = pXX
            df_vams = pd.concat([df_vams, vams_pXX])
        except FileNotFoundError:
            miss = f"File not found: {pXX}/fitbit/very_active_minutes.json -- Skipping..."
            print(miss)
            missing_file_lists.append(miss)

        try:
            steps_pXX = pd.read_json(f"{pXX}/fitbit/steps.json")
            steps_pXX['date'] = steps_pXX['dateTime'].dt.date
            steps_pXX['pXX'] = pXX
            df_steps = pd.concat([df_steps, steps_pXX])
        except FileNotFoundError:
            miss = f"{pXX}/fitbit/steps.json -- Skipping..."
            print(miss)
            missing_file_lists.append(miss)
            
    df_steps_per_day = (df_steps.drop('dateTime', axis=1)
    .groupby(['pXX', 'date']).agg('sum').reset_index()
    .rename(columns={'date': 'dateTime', 'value':'num_steps'})
    )

    active_dfs_pXX = [df_steps_per_day, 
          df_sms, df_lams, df_mams, df_vams]

    for active_df in active_dfs_pXX:
        # Changing columns of dateTime to str so we can go for pd.merge.
        # Since there are chances a file is missing, doing pd.concat
        # would not put the missing files at place (NaN)
        active_df['dateTime'] = active_df['dateTime'].astype('str')

    df_active_steps_pXX = reduce(
        lambda left, right: pd.merge(left, right, how='outer',
            on=['pXX', 'dateTime']), active_dfs_pXX)
    
    df_active_steps_pXX = df_active_steps_pXX.sort_values(['pXX', 'dateTime'])
    df_active_steps_pXX['dateTime'] = pd.to_datetime(df_active_steps_pXX['dateTime'])
    
    return df_active_steps_pXX


def active_minutes_bar_chart_pXX(player='p01', num_steps=True, startfromzone=0):

    '''
    Parameters:
    - player: Number of player
    - withstep: Displaying charts: number_of_step
    - startfromzone: [0, 1, 2, 3] as in sequence of:
        [sedentary_minutes, lightly_active_minutes,
         moderately_active_minutes, very_active_minutes]
    '''
    
    if player == 'p12':
        with st.container(height=50):
            st.write(f'{player}/fitbit/steps.json is not found -- Skipping...')
    
    df_active_per_player = df_active_steps_pXX.loc[
        df_active_steps_pXX['pXX'] == player].copy()
    
    # The data starts on Friday. To include the whole week,
    # Data are grouped weekly starting on Thursday. So 'W-THU'
    
    ## I'm trying to do the same thing of pd.Grouper. However,
    ## seeing that we have 'pXX' into account, we need to 
    ## convert the dates separately using pd.Series.dt.to_period()
    
    df_active_per_player['dateTime'] = (
        df_active_per_player['dateTime']
            .dt.to_period("W-THU").dt.end_time.dt.date)
    
    df_active_mins_weekly_pXX = df_active_per_player.groupby(
            ['pXX', 'dateTime']).agg('sum').droplevel(0)
    
    # We're dropping num_steps (first col) + column of 
    # non-preference, looking at parameter of `startfromzone`
    active_cols_to_drop = (df_active_mins_weekly_pXX.columns
                           .to_list()[:startfromzone+1])
    active_mins_color = ['#98FB98', '#77DD77', '#32CD32', '#006400']

    if num_steps:
    
        fig, ax = plt.subplots(figsize=(12, 6))

        df_active_mins_weekly_pXX['num_steps'].plot(
            kind='bar', width=0.8, ax=ax)
        ax.set_title(f'Active Steps per Week, {player} (updated every Thursday)',
            fontsize=15, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('Duration (mins)')
        ax.legend(labels=['Number of Steps'], loc='best')
        ax.grid(alpha=0.4)
        fig.autofmt_xdate()
        
        st.pyplot(fig)
    
    active_labels = [
        'Sedentary Minutes', 'Lightly Active Minutes',
        'Moderately Active Minutes', 'Very Active Minutes']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    am_labels_loc = 'lower right' if startfromzone == 0 else 'best'
        
    df_active_mins_weekly_pXX.drop(active_cols_to_drop, axis=1).plot(
        kind='bar', stacked=True, width=0.8, ax=ax, 
        color=active_mins_color[startfromzone:])
    ax.set_title(f'Active Minutes per Week, {player} (updated every Thursday)',
        fontsize=15, fontweight='bold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Duration (mins)')
    ax.legend(labels=active_labels[startfromzone:], loc=am_labels_loc)
    ax.grid(alpha=0.4)
    fig.autofmt_xdate()
    
    st.pyplot(fig)
        
    
### `sleep`:
    ### Sleep Stages on a Day, Step Chart
    ### Total Duration in Sleep Stages, Stacked Area Chart
    
@st.cache_data
def clean_data_sleep():
    
    df_sleep = pd.DataFrame()

    for pXX in id_players:

        sleep_pXX = pd.read_json(f"{pXX}/fitbit/sleep.json")
        sleep_pXX['pXX'] = pXX
        df_sleep  = pd.concat([df_sleep, sleep_pXX], ignore_index=True)

    df_sleep = df_sleep.join(
        pd.json_normalize(df_sleep['levels'])
    ).drop(['levels', 'shortData'], axis=1)

    date_cols = ['dateOfSleep', 'startTime', 'endTime']

    for col in date_cols:
        df_sleep[col] = pd.to_datetime(df_sleep[col])
    
    df_sleep_chr = pd.DataFrame(
        df_sleep[['pXX','data', 'dateOfSleep', 'type', 'mainSleep']]
            .explode('data', ignore_index=True)) 

    df_sleep_chr = df_sleep_chr.merge(
        pd.json_normalize(df_sleep_chr['data']), 
            left_index=True, right_index=True
    ).drop('data', axis=1)

    df_sleep_chr['dateTime'] = pd.to_datetime(
        df_sleep_chr['dateTime'])
        
    df_sleep_chr = df_sleep_chr.drop_duplicates()
    
    ## For convenience, we'll change all 9 `unknown` levels to `light`.
    ## They're all in Sensitive Mode, it'd be easier to change it amidst of 46k rows
    df_sleep_chr.loc[df_sleep_chr['level'] == 'unknown', 'level'] = 'light'
    
    return df_sleep_chr


def sleep_stages_by_day_step_chart_pXX(player='p01', date='2019-11-02'):
    
    df_sleep_main_pXX = df_sleep_chr.loc[
        (df_sleep_chr['pXX'] == player) &
        (df_sleep_chr['mainSleep'] == True) &
        (df_sleep_chr['dateOfSleep'] == date)].copy()
        
    measure_type = df_sleep_main_pXX['type'].max()
    
    df_stage_order = []
    if measure_type == 'classic':
        df_stage_order = ['asleep', 'restless', 'awake'] 
    else:
        df_stage_order = ['deep', 'rem', 'light', 'wake']
    
    df_sleep_main_pXX['level'] = pd.Categorical(
        df_sleep_main_pXX['level'],
        categories=df_stage_order)
    
    df_sleep_main_pXX['level_num'] = df_sleep_main_pXX['level'].cat.codes
    
    stage_labels = df_sleep_main_pXX['level'].cat.categories
    stage_values = range(len(stage_labels))
    
    ## Setting line width according to minimum duration
    min_duration = df_sleep_main_pXX['seconds'].min()
    lw_settings  = (2 if min_duration < 300 else 4)    
    
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    
    ax.step(
        df_sleep_main_pXX['dateTime'], 
        df_sleep_main_pXX['level'].cat.codes, where='post', 
        linewidth=lw_settings, solid_joinstyle='bevel')
    ax.set_title(f'Sleep Cycle of Stages, {player} at {date}',
        fontsize=15, fontweight='bold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Sleep Stages')
    
    ax.set_yticks(stage_values)
    ax.set_yticklabels(stage_labels)

    ax.grid(alpha=0.4)
    
    st.pyplot(fig)
    
    
def total_sleep_stages_stacked_area_chart_pXX(player='p01', days='2019-11-02'):

    df_sleep_chr_pXX = df_sleep_chr.loc[
        (df_sleep_chr['pXX'] == player) &
        (df_sleep_chr['mainSleep'] == True)
    ]
    
    df_sleep_chr_pXX_sum = df_sleep_chr_pXX[
        ['dateOfSleep', 'level', 'seconds']].groupby(
        ['dateOfSleep', 'level']).agg('sum').reset_index()
    
    df_sleep_chr_pXX_sum_pivot = df_sleep_chr_pXX_sum.pivot(
        columns='level', index='dateOfSleep', values='seconds'
    ).fillna(0)
    
    ## Adding new columns for player with no `Normal` mode, smoothly executing the viz
    if len(df_sleep_chr_pXX_sum_pivot.columns) < 7:
        df_sleep_chr_pXX_sum_pivot[['asleep', 'restless', 'awake']] = 0
    
    df_sleep_chr_pXX_sum_pivot = df_sleep_chr_pXX_sum_pivot[[
        'asleep', 'restless', 'awake', 'deep', 'rem', 'light', 'wake']]
    
    sleep_stages_colors = {
        ## Normal Mode, lower score
        'asleep': '#4D001F', 'restless': '#B3002D', 
         'awake': '#ff6666',
        ## Sensitive Mode, higher score
          'deep': '#0F3E58', 'rem': '#015482', 
         'light': '#4AA6D7', 'wake': '#82D3FF'
    }
    
    fig, ax = plt.subplots(figsize=(12, 6))

    # Now we have 4 records in pivoted data, 
    # we no longer need to match the dates   
    df_sleep_chr_pXX_sum_pivot[-days:].plot.area(ax=ax,
        color=[sleep_stages_colors[key] for key in 
           df_sleep_chr_pXX_sum_pivot.columns])
    
    ax.set_title(f'Duration in Sleep Stages, {player} (the last {days} days)',
        fontsize=15, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Duration')
    ax.grid(alpha=0.4)
    ax.legend(title='Sleep Stages', fontsize=12, loc='best')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)


### `googledocs`:
    ### Meals Check per Player, Heatmap
    
@st.cache_data    
def clean_data_reporting():
    
    df_reporting = pd.DataFrame()

    for pXX in id_players:

        reporting_pXX = pd.read_csv("p01/googledocs/reporting.csv")
        reporting_pXX['pXX'] = pXX
        df_reporting = pd.concat([df_reporting, reporting_pXX], ignore_index=True)
    
    df_reporting['date']      = pd.to_datetime(
        df_reporting['date'], dayfirst=True)
    df_reporting['timestamp'] = pd.to_datetime(
        df_reporting['timestamp'], dayfirst=True)
    
    df_reporting['time_diffs'] = df_reporting['timestamp'] - df_reporting['date']
    
    # Case 1 -- Filtering total seconds less than 14400s, or within 4 hours.
    df_filter_case_1 =  df_reporting.loc[
        (df_reporting['time_diffs'].dt.days == 0) & 
        (df_reporting['time_diffs'].dt.total_seconds() < 14400)]
    
    ## Case 2 -- Input date within a month before/after
    df_filter_case_2 = df_reporting.loc[
        (df_reporting['time_diffs'].dt.days >= 3) | 
        (df_reporting['time_diffs'].dt.days < 0)]
    
    ## Cleaning case 1: Subtract date by one day
    df_reporting.loc[df_reporting.index.isin(
        df_filter_case_1.index), 'date'] = (

    df_reporting.loc[df_reporting.index.isin(
        df_filter_case_1.index), 'date'] - pd.Timedelta(days=1))
    
    ## Cleaning case 2: Change `date` into date of `timestamp`
    df_reporting.loc[df_reporting.index.isin(
        df_filter_case_2.index), 'date'] = (

    df_reporting.loc[df_reporting.index.isin(
        df_filter_case_2.index), 'timestamp'].dt.date)
    
    ## Cleaning duplicates
    df_dupl = (df_reporting.loc[
        df_reporting[['pXX', 'date']].duplicated(keep=False), :]
            .sort_values(['pXX', 'date', 'timestamp']))
    
    ## Case 3 (duplicates): 
    ## Double-input in a day, both submitted after midnight
    df_dupl_cleaned = pd.DataFrame()

    for pXX in id_players:

        df_dupl_pXX    = df_dupl.loc[df_dupl['pXX'] == pXX]
        dupl_shape_pXX = df_dupl_pXX.shape[0] - 1

        for i in range(dupl_shape_pXX):
            df_dupl_pXX.iloc[i, df_dupl_pXX.columns.get_loc('date')] = (
                df_dupl_pXX.iloc[i]['date'] - pd.Timedelta(days=dupl_shape_pXX - i))

        df_dupl_cleaned = pd.concat([df_dupl_cleaned, df_dupl_pXX])
    
    df_reporting.update(df_dupl_cleaned)
    
    df_reporting = df_reporting.drop('time_diffs', axis=1)
    
    ## Additional cleaning for data-viz of meals:
    
    meals = pd.get_dummies(df_reporting['meals'].str.get_dummies(sep=', '))
    meals.columns = meals.columns.str.lower()
    meals = meals[['breakfast', 'lunch', 'evening', 'dinner']]
    
    df_reporting = pd.concat([df_reporting, meals], axis=1)
    
    return df_reporting


def meals_check_heatmap_pXX(player, days):
    
    df_reporting_pXX = df_reporting.loc[df_reporting['pXX'] == player]
    df_reporting_pXX = df_reporting_pXX[['date', 'breakfast', 
        'lunch', 'evening', 'dinner']][-days:].set_index('date')
    df_reporting_pXX.index = (df_reporting_pXX.index.strftime('%Y-%m-%d'))
    
    fig, ax = plt.subplots(figsize=(15, 6))

    sns.heatmap(df_reporting_pXX.T,
        cmap='rocket', xticklabels=True, linewidths=2, 
        linecolor='black', clip_on=False, ax=ax)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    fig.autofmt_xdate()
    
    plt.title(f'Meals Check, {player} (the last {days} days)',
        fontsize=15, fontweight='bold')
    st.pyplot(plt.gcf())


### `wellness`:
    ### Wellness Score of a Player, Radar Chart
    
@st.cache_data
def clean_data_wellness():

    df_wellness = pd.DataFrame()

    for pXX in id_players:

        wellness_pXX = pd.read_csv(f"{pXX}/pmsys/wellness.csv")
        wellness_pXX['pXX'] = pXX
        df_wellness = pd.concat([df_wellness, wellness_pXX])

    df_wellness['date'] = pd.to_datetime(
        df_wellness['effective_time_frame']).dt.floor('d')

    # We'll visualize only subjective scores
    df_wellness_cleaned = df_wellness.drop(['effective_time_frame', 
        'sleep_duration_h', 'soreness_area'], axis=1)
    new_cols = ['date', 'pXX'] + df_wellness_cleaned.columns[:-2].to_list()
    df_wellness_cleaned = df_wellness_cleaned[new_cols]

    ## Normalize scores--All subjective scores are within scale of 1-5,
    ##    with only `readiness` have a scale of 1-10. 
    df_wellness_cleaned['readiness'] /= 2

    # The data starts on Friday. To include the whole week,
    # Data are grouped weekly starting on Thursday. So 'W-THU'

    df_wellness_per_week = df_wellness_cleaned.copy()

    df_wellness_per_week['date'] = (
        df_wellness_per_week['date']
            .dt.to_period("W-THU").dt.end_time.dt.date)

    df_wellness_per_week = df_wellness_per_week.groupby(
            ['pXX', 'date']).agg(['mean', 'std'])

    df_wellness_per_week.columns = df_wellness_per_week.columns.map('_'.join)
    # wellness_per_week = wellness_per_week.reset_index()
    df_wellness_per_week = df_wellness_per_week.reset_index()
    return df_wellness_per_week


def wellness_score_radar_chart_pXX(player='p01', week_n=1):
    
    df_data_mean_cols = df_wellness_per_week.columns[
        df_wellness_per_week.columns.str.endswith('_mean')]
    df_data_std_cols  = df_wellness_per_week.columns[
        df_wellness_per_week.columns.str.endswith('_std')]
    
    wellness_pXX = df_wellness_per_week.loc[
        df_wellness_per_week['pXX'] == player]
    
    # Extract row of data per week
    df_data_mean = np.array(wellness_pXX[df_data_mean_cols].iloc[week_n-1])
    df_data_std  = np.array(wellness_pXX[df_data_std_cols].iloc[week_n-1])
        
    label_loc = np.linspace(start=0, stop=2*np.pi,
        num=df_data_mean_cols.shape[0] + 1)
    
    viz_labels = (df_data_mean_cols.str.replace('_mean', '')
        .str.replace('_', ' ').str.title())
    
    date_end   = str(wellness_pXX['date'].iloc[week_n-1])
    date_start = str((wellness_pXX['date'].iloc[week_n-1] - 
                      pd.Timedelta(days=6)))
    
    plt.figure(figsize=(12, 6))
    plt.subplot(polar=True)
    plt.plot(label_loc, np.r_[df_data_mean, df_data_mean[0]], 
        label=f'Week {week_n}', linewidth=4)
    plt.fill(label_loc, np.r_[(df_data_mean + df_data_std),
        (df_data_mean[0] + df_data_std[0])], facecolor='paleturquoise', alpha=0.15)
    plt.fill(label_loc, np.r_[(df_data_mean - df_data_std),
        (df_data_mean[0] - df_data_std[0])], facecolor='black')
    plt.title(f'''Wellness Score, {player} -- Week {week_n}: {date_start} to {date_end}''', 
              fontsize=15, fontweight='bold', y=1.05)
    lines, labels = plt.thetagrids(
        np.degrees(label_loc[:-1]), labels=viz_labels)
    plt.ylim([0, 5])
    plt.legend(bbox_to_anchor=[1.2, 1])
    
    st.pyplot(plt.gcf())
    

# ## RETRACTED FEATURE    
# ## Features available: Cleaning data provided to *Only* Individual players


# ### `heart_rate`:
#     ### Heart Rate per Player in Real-Time (6-hour interval),
#         ### Line Chart (avg) + Bar Chart (confidence)
        
# @st.cache_data
# def clean_data_heart_rate_per_player(player='p01'):
    
#     HR_pXX = pd.read_json(f"{player}/fitbit/heart_rate.json")

#     HR_pXX = (HR_pXX.join(pd.json_normalize(HR_pXX['value']))
#         .drop('value', axis=1).rename(columns={'bpm':'hr_bpm'}))

#     HR_pXX['dateTime'] = HR_pXX['dateTime'].dt.floor('6h')
#     HR_pXX_per_six_hour = HR_pXX.groupby('dateTime').agg(
#         ['mean', 'max', 'min']).reset_index()

#     new_cols = ['datetime'] + ['_'.join(pair) 
#         for pair in HR_pXX_per_six_hour.columns[1:]]
#     HR_pXX_per_six_hour.columns = HR_pXX_per_six_hour.columns.droplevel(0)
#     HR_pXX_per_six_hour.columns = new_cols
    
#     HR_pXX_per_six_hour = HR_pXX_per_six_hour.drop(
#         ['confidence_max', 'confidence_min'], axis=1)
#     HR_pXX_per_six_hour['confidence_mean'] = np.rint(
#         HR_pXX_per_six_hour['confidence_mean'])
    
#     HR_pXX_per_six_hour['pXX'] = player
    
#     return HR_pXX_per_six_hour


# def heart_rate_bar_and_line_chart_pXX(df: pd.DataFrame, days):

#     conf_colors = {3: '#91FF61', 2: '#88AA79', 1: '#465540', 0:'#283024'}
#     bar_diffs   = df['hr_bpm_max'] - df['hr_bpm_min']
#     bar_colors  = df['confidence_mean'].map(conf_colors)
    
#     fig, ax = plt.subplots(figsize=(12, 6))
#     i_start = -1 * (4 * days + 1)
#     # Add by one since last day only display 3 rows, not 4.
    
#     ax.bar(df['datetime'][i_start:], bar_diffs[i_start:],
#         bottom = df['hr_bpm_min'][i_start:], 
#         color = bar_colors[i_start:], alpha = 0.6, width = 0.2)

#     ax.plot(df['datetime'][i_start:], df['hr_bpm_mean'][i_start:],
#         color = 'white', linewidth = 1, marker = 'o', label = 'HR_avg')
    
#     player = df['pXX'].max()

#     ax.set_title(f'Heart Rate in latest {days} days, {player} (grouped every 6 hours)',
#         fontsize=15, fontweight='bold')
#     ax.set_xlabel('Time')
#     ax.set_ylabel('Heart Rate (bpm)')
#     ax.grid(alpha=0.4)
    
#     legend_elements = [
#         Patch(facecolor=conf_colors[3], edgecolor='none', alpha=0.5, label='Confidence = 3'),
#         Patch(facecolor=conf_colors[2], edgecolor='none', alpha=0.5, label='Confidence = 2'),
#         Patch(facecolor=conf_colors[1], edgecolor='none', alpha=0.5, label='Confidence = 1'),
#         Patch(facecolor=conf_colors[0], edgecolor='none', alpha=0.5, label='Confidence = 0')
#     ]
    
#     ax.legend(handles = legend_elements + 
#         [Patch(color='white', label='HR_avg')], loc='best')

#     plt.xticks(rotation=45)
#     plt.tight_layout()
        
#     st.pyplot(fig)
    
    
#### MAIN FUNCTION

df_cals              = clean_data_calories_per_month()
df_dists             = clean_data_distances_per_month()
df_exercises         = clean_data_exercise()
df_RHR               = clean_data_resting_heart_rate()
df_srpe              = clean_data_srpe()
df_hrz_in_mins       = clean_data_hrz()
df_active_steps_pXX  = clean_data_active_minutes()
df_sleep_chr         = clean_data_sleep()
df_sleep_score       = clean_data_sleep_score()
df_reporting         = clean_data_reporting()
df_wellness_per_week = clean_data_wellness()
# df_HR_rt             = clean_data_heart_rate_per_player()

#### STREAMLIT COMPONENTS

url_linkedin = "https://www.linkedin.com/in/mohamadalamsyah/"
url_dataset  = "https://www.kaggle.com/datasets/vlbthambawita/pmdata-a-sports-logging-dataset"
url_github   = "https://github.com/itsalamhere/sports-logs-streamlit"

st.header('SportsLogs: Sports Logging Dashboard')
# st.write('Dashboard by [Mohamad Alamsyah](%s)' % url_linkedin)

with st.sidebar.expander("**About SportsLogs**"):
    st.markdown("""
    SportsLogs is a dashboard visualizing the performance of 16 players through 10+ datasets:
    from distance and calories, up to sleep stages and wellness score.  \n
    The data is taken from [PMData](%s) where all data are collected from sources of 
    biometric sensors (**FitBit**), sports logging (**PMSys**), and subjective scores on all players (**Google Docs**).  \n
    All data has been cleaned and then visualized through Jupyter Notebook and then transferred to
    Streamlit as a web-app dashboard.""" % url_dataset)
    st.markdown("For the whole project, you can go [here](%s)." % url_github)
    st.markdown("Created by [Mohamad Alamsyah](%s)" % url_linkedin)

selected_player = st.sidebar.selectbox(
    'Choose a Player',
    tuple(['all'] + id_players))    
    
if selected_player == 'all':
    
    with st.sidebar.container(height=155):
        st.markdown("""
            Other charts are available for individual players only. \n
            For further inspection, please choose a player on the sidebar.
        """)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🍕🔥 Calories",
        "🛣️🏃‍➡️ Distances",
        "⚽✊ Sport Activities",
        "💤🔋 Sleep Quality"])
    
    with tab1:
        calories_per_month_bar_chart_pXX(selected_player)        ## Calories per month
    with tab2:
        distance_per_month_bar_chart_pXX(selected_player)        ## Distance per month
    with tab3:
        sport_activities_pie_chart_pXX(selected_player)          ## Sport activities
    with tab4:
        sleep_quality_pie_chart_pXX(selected_player)

else:
    
    with st.sidebar.container(height=155):
        st.markdown("""
            The charts can be modified with parameters in each data.  \n
            You can adjust the respective parameters below.
        """)
    
    ### FEATURES IN SIDEBAR:
    st.sidebar.write("###")
    
    st.sidebar.subheader('🫀📍 **Heart Rate Zones (Real-Time)**')
    params_hrz = st.sidebar.slider(
        '''**Heart Rate Zones** starts from: 
        (0: Out of Range Zone, 3: Peak Zone)''', 
        0, 3, 1, key="hrz_realtime")
    st.sidebar.write("###")
        
    st.sidebar.subheader('⚡⏲️ **Active Minutes (Real-Time)**')
    params_active = st.sidebar.slider(
        '''**Active Minutes** starts from:
        (0: Sedentary Minutes, 3: Very Active Minutes)''', 
        0, 3, 1, key="act_realtime")
        
    params_num_steps = st.sidebar.checkbox(
        'Show Chart: **Number of Steps**', True)
    st.sidebar.write("###")
    
    st.sidebar.subheader('🌌🗓️ **Sleep Stages by Date**')    
    params_sleep_date = st.sidebar.date_input(
        'Date of Sleep (from 2019-11-02 to 2020-03-31):',
        value=date.fromisoformat('2020-01-01'), 
        min_value=date.fromisoformat('2019-11-02'), 
        max_value=date.fromisoformat('2020-03-31'))
    st.sidebar.write("###")
     
    st.sidebar.subheader('⏲️🌌 **Total Duration of Sleep Stages**')
    params_sleep_duration = st.sidebar.slider(
        'Duration for the **last N days**:', 7, 150, 28)
    st.sidebar.write("###")
    
    st.sidebar.subheader('🍽️📆 **Meals Check**')
    params_meals = st.sidebar.slider(
      'Meals check for the **last N days**:', 7, 150, 28)      
    st.sidebar.write("###")
    
    st.sidebar.subheader('🔋💯 **Wellness Score**')
    params_wellness = st.sidebar.slider(
      'Wellness Score **Week N**:', 1, 15)
    st.sidebar.write("###")

    # st.sidebar.subheader('🫀⌚ **Heart Rate (Real-Time)**')
    # params_hrz_rt = st.sidebar.slider(
    #   'Heart rate for the **last N days**:', 7, 150, 28)      
    # st.sidebar.write("###")
    
    
    ### Showing the data-viz of tabs at the main area
    
    ( tab1,  tab2,  tab3,  tab4,  tab5,
      tab6,  tab7,  tab8,  tab9, tab10,
     tab11, tab12, tab13) = st.tabs([ # tab14
        "🍕🔥 Calories",
        "🛣️🏃‍➡️ Distances",
        "⚽✊ Sport Activities",
        "💤🔋 Sleep Quality",
        "🫀🛌 Resting Heart Rate",
        "📊⚽ Active Metrics in Sport Activities",
        "💪⚽ SRPE in Sport Activities",
        "🫀📍 Heart Rate Zones (Real-Time)",
        "⚡⏲️ Active Minutes (Real-Time)",
        "🌌🗓️ Sleep Stages by Date",    
        "⏲️🌌 Total Duration of Sleep Stages",
        "🍽️📆 Meals Check in Last X Days",
        "🔋💯 Wellness Score on a Given Week"
        # "🫀⌚ Heart Rate (Real-Time)"
        ])
    
    with tab1:
        calories_per_month_bar_chart_pXX(selected_player)        ## Calories per month
    with tab2:
        distance_per_month_bar_chart_pXX(selected_player)        ## Distance per month
    with tab3:
        sport_activities_pie_chart_pXX(selected_player)          ## Sport activities
    with tab4:
        sleep_quality_pie_chart_pXX(selected_player)
    with tab5:
        if selected_player in ['p12', 'p13']:
            with st.container(height=90):
                st.write(f"Resting heart rate file of {selected_player} is not found.")
        else:
            resting_heart_rate_line_chart_pXX(selected_player)
            with st.expander("**Additional Notes**"):
                st.write("Some player has value of 0 in several dates.  \n",
                    "That means the data at those dates are missing.")
    with tab6:
        active_metrics_per_sport_stacked_bar_chart_pXX(selected_player)
    with tab7:
        srpe_per_sport_boxplot_pXX(selected_player)
    with tab8:
        hrz_bar_chart_pXX(selected_player, startfromzone=params_hrz)
    with tab9:
        if selected_player == 'p12':
            with st.container(height=50):
                st.write(f"Lightly active minutes file of {selected_player} is not found. Skipping..")   
        active_minutes_bar_chart_pXX(selected_player, 
            num_steps=params_num_steps, startfromzone=params_active)
    with tab10:
        sleep_stages_by_day_step_chart_pXX(
            selected_player, date=str(params_sleep_date))
        with st.expander("**Additional Notes**"):
            st.write(
                "The measurement of sleep stages are divided into 2 modes:  \n",
                "**Normal Mode** (asleep, restless, awake) and **Sensitive Mode** (deep, rem, light, wake). \n",
                
                "  \n  The measurements are **Sensitive Mode** in default, but this can change to **Normal Mode** due to several reasons:  \n",
                "- Positions of tracker in wrist,  \n",
                "- Battery almost empty going to bed (less than 25%), or  \n",
                "- Having a main sleep less than 3 hours.  \n")            
    with tab11:
        total_sleep_stages_stacked_area_chart_pXX(
            selected_player, days=params_sleep_duration)
        with st.expander("**Additional Notes**"):
            st.write(
                "The measurement of sleep stages are divided into 2 modes:  \n",
                "**Normal Mode** (red) and **Sensitive Mode** (blue). \n",
                
                "  \n  The measurements are **Sensitive Mode** in default, but this can change to **Normal Mode** due to several reasons:  \n",
                "- Positions of tracker in wrist,  \n",
                "- Battery almost empty going to bed (less than 25%), or  \n",
                "- Having a main sleep less than 3 hours.  \n")
    with tab12:
        meals_check_heatmap_pXX(selected_player, days=params_meals)
    with tab13:
        wellness_score_radar_chart_pXX(
            selected_player, week_n=params_wellness)
    # with tab14:
    #   heart_rate_bar_and_line_chart_pXX(df_HR_rt, days=params_hrz_rt)
            
