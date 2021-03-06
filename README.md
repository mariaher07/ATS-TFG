# From Abstracts to Titles: Experiments with Sequence-to-Sequence models
This repository includes the code used for developing the Bachelor Thesis named after this repository, written by María Hernández Padilla, 2021.




**Datasets used for the project**:
- [News dataset](https://www.kaggle.com/sunnysai12345/news-summary) 
- [ArXiv dataset](https://www.kaggle.com/Cornell-University/arxiv)







**Instructions for executing**:

- Loading dataset and preprocessing with nltk: "load_preprocess_arxiv.ipynb", "load_preprocess_arxiv.ipynb".
  
  This is done using Google Colab; in "data_path" and "results_path" add the paths needed.
  
  
- Training the models: 
    - Two files: "model_gpu_arixv.ipynb" and "model_gpu_news.ipynb". Ideally, this part should be run on GPU. These two files contain the same code, only changing the limitation for the headline size for each dataset.
      
      
      Dependencies: "Python 3.6.4", "CUDA/10.0.130" and "cuDNN/7.6.3.30-CUDA-10.0.130"
      
    - Modify "data_path" and "results_path"
    - attention.py should be imported. Import Attention mechanism class (Bahdanaus architecture) extracted from [attention class](https://github.com/madhav727/abstractive-news-summary/blob/master/attention.py)
    - Inputs are the results from "loading and preprocessing" section.
    - Results will be model predictions for the test subdataset.
    
  
  
- Results after training the models are included in predictions_results folder.
- Assessment using ROUGE framework: rouge.ipynb
