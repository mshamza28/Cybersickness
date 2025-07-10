"""
VR Sickness Mitigation Techniques
-----------------------------------------------------------------------------------
This script creates boxplot visualizations and calculates descriptive statistics
for different scenarios and mitigation techniques.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Optional, Dict, List, Tuple

# Configuration
CONFIG = {
    'file_path': 'data/SSQ/Post_SSQ.csv',
    'scenarios': ['Tower Defense', 'Roller Coaster'],
    'techniques': [
        'Baseline (No Mitigation Technique)',
        'Gaze-Contingent DOF',
        'Virtual Cave'
    ],
    'measures': ['Total Score', 'Nausea', 'Oculomotor', 'Disorientation'],
    'output_dir': 'output/SSQ_Results',
    'save_figures': True
}


def load_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load and return the SSQ data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing the SSQ data or None if file not found
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded data from {file_path}")
        print(f"Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None


def get_descriptive_stats(df: pd.DataFrame, measure: str) -> pd.DataFrame:
    """
    Calculate descriptive statistics for each scenario and mitigation technique.
    
    Args:
        df: DataFrame containing the SSQ data
        measure: The measure to analyze
        
    Returns:
        DataFrame containing descriptive statistics
    """
    # Clean technique names for better display
    df['Mitigation Technique'] = df['Select the Mitigation Technique'].apply(
        lambda x: 'Baseline' if 'Baseline' in x else x
    )
    
    # Create a list to store statistics for each group
    stats_list = []
    
    # For each scenario and technique combination
    for scenario in CONFIG['scenarios']:
        for technique in CONFIG['techniques']:
            # Get technique name as displayed in plot
            tech_name = 'Baseline' if 'Baseline' in technique else technique
            
            # Filter data
            filtered_data = df[(df['Select the Scenario:'] == scenario) & 
                              (df['Mitigation Technique'] == tech_name)][measure]
            
            if not filtered_data.empty:
                # Calculate statistics
                stats = {
                    'Scenario': scenario,
                    'Technique': tech_name,
                    'Count': len(filtered_data),
                    'Mean': filtered_data.mean(),
                    'Std Dev': filtered_data.std(),
                    'SEM': filtered_data.std() / np.sqrt(len(filtered_data)),
                    'Median': filtered_data.median(),
                    'Min': filtered_data.min(),
                    'Max': filtered_data.max(),
                    'Q1': filtered_data.quantile(0.25),
                    'Q3': filtered_data.quantile(0.75),
                    'IQR': filtered_data.quantile(0.75) - filtered_data.quantile(0.25)
                }
                stats_list.append(stats)
    
    # Create DataFrame from stats list
    stats_df = pd.DataFrame(stats_list)
    
    return stats_df


def export_stats_to_csv(stats_df: pd.DataFrame, measure: str, output_dir: str) -> None:
    """
    Export descriptive statistics to a CSV file.
    
    Args:
        stats_df: DataFrame containing the statistics
        measure: The measure being analyzed
        output_dir: Directory to save the CSV file
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{measure.replace(' ', '_')}_descriptive_stats.csv")
    stats_df.to_csv(filename, index=False)
    print(f"Descriptive statistics saved to {filename}")


def print_descriptive_stats(stats_df: pd.DataFrame, measure: str) -> None:
    """
    Print descriptive statistics in a formatted way.
    
    Args:
        stats_df: DataFrame containing the statistics
        measure: The measure being analyzed
    """
    print(f"\n{'='*80}")
    print(f"DESCRIPTIVE STATISTICS FOR {measure.upper()}")
    print(f"{'='*80}")
    
    for scenario in CONFIG['scenarios']:
        print(f"\n--- {scenario} Scenario ---\n")
        
        # Filter stats for this scenario
        scenario_stats = stats_df[stats_df['Scenario'] == scenario]
        
        # Print header
        print(f"{'Technique':<20} {'Count':<8} {'Mean':<10} {'SD':<10} {'SEM':<10} "
              f"{'Median':<10} {'Min':<8} {'Max':<8} {'Q1':<8} {'Q3':<8}")
        print("-" * 100)
        
        # Print stats for each technique
        for _, row in scenario_stats.iterrows():
            print(f"{row['Technique']:<20} {row['Count']:<8.0f} {row['Mean']:<10.2f} "
                  f"{row['Std Dev']:<10.2f} {row['SEM']:<10.2f} {row['Median']:<10.2f} "
                  f"{row['Min']:<8.2f} {row['Max']:<8.2f} {row['Q1']:<8.2f} {row['Q3']:<8.2f}")


