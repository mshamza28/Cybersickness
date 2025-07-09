# VR Sickness & Presence Analysis

## Overview

This project analyzes the effectiveness of different VR sickness mitigation techniques and presence ratings in VR environments using Simulator Sickness Questionnaire (SSQ) and VRUSE data. It provides statistical analysis, visualizations, and publication-ready outputs.

---

## Folder Structure

```
├── data/                # Raw and processed data files (e.g., Pre_SSQ.csv, Post_SSQ.csv)
├── scripts/             # Python scripts for analysis and visualization
├── output/              # Generated plots, statistics, and results
│   ├── SSQ_Results/         # Output from SSQ analysis (plots, CSVs)
│   └── Presence_Results/    # Output from VRUSE analysis (plots, Excel)
├── .venv/               # (Optional) Python virtual environment
```

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mshamza28/Cybersickness.git
   cd Cybersickness
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Data Format

### Example: `Pre_SSQ.csv` (before VR exposure)

| ID | Age | Gender | ... | Select the Scenario: | Select the Mitigation Technique | Before VR [General Discomfort] | ... | Nausea | Oculomotor | Disorientation | Total Score |
|----|-----|--------|-----|---------------------|-------------------------------|-------------------------------|-----|--------|------------|---------------|-------------|
| 4  | 25  | Male   | ... | Roller Coaster      | Baseline (No Mitigation Technique) | None (0) | ... | 9.54 | 15.16 | 13.92 | 14.96 |

### Example: `Post_SSQ.csv` (after VR exposure)

| ID | Age | Gender | Select the Scenario: | Select the Mitigation Technique | ... | VRUSE Overall Presence [Overall I would rate my sense of presence as:] | Nausea | Oculomotor | Disorientation | Total Score |
|----|-----|--------|---------------------|-------------------------------|-----|-----------------------------------------------------------------------|--------|------------|---------------|-------------|
| 4  | 25  | Male   | Roller Coaster      | Baseline (No Mitigation Technique) | ... | Very Satisfactory | 95.4 | 60.64 | 125.28 | 100.98 |

**Note:** Ensure your CSV files have the correct column headers as shown above.

---

## How to Run

1. Place your data files (`Pre_SSQ.csv`, `Post_SSQ.csv`) in the `data/` folder.
2. Run the desired analysis script from the `scripts/` folder:

   ```bash
   python scripts/SSQ_Data_Analysis.py
   python scripts/VRUSE_Analysis.py
   ```

3. Results and plots will be saved in the `output/` folder.

---

## Script Descriptions & Usage

### `SSQ_Data_Analysis.py`

- **Purpose:** Analyzes VR sickness mitigation using SSQ data.
- **Input:** `data/Post_SSQ.csv`
- **Output:** Plots (PNG) and descriptive statistics (CSV) in `output/SSQ_Results/`
- **How to run:**
  ```bash
  python scripts/SSQ_Data_Analysis.py
  ```

### `VRUSE_Analysis.py`

- **Purpose:** Analyzes presence ratings using VRUSE data.
- **Input:** `data/Post_SSQ.csv` (must contain VRUSE columns)
- **Output:** Plots (PNG) and results (Excel) in `output/Presence_Results/`
- **How to run:**
  ```bash
  python scripts/VRUSE_Analysis.py
  ```

---

## Example Outputs

- **Plots:** Boxplots and combined plots for each SSQ measure (e.g., `Total_Score_boxplot.png`, `Nausea_boxplot.png`).
- **Statistics:** CSV files with descriptive stats (e.g., `Total_Score_descriptive_stats.csv`).
- **Presence Analysis:** Plots for presence ratings (e.g., `presence_ratings_Tower_Defense.png`) and Excel summary (`VR_Presence_Analysis_Results.xlsx`).

---

## Analysis Workflow

1. **Prepare Data:** Collect and format your data as shown above.
2. **Run SSQ Analysis:** Execute `SSQ_Data_Analysis.py` to analyze sickness scores.
3. **Run VRUSE Analysis:** Execute `VRUSE_Analysis.py` to analyze presence ratings.
4. **Review Outputs:** Check the `output/` folder for plots and statistics.
5. **Interpret Results:** Use the generated outputs for reporting or publication.

---

## Troubleshooting & FAQ

- **File Not Found:** Ensure your data files are named and placed correctly in the `data/` folder.
- **Missing Columns:** Check that your CSV files have all required columns.
- **Missing Packages:** Install all dependencies with `pip install -r requirements.txt`. For advanced post-hoc tests, you may need `scikit-posthocs`:
  ```bash
  pip install scikit-posthocs
  ```
- **Output Not Generated:** Check the console for error messages and ensure the `output/` directory is writable.

---

## Requirements

See `requirements.txt` for a full list. Main packages:
- pandas
- numpy
- matplotlib
- seaborn
- scipy
- statsmodels

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## Citation

If you use this code or data in your research, please cite:

```
[Add your citation here, e.g., paper reference or DOI]
```

---

## License

MIT License (or specify your license here)

---

## Contact

For questions or support, contact [your email or GitHub profile]. 