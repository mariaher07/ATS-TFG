# From Abstracts to Titles: Experiments with Sequence-to-Sequence models
This repository includes the code used for developing the Bachelor Thesis named after this repository, written by María Hernández Padilla, 2021.

Datasets used for the project:
- News dataset: https://www.kaggle.com/sunnysai12345/news-summary 
- ArXiv dataset: https://www.kaggle.com/Cornell-University/arxiv



Instructions for executing:

- Loading dataset and preprocessing with nltk: load_preprocess_arxiv.ipynb, load_preprocess_arxiv.ipynb
  This is done using Google Colab; in "data_path" and "results_path" add the paths needed.
  
  
- Training the models: 
    - Modify "data_path" and "results_path"
    - attention.py should be imported. Import Attention mechanism class (Bahdanaus architecture) extracted from https://github.com/madhav727/abstractive-news-summary/blob/master/attention.py
    - Inputs are the results from "loading and preprocessing" section.
    - Results will be model predictions for the test subdataset.
    
  
  
- Results after training the models are included in predictions_results folder.
- Assessment using ROUGE framework: rouge.ipynb