def create_boxplot(df: pd.DataFrame, measure: str, output_dir: str = None) -> None:
    """
    Create a boxplot visualization for the specified measure.
    
    Args:
        df: DataFrame containing the SSQ data
        measure: The measure to visualize (e.g., 'Total Score', 'Nausea')
        output_dir: Directory to save the figure (if None, figure is not saved)
    """
    # Set up the plot style
    sns.set(style="whitegrid", font_scale=1.2)
    plt.figure(figsize=(12, 7))
    
    # Prepare data for plotting
    # Create a clean version of the mitigation technique names for better display
    df['Mitigation Technique'] = df['Select the Mitigation Technique'].apply(
        lambda x: 'Baseline' if 'Baseline' in x else x
    )
    
    # Create the boxplot
    ax = sns.boxplot(
        x='Select the Scenario:', 
        y=measure, 
        hue='Mitigation Technique',
        data=df,
        palette='muted',
        width=0.7,
        fliersize=5
    )
    
    # Improve the plot appearance
    plt.title(f'Boxplot of {measure} by Scenario and Mitigation Technique', fontsize=16, pad=20)
    plt.xlabel('Scenario', fontsize=14)
    plt.ylabel(measure, fontsize=14)
    
    # Adjust legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title="Mitigation Technique", fontsize=12, title_fontsize=13)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure if requested
    if output_dir and CONFIG['save_figures']:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{measure.replace(' ', '_')}_boxplot.png")
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Boxplot saved to {filename}")
    
    plt.show()


def create_enhanced_boxplot(df: pd.DataFrame, measure: str, stats_df: pd.DataFrame, output_dir: str = None) -> None:
    """
    Create an enhanced boxplot visualization with additional statistics.
    
    Args:
        df: DataFrame containing the SSQ data
        measure: The measure to visualize (e.g., 'Total Score', 'Nausea')
        stats_df: DataFrame with descriptive statistics
        output_dir: Directory to save the figure (if None, figure is not saved)
    """
    # Set up the plot style
    sns.set(style="whitegrid", font_scale=1.2)
    plt.figure(figsize=(14, 9))
    
    # Prepare data for plotting
    # Create a clean version of the mitigation technique names for better display
    df['Mitigation Technique'] = df['Select the Mitigation Technique'].apply(
        lambda x: 'Baseline' if 'Baseline' in x else x
    )
    
    # Create the boxplot
    ax = sns.boxplot(
        x='Select the Scenario:', 
        y=measure, 
        hue='Mitigation Technique',
        data=df,
        palette='muted',
        width=0.7,
        fliersize=5
    )
    
    # Add individual data points with jitter
    sns.stripplot(
        x='Select the Scenario:', 
        y=measure, 
        hue='Mitigation Technique',
        data=df,
        palette='dark:black',
        size=4,
        jitter=True,
        dodge=True,
        alpha=0.6,
        legend=False
    )
    
    # Annotate with statistics
    for scenario_idx, scenario in enumerate(CONFIG['scenarios']):
        for tech_idx, technique in enumerate(CONFIG['techniques']):
            # Get the display name for the technique
            tech_display = 'Baseline' if 'Baseline' in technique else technique
            
            # Get statistics for this group
            group_stats = stats_df[(stats_df['Scenario'] == scenario) & 
                                  (stats_df['Technique'] == tech_display)]
            
            if not group_stats.empty:
                # Position for the annotation
                x_pos = scenario_idx + (tech_idx - 1) * 0.3
                y_pos = group_stats['Q3'].values[0] + 0.5 * group_stats['IQR'].values[0]
                
                # Create annotation text
                stat_text = f"n={int(group_stats['Count'].values[0])}\n" \
                           f"mean={group_stats['Mean'].values[0]:.1f}\n" \
                           f"sd={group_stats['Std Dev'].values[0]:.1f}"
                
                # Add annotation
                ax.annotate(
                    stat_text,
                    xy=(x_pos, y_pos),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7)
                )
    
    # Improve the plot appearance
    plt.title(f'Boxplot of {measure} by Scenario and Mitigation Technique', fontsize=16, pad=20)
    plt.xlabel('Scenario', fontsize=14)
    plt.ylabel(measure, fontsize=14)
    
    # Adjust legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:3], labels[:3], title="Mitigation Technique", fontsize=12, title_fontsize=13)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure if requested
    if output_dir and CONFIG['save_figures']:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{measure.replace(' ', '_')}_enhanced_boxplot.png")
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Enhanced boxplot saved to {filename}")
    
    plt.show()


