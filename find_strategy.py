import itertools
import pandas as pd
import numpy as np
from itertools import combinations
import re
from collections import defaultdict

def process_trades(input_filename, output_filename):
    df = pd.read_csv(input_filename)
    
    def max_transactions_count_by_time(data_set):
        # Convert to datetime format and tag them
        tagged_times = [(pd.to_datetime(el), 'entry') for el in data_set['Entry time']] + \
                       [(pd.to_datetime(el), 'exit') for el in data_set['Exit time']]
        
        # Sort by timestamp
        sorted_times = sorted(tagged_times, key=lambda x: x[0])
        
        transactions_count = 0
        highest_transactions_count = 0
    
        for time, tag in sorted_times:
            if tag == 'entry':
                transactions_count += 1
            else:
                transactions_count -= 1
    
            if transactions_count > highest_transactions_count:
                highest_transactions_count = transactions_count
                
        return highest_transactions_count

    results = defaultdict(lambda: {
        'Wins': 0, 'Losses': 0, 'Real Entrance': 0, 'Overall Profit': 0
    })
    
    all_y_columns = [col for col in df if (df[col] == 'y').all()]
    y_gt_n_columns = [col for col in df if (df[col] == 'y').sum() > (df[col] == 'n').sum()]
    selected_columns = list(set(all_y_columns + y_gt_n_columns))
    sorted_columns = sorted(selected_columns, key=lambda col: (df[col] == 'y').sum(), reverse=True)
    
    all_strategies = [sorted_columns[i:i+16] for i in range(0, len(sorted_columns), 16)]
    
    for strategy_columns in all_strategies:
        strategy_data = df[df[strategy_columns].eq('y').all(axis=1)]
        if strategy_data.empty:
            continue
        
        strategy_name = ", ".join(strategy_columns)
    
        wins = (strategy_data['PnL'] > 0).sum()
        losses = (strategy_data['PnL'] <= 0).sum()
        real_entrance = max_transactions_count_by_time(strategy_data)
        overall_profit = strategy_data['PnL'].clip(lower=0).sum()
    
        results[strategy_name]['Wins'] += wins
        results[strategy_name]['Losses'] += losses
        results[strategy_name]['Real Entrance'] = real_entrance
        results[strategy_name]['Overall Profit'] += overall_profit
    
    output = []

    for strategy, metrics in results.items():
        C = metrics['Wins']
        D = metrics['Losses']
        E = metrics['Real Entrance']
        B = metrics['Overall Profit']
        F = C + D
        G = C - D
        H = E * 500
        I = (B / H) * 100 if H != 0 else 0
        J = B / (E * 500) * 100 if E != 0 else 0
        K = B / (500 * 150) * 100
        L = (G / F) * 100 if F != 0 else 0
        output.append([strategy, B, C, D, E, F, G, H, I, J, K, L])
    
    columns = [
        'Strategy', 'Overall Profit', 'Wins', 'Losses', 'Real Entrance', 
        'C+D', 'C-D', 'E*500', '(B/H)*100', 'B/(E*500)*100', 'B/(500*150)*100', '(G/F)*100'
    ]
    result_df = pd.DataFrame(output, columns=columns)
    result_df = result_df.sort_values(by='Overall Profit', ascending=False)
    result_df = result_df.reset_index(drop=True)
    result_df.to_csv(output_filename, index=False)
    print(f"{output_filename} is Done!")

# Example Usage:
input_file = input("Please enter the input filename (As CSV format): ")
output_file = input("Please enter the output filename (As CSV format): ")
process_trades(input_file, output_file)
