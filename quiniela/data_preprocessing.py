import pandas as pd











def generate_features(df):
    # Filter rows where 'score' is not null
    df = df.loc[~df['score'].isnull()].copy()
    
    # Separate home and away scores
    df[['home_score', 'away_score']] = df['score'].str.split(':', expand=True)
    df['home_score'] = pd.to_numeric(df['home_score'])
    df['away_score'] = pd.to_numeric(df['away_score'])
    
    # Calculate home and away goals for each team
    home_goals = df.groupby('home_team')['home_score'].sum().reset_index()
    home_goals.columns = ['team', 'home_goals']
    away_goals = df.groupby('away_team')['away_score'].sum().reset_index()
    away_goals.columns = ['team', 'away_goals']
    
    # Merge home and away goals to get total goals
    all_time = pd.merge(home_goals, away_goals, on='team', how='outer').fillna(0)
    all_time['total_goals'] = all_time['home_goals'] + all_time['away_goals']
    
    # Calculate home and away concedes for each team
    home_conceding = df.groupby('home_team')['away_score'].sum().reset_index()
    home_conceding.columns = ['team', 'concedes_home']
    away_conceding = df.groupby('away_team')['home_score'].sum().reset_index()
    away_conceding.columns = ['team', 'concedes_away']
    
    # Merge conceding data with total goals data
    all_time_concedes = pd.merge(home_conceding, away_conceding, on='team', how='outer').fillna(0)
    all_time_concedes['total_concedes'] = all_time_concedes['concedes_home'] + all_time_concedes['concedes_away']
    all_time = pd.merge(all_time, all_time_concedes, on='team', how='outer').fillna(0)
    
    # Compute game appearances for home and away
    home_counts = df['home_team'].value_counts()
    away_counts = df['away_team'].value_counts()
    total_counts = home_counts.add(away_counts, fill_value=0)
    
    # Map appearances onto the DataFrame
    df['home_app_home'] = df['home_team'].map(home_counts)
    df['home_app_total'] = df['home_team'].map(total_counts)
    df['away_app_away'] = df['away_team'].map(away_counts)
    df['away_app_total'] = df['away_team'].map(total_counts)
    
    # Merge stats onto the DataFrame
    df = df.merge(all_time[['team','home_goals','total_goals','concedes_home','total_concedes']], 
                  left_on='home_team', right_on='team', how='outer').fillna(0)
    df = df.merge(all_time[['team','away_goals','total_goals','concedes_away','total_concedes']], 
                  left_on='away_team', right_on='team', suffixes=('_home', '_away'), how='outer').fillna(0)
    df = df.drop(['team_home', 'team_away'], axis=1)
    
    # Calculate scoring and conceding ratios
    df['home_goals_ratio'] = df['home_goals'] / df['home_app_home']
    df['away_goals_ratio'] = df['away_goals'] / df['away_app_away']
    df['total_goals_home_ratio'] = df['total_goals_home'] / df['home_app_total']
    df['total_goals_away_ratio'] = df['total_goals_away'] / df['away_app_total']
    
    df['concedes_home_ratio'] = df['concedes_home'] / df['home_app_home']
    df['concedes_away_ratio'] = df['concedes_away'] / df['away_app_away']
    df['total_concedes_home_ratio'] = df['total_concedes_home'] / df['home_app_total']
    df['total_concedes_away_ratio'] = df['total_concedes_away'] / df['away_app_total']
    
    # Calculate goal differences
    df['goal_diff_home'] = df['home_goals'] - df['concedes_home']
    df['goal_diff_home_total'] = df['total_goals_home'] - df['total_concedes_home']
    df['goal_diff_away'] = df['away_goals'] - df['concedes_away']
    df['goal_diff_away_total'] = df['total_goals_away'] - df['total_concedes_away']
    df['goal_diff_home_ratio'] = df['home_goals_ratio'] - df['concedes_home_ratio']
    df['goal_diff_home_total_ratio'] = df['total_goals_home_ratio'] - df['total_concedes_home_ratio']
    df['goal_diff_away_ratio'] = df['away_goals_ratio'] - df['concedes_away_ratio']
    df['goal_diff_away_total_ratio'] = df['total_goals_away_ratio'] - df['total_concedes_away_ratio']
    
    # Define the result column (home win, away win, tie)
    df['result'] = df.apply(lambda row: '1' if row['home_score'] > row['away_score']
                                        else '2' if row['home_score'] < row['away_score']
                                        else 'X', axis=1)
    
    # Convert 'date' column to datetime with specified format and add weekday columns
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y')
    df['weekday'] = df['date'].dt.day_name()
    df['weekday_num'] = df['date'].dt.dayofweek
    
    # Drop 'weekday' if unnecessary
    df = df.drop('weekday', axis=1)
    
    return df

def get_X_y(df):
    y = df.loc[:,'result']
    cols_to_drop = ['score','home_score','away_score','result','date', 'time']
    X = df.drop(columns=cols_to_drop)
    X = pd.get_dummies(X, columns=['season','home_team','away_team'])

    return X, y