def create_box_and_bar_plot(df: pd.DataFrame, measure: str, stats_df: pd.DataFrame, output_dir: str = None) -> None:
    """
    Create a figure with both boxplot and bar chart for comparison, with fixed x-axis labels.
    
    Args:
        df: DataFrame containing the SSQ data
        measure: The measure to visualize (e.g., 'Total Score', 'Nausea')
        stats_df: DataFrame with descriptive statistics
        output_dir: Directory to save the figure (if None, figure is not saved)
    """
    # Set up the plot style
    sns.set(style="whitegrid", font_scale=1.2)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Prepare data for plotting
    df['Mitigation Technique'] = df['Select the Mitigation Technique'].apply(
        lambda x: 'Baseline' if 'Baseline' in x else x
    )
    
    # 1. Create the boxplot on the first axis
    sns.boxplot(
        x='Select the Scenario:', 
        y=measure, 
        hue='Mitigation Technique',
        data=df,
        palette='muted',
        width=0.7,
        fliersize=5,
        ax=ax1
    )
    
    # Add individual data points to boxplot
    sns.stripplot(
        x='Select the Scenario:', 
        y=measure, 
        hue='Mitigation Technique',
        data=df,
        palette='dark:black',
        size=4,
        jitter=True,
        dodge=True,
        alpha=0.6,
        legend=False,
        ax=ax1
    )
    
    ax1.set_title(f'Boxplot of {measure}', fontsize=14)
    ax1.set_xlabel('Scenario', fontsize=12)
    ax1.set_ylabel(measure, fontsize=12)
    
    # Adjust boxplot legend
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[:3], labels[:3], title="Mitigation Technique", fontsize=10, title_fontsize=11)
    
    # 2. Create bar chart on the second axis with FIXED LABELS
    # Define the number of groups and bars per group
    n_scenarios = len(CONFIG['scenarios'])
    n_techniques = len(CONFIG['techniques'])
    
    # Set width of bars
    bar_width = 0.25
    
    # Set positions for the bars
    index = np.arange(n_scenarios)
    
    # Define colors
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    
    # Create bars for each technique
    for i, technique in enumerate(CONFIG['techniques']):
        # Get display name
        tech_display = 'Baseline' if 'Baseline' in technique else technique
        
        # Collect means and errors for this technique across scenarios
        means = []
        errors = []
        
        for scenario in CONFIG['scenarios']:
            # Get statistics
            group_stats = stats_df[(stats_df['Scenario'] == scenario) & 
                                  (stats_df['Technique'] == tech_display)]
            
            if not group_stats.empty:
                means.append(group_stats['Mean'].values[0])
                errors.append(group_stats['SEM'].values[0])
            else:
                means.append(0)
                errors.append(0)
        
        # Plot bars for this technique
        bars = ax2.bar(index + i*bar_width, means, bar_width, yerr=errors, 
                       capsize=5, color=colors[i], label=tech_display)
        
        # Add value labels on bars
        for j, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + errors[j] + 2, 
                    f"{height:.1f}", ha='center', va='bottom', fontsize=10)
    
    # Set x-axis labels and ticks
    ax2.set_xticks(index + bar_width)
    ax2.set_xticklabels(CONFIG['scenarios'])
    
    # Add title and labels
    ax2.set_title(f'Mean {measure} with SEM', fontsize=14)
    ax2.set_ylabel(measure, fontsize=12)
    ax2.set_xlabel('Scenario', fontsize=12)
    
    # Add legend to bar chart
    ax2.legend(title="Mitigation Technique", fontsize=10, title_fontsize=11)
    
    # Add overall title
    fig.suptitle(f'Comparison of {measure} by Scenario and Mitigation Technique', 
                fontsize=16, y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    fig.subplots_adjust(top=0.9)
    
    # Save figure if requested
    if output_dir and CONFIG['save_figures']:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{measure.replace(' ', '_')}_combined_plot.png")
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Combined plot saved to {filename}")
    
    plt.show()


def main():
    """Main function to create visualizations and calculate statistics."""
    print("Starting Visualization and Statistical Analysis")
    
    # Create output directory if saving results
    if CONFIG['save_figures']:
        os.makedirs(CONFIG['output_dir'], exist_ok=True)
    
    # Load data
    df = load_data(CONFIG['file_path'])
    if df is None:
        print("Error: Could not load data. Analysis aborted.")
        return
    
    # Analyze each measure
    for measure in CONFIG['measures']:
        print(f"\n{'='*80}")
        print(f"ANALYZING {measure.upper()}")
        print(f"{'='*80}")
        
        # Calculate descriptive statistics
        stats_df = get_descriptive_stats(df, measure)
        
        # Print descriptive statistics
        print_descriptive_stats(stats_df, measure)
        
        # Export statistics to CSV
        if CONFIG['save_figures']:
            export_stats_to_csv(stats_df, measure, CONFIG['output_dir'])
        
        # Create standard boxplot
        create_boxplot(df, measure, CONFIG['output_dir'])
        
        # Create enhanced boxplot with statistics
        create_enhanced_boxplot(df, measure, stats_df, CONFIG['output_dir'])
        
        # Create combined box and bar plot
        create_box_and_bar_plot(df, measure, stats_df, CONFIG['output_dir'])
    
    print("\nAnalysis and visualization complete!")


if __name__ == "__main__":
    main()