import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration - Set your output directory here
OUTPUT_DIR = "output/Presence_Results"  # Change this to your desired output directory

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the data
data = pd.read_csv('data/SSQ/Post_SSQ.csv')

# Create correct mapping dictionary based on the provided VRUSE scale
presence_mapping = {
    'Very Unsatisfactory': 0,
    'Unsatisfactory': 1,
    'Neutral': 2,
    'Satisfactory': 3,
    'Very Satisfactory': 4
}

# Convert text ratings to numeric values using the mapping
data['Presence_Rating'] = data['VRUSE Overall Presence [Overall I would rate my sense of presence as:]'].map(presence_mapping)

# Verification step to ensure proper conversion
print("Verification of presence rating conversion:")
verification_sample = data[['VRUSE Overall Presence [Overall I would rate my sense of presence as:]', 'Presence_Rating']].head(5)
print(verification_sample)

# Function for analyzing presence by mitigation technique
def analyze_presence_by_technique(data, scenario_name, output_dir):
    # Filter data for the specific scenario
    scenario_data = data[data['Select the Scenario:'] == scenario_name].copy()
    
    # Group data by mitigation technique
    techniques = scenario_data['Select the Mitigation Technique'].unique()
    grouped_data = [scenario_data[scenario_data['Select the Mitigation Technique'] == tech]['Presence_Rating'].values 
                    for tech in techniques]
    
    # Descriptive statistics
    print(f"\n=== Analysis for {scenario_name} Scenario ===")
    descriptive_stats = []
    
    for i, tech in enumerate(techniques):
        mean = np.mean(grouped_data[i])
        std = np.std(grouped_data[i], ddof=1)
        sem = std / np.sqrt(len(grouped_data[i]))
        median = np.median(grouped_data[i])
        q1 = np.percentile(grouped_data[i], 25)
        q3 = np.percentile(grouped_data[i], 75)
        min_val = np.min(grouped_data[i])
        max_val = np.max(grouped_data[i])
        
        descriptive_stats.append({
            'Scenario': scenario_name,
            'Technique': tech,
            'N': len(grouped_data[i]),
            'Mean': mean,
            'Std_Dev': std,
            'SEM': sem,
            'Median': median,
            'Q1': q1,
            'Q3': q3,
            'Min': min_val,
            'Max': max_val
        })
        
        print(f"{tech}: Mean = {mean:.2f}, SD = {std:.2f}, SEM = {sem:.2f}, n = {len(grouped_data[i])}")
    
    # Normality and homogeneity of variance checks
    print("\nNormality Tests (Shapiro-Wilk):")
    normality_violated = False
    normality_results = []
    
    for i, tech in enumerate(techniques):
        if len(grouped_data[i]) >= 3:  # Minimum sample size for Shapiro-Wilk
            stat, p = stats.shapiro(grouped_data[i])
            normality_status = 'Normal' if p > 0.05 else 'Non-normal'
            if p <= 0.05:
                normality_violated = True
            normality_results.append({
                'Scenario': scenario_name,
                'Technique': tech,
                'Shapiro_W': stat,
                'Shapiro_p': p,
                'Normality_Status': normality_status
            })
            print(f"{tech}: W = {stat:.3f}, p = {p:.3f} ({normality_status})")
    
    # Homogeneity of variance test
    stat, p = stats.levene(*grouped_data)
    homogeneity_status = 'Equal variances' if p > 0.05 else 'Unequal variances'
    homogeneity_violated = p <= 0.05
    print(f"\nHomogeneity of Variance (Levene's Test): W = {stat:.3f}, p = {p:.3f} ({homogeneity_status})")
    
    # Store assumption test results
    assumption_results = {
        'Scenario': scenario_name,
        'Levene_W': stat,
        'Levene_p': p,
        'Homogeneity_Status': homogeneity_status,
        'Normality_Violated': normality_violated,
        'Homogeneity_Violated': homogeneity_violated
    }
    
    # Parametric or non-parametric analysis based on assumption checks
    if normality_violated or homogeneity_violated:
        print("\nAssumptions for parametric testing are violated. Proceeding with non-parametric analysis.")
        h_stat, h_p = stats.kruskal(*grouped_data)
        print(f"Kruskal-Wallis Test: H = {h_stat:.3f}, p = {h_p:.3f}")
        significance = 'Significant' if h_p < 0.05 else 'Not significant'
        print(f"Statistical significance: {significance}")
        
        # Effect size for Kruskal-Wallis (η² H)
        n = sum(len(group) for group in grouped_data)
        eta_h_squared = (h_stat - len(techniques) + 1) / (n - len(techniques))
        print(f"Effect size (η² H): {eta_h_squared:.3f}")
        
        primary_test = 'kruskal'
        primary_stat = h_stat
        primary_p = h_p
        primary_effect = eta_h_squared
    else:
        print("\nAssumptions for parametric testing are met. Proceeding with ANOVA.")
        f_val, p_val = stats.f_oneway(*grouped_data)
        print(f"One-way ANOVA: F = {f_val:.3f}, p = {p_val:.3f}")
        significance = 'Significant' if p_val < 0.05 else 'Not significant'
        print(f"Statistical significance: {significance}")
        
        # Effect size (Eta-squared)
        dfn = len(techniques) - 1
        dfd = sum(len(group) for group in grouped_data) - len(techniques)
        eta_squared = (dfn * f_val) / (dfn * f_val + dfd)
        print(f"Effect size (η²): {eta_squared:.3f}")
        
        primary_test = 'anova'
        primary_stat = f_val
        primary_p = p_val
        primary_effect = eta_squared
    
    # Store statistical test results
    statistical_results = {
        'Scenario': scenario_name,
        'Test_Type': primary_test,
        'Test_Statistic': primary_stat,
        'p_value': primary_p,
        'Effect_Size': primary_effect,
        'Significance': significance,
        'DF_Between': len(techniques) - 1,
        'DF_Within': sum(len(group) for group in grouped_data) - len(techniques)
    }
    
    # Post-hoc tests if primary test is significant
    posthoc_results = []
    if primary_p < 0.05:
        print("\nPost-hoc analysis:")
        if primary_test == 'anova':
            posthoc = pairwise_tukeyhsd(
                scenario_data['Presence_Rating'], 
                scenario_data['Select the Mitigation Technique'],
                alpha=0.05)
            print(posthoc)
            
            # Convert Tukey results to DataFrame
            posthoc_df = pd.DataFrame(data=posthoc.summary().data[1:], 
                                    columns=posthoc.summary().data[0])
            posthoc_df['Scenario'] = scenario_name
            posthoc_results = posthoc_df.to_dict('records')
        else:
            # Dunn's test for non-parametric post-hoc comparisons
            try:
                from scikit_posthocs import posthoc_dunn
                posthoc_data = {tech: group for tech, group in zip(techniques, grouped_data)}
                dunn_result = posthoc_dunn(posthoc_data, p_adjust='bonferroni')
                print("Dunn's test (p-values):")
                print(dunn_result)
                
                # Convert Dunn results to list of dictionaries
                for i, tech1 in enumerate(techniques):
                    for j, tech2 in enumerate(techniques):
                        if i < j:  # Only upper triangle to avoid duplicates
                            posthoc_results.append({
                                'Scenario': scenario_name,
                                'group1': tech1,
                                'group2': tech2,
                                'p_adj': dunn_result.iloc[i, j],
                                'reject': dunn_result.iloc[i, j] < 0.05
                            })
            except ImportError:
                print("scikit-posthocs not available. Skipping Dunn's test.")
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    means = [np.mean(group) for group in grouped_data]
    sems = [np.std(group, ddof=1) / np.sqrt(len(group)) for group in grouped_data]
    
    plt.bar(techniques, means, yerr=sems, capsize=10, alpha=0.7, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.axhline(y=2, color='gray', linestyle='--', alpha=0.5)  # Neutral line
    plt.ylim(0, 4)  # Set y-axis limits to match VRUSE scale (0-4)
    plt.ylabel('Mean Presence Rating (0-4)')
    plt.title(f'Mean Presence Ratings by Mitigation Technique ({scenario_name})')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    # Save plot to output directory
    plot_filename = os.path.join(output_dir, f'presence_ratings_{scenario_name.replace(" ", "_")}.png')
    plt.savefig(plot_filename, dpi=300)
    plt.close()  # Close the figure to free memory
    
    return {
        'test': primary_test,
        'stat_value': primary_stat,
        'p_value': primary_p,
        'effect_size': primary_effect,
        'means': means,
        'sems': sems,
        'df_between': len(techniques) - 1,
        'df_within': sum(len(group) for group in grouped_data) - len(techniques),
        'techniques': techniques,
        'descriptive_stats': descriptive_stats,
        'normality_results': normality_results,
        'assumption_results': assumption_results,
        'statistical_results': statistical_results,
        'posthoc_results': posthoc_results
    }

# Analyze each scenario separately
print(f"Results will be saved to: {OUTPUT_DIR}")
rc_results = analyze_presence_by_technique(data, 'Roller Coaster', OUTPUT_DIR)
td_results = analyze_presence_by_technique(data, 'Tower Defense', OUTPUT_DIR)

# Generate Excel file with all results
excel_filename = os.path.join(OUTPUT_DIR, f'VR_Presence_Analysis_Results.xlsx')

# Try to create Excel file with error handling
try:
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Descriptive Statistics Sheet
        desc_stats = rc_results['descriptive_stats'] + td_results['descriptive_stats']
        desc_df = pd.DataFrame(desc_stats)
        desc_df.to_excel(writer, sheet_name='Descriptive_Statistics', index=False)
        
        # Normality Tests Sheet
        norm_stats = rc_results['normality_results'] + td_results['normality_results']
        if norm_stats:
            norm_df = pd.DataFrame(norm_stats)
            norm_df.to_excel(writer, sheet_name='Normality_Tests', index=False)
        
        # Assumption Tests Sheet
        assumption_stats = [rc_results['assumption_results'], td_results['assumption_results']]
        assumption_df = pd.DataFrame(assumption_stats)
        assumption_df.to_excel(writer, sheet_name='Assumption_Tests', index=False)
        
        # Statistical Tests Sheet
        stat_stats = [rc_results['statistical_results'], td_results['statistical_results']]
        stat_df = pd.DataFrame(stat_stats)
        stat_df.to_excel(writer, sheet_name='Statistical_Tests', index=False)
        
        # Post-hoc Tests Sheet
        posthoc_stats = rc_results['posthoc_results'] + td_results['posthoc_results']
        if posthoc_stats:
            posthoc_df = pd.DataFrame(posthoc_stats)
            posthoc_df.to_excel(writer, sheet_name='Posthoc_Tests', index=False)
        
        # Summary Table for Publication
        summary_data = []
        for scenario, results in [('Roller Coaster', rc_results), ('Tower Defense', td_results)]:
            for i, tech in enumerate(results['techniques']):
                summary_data.append({
                    'Scenario': scenario,
                    'Technique': tech,
                    'Mean': results['means'][i],
                    'SEM': results['sems'][i],
                    'Mean_SEM_Format': f"{results['means'][i]:.2f} (±{results['sems'][i]:.2f})"
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary_Table', index=False)

    print(f"\nExcel file saved successfully: {excel_filename}")

except ImportError as e:
    print(f"Error: openpyxl not installed. Installing alternative CSV outputs...")
    print("To install openpyxl, run: pip install openpyxl")
    
    # Create CSV files as alternative
    desc_stats = rc_results['descriptive_stats'] + td_results['descriptive_stats']
    desc_df = pd.DataFrame(desc_stats)
    desc_df.to_csv(os.path.join(OUTPUT_DIR, 'Descriptive_Statistics.csv'), index=False)
    
    norm_stats = rc_results['normality_results'] + td_results['normality_results']
    if norm_stats:
        norm_df = pd.DataFrame(norm_stats)
        norm_df.to_csv(os.path.join(OUTPUT_DIR, 'Normality_Tests.csv'), index=False)
    
    assumption_stats = [rc_results['assumption_results'], td_results['assumption_results']]
    assumption_df = pd.DataFrame(assumption_stats)
    assumption_df.to_csv(os.path.join(OUTPUT_DIR, 'Assumption_Tests.csv'), index=False)
    
    stat_stats = [rc_results['statistical_results'], td_results['statistical_results']]
    stat_df = pd.DataFrame(stat_stats)
    stat_df.to_csv(os.path.join(OUTPUT_DIR, 'Statistical_Tests.csv'), index=False)
    
    posthoc_stats = rc_results['posthoc_results'] + td_results['posthoc_results']
    if posthoc_stats:
        posthoc_df = pd.DataFrame(posthoc_stats)
        posthoc_df.to_csv(os.path.join(OUTPUT_DIR, 'Posthoc_Tests.csv'), index=False)
    
    summary_data = []
    for scenario, results in [('Roller Coaster', rc_results), ('Tower Defense', td_results)]:
        for i, tech in enumerate(results['techniques']):
            summary_data.append({
                'Scenario': scenario,
                'Technique': tech,
                'Mean': results['means'][i],
                'SEM': results['sems'][i],
                'Mean_SEM_Format': f"{results['means'][i]:.2f} (±{results['sems'][i]:.2f})"
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(OUTPUT_DIR, 'Summary_Table.csv'), index=False)
    
    print("CSV files created as alternative:")
    print("- Descriptive_Statistics.csv")
    print("- Normality_Tests.csv") 
    print("- Assumption_Tests.csv")
    print("- Statistical_Tests.csv")
    print("- Posthoc_Tests.csv")
    print("- Summary_Table.csv")

except Exception as e:
    print(f"Error creating Excel file: {e}")
    print("Creating CSV files as backup...")
    
    # Create CSV files as backup
    desc_stats = rc_results['descriptive_stats'] + td_results['descriptive_stats']
    desc_df = pd.DataFrame(desc_stats)
    desc_df.to_csv(os.path.join(OUTPUT_DIR, 'Descriptive_Statistics.csv'), index=False)
    
    norm_stats = rc_results['normality_results'] + td_results['normality_results']
    if norm_stats:
        norm_df = pd.DataFrame(norm_stats)
        norm_df.to_csv(os.path.join(OUTPUT_DIR, 'Normality_Tests.csv'), index=False)
    
    assumption_stats = [rc_results['assumption_results'], td_results['assumption_results']]
    assumption_df = pd.DataFrame(assumption_stats)
    assumption_df.to_csv(os.path.join(OUTPUT_DIR, 'Assumption_Tests.csv'), index=False)
    
    stat_stats = [rc_results['statistical_results'], td_results['statistical_results']]
    stat_df = pd.DataFrame(stat_stats)
    stat_df.to_csv(os.path.join(OUTPUT_DIR, 'Statistical_Tests.csv'), index=False)
    
    posthoc_stats = rc_results['posthoc_results'] + td_results['posthoc_results']
    if posthoc_stats:
        posthoc_df = pd.DataFrame(posthoc_stats)
        posthoc_df.to_csv(os.path.join(OUTPUT_DIR, 'Posthoc_Tests.csv'), index=False)
    
    summary_data = []
    for scenario, results in [('Roller Coaster', rc_results), ('Tower Defense', td_results)]:
        for i, tech in enumerate(results['techniques']):
            summary_data.append({
                'Scenario': scenario,
                'Technique': tech,
                'Mean': results['means'][i],
                'SEM': results['sems'][i],
                'Mean_SEM_Format': f"{results['means'][i]:.2f} (±{results['sems'][i]:.2f})"
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(OUTPUT_DIR, 'Summary_Table.csv'), index=False)
    
    print("Backup CSV files created successfully!")

print(f"\nExcel file saved: {excel_filename}")

# Generate formal reporting for academic publication
print("\n===== FORMAL RESULTS =====")
print("\nVRUSE Overall Presence Analysis:")

# Roller Coaster results
if rc_results['test'] == 'anova':
    print(f"Roller Coaster scenario: F({rc_results['df_between']}, {rc_results['df_within']}) = {rc_results['stat_value']:.2f}, p = {rc_results['p_value']:.3f}, η² = {rc_results['effect_size']:.3f}")
else:
    print(f"Roller Coaster scenario: H({rc_results['df_between']}) = {rc_results['stat_value']:.2f}, p = {rc_results['p_value']:.3f}, η²H = {rc_results['effect_size']:.3f}")

# Tower Defense results
if td_results['test'] == 'anova':
    print(f"Tower Defense scenario: F({td_results['df_between']}, {td_results['df_within']}) = {td_results['stat_value']:.2f}, p = {td_results['p_value']:.3f}, η² = {td_results['effect_size']:.3f}")
else:
    print(f"Tower Defense scenario: H({td_results['df_between']}) = {td_results['stat_value']:.2f}, p = {td_results['p_value']:.3f}, η²H = {td_results['effect_size']:.3f}")

# Generate formatted table for paper inclusion
print("\nTable for Paper:")
techniques = [str(tech) for tech in rc_results['techniques']]
print("| Scenario | " + " | ".join(techniques) + " |")
print("| --- | " + " | ".join(["---" for _ in techniques]) + " |")
print(f"| Roller Coaster | " + " | ".join([f"{m:.2f} (±{s:.2f})" for m, s in zip(rc_results['means'], rc_results['sems'])]) + " |")
print(f"| Tower Defense | " + " | ".join([f"{m:.2f} (±{s:.2f})" for m, s in zip(td_results['means'], td_results['sems'])]) + " |")

print(f"\nAll results saved to directory: {OUTPUT_DIR}")
print(f"- PNG files: presence_ratings_Roller_Coaster.png, presence_ratings_Tower_Defense.png")
if os.path.exists(excel_filename):
    print(f"- Excel file: {os.path.basename(excel_filename)}")
else:
    print("- CSV files: Descriptive_Statistics.csv, Normality_Tests.csv, Assumption_Tests.csv, Statistical_Tests.csv, Posthoc_Tests.csv, Summary_Table.csv")