# FTM Type Predict

> This repo has the code associated with a model which, given a snippet of text, predicts what FTM type it probably is


## Commands:

- create-training-data: Creates training data using input from `aleph sample-entities`
- train-model: Trains a type-predict model
- evaluate-model: Evaluates model precision and generates a confusion matrix
- test-model: Reads input from stdin or newline-deliniated file and shows model prediction for that text


## Example:

```
$ pip install -e .[analysis]

$ followthemoney-typepredict create-training-data ./sample_entities.jsonl ./data/

$ followthemoney-typepredict train-model --tune-durration 30 ./data/ ./model.ftq
Training type model with the following parameters:                   
        Tune: data/valid.txt                                                                                        
        Train: data/train.txt                                                                                                       
        Valid: data/valid.txt                                                                                                   
        Quantize: data/train.txt       
        Tune Durration: 30                                                                                                        
Progress: 100.0% Trials:   11 Best score:  0.973257 ETA:   0h 0m 0s                                                               
Training again with best arguments                                                                                                  
Read 0M words                                                                                             
Number of words:  21633                                                                                                        
Number of labels: 6                                                                                                               
Progress: 100.0% words/sec/thread:  123951 lr:  0.000000 avg.loss:  0.009439 ETA:   0h 0m 0s                                  
Quantizing model                                                                                           
Fitting done. Model evaluation:                                                                                                     
{'__label__address': {'f1score': 1.38, 'precision': 0.69, 'recall': nan},                                 
 '__label__date': {'f1score': 1.989071038251366,                                                                   
                   'precision': 0.994535519125683,
                   'recall': nan},                                                                                                
 '__label__email': {'f1score': 1.7419354838709677,      
                    'precision': 0.8709677419354839,                                                                
                    'recall': nan},                                                                                                 
 '__label__identifier': {'f1score': 1.8571428571428572,                                                                         
                         'precision': 0.9285714285714286,                                                                           
                         'recall': nan},                                                                                    
 '__label__name': {'f1score': 1.9759519038076152,                                                                                 
                   'precision': 0.9879759519038076,                                                                            
                   'recall': nan},                                                                                                
 '__label__phone': {'f1score': 2.0, 'precision': 1.0, 'recall': nan}}                                                          

$ followthemoney-typepredict evaluate-model --plot ./eval.png ./model.ftq ./data/valid.txt
{'__label__address': {'f1score': 1.38, 'precision': 0.69, 'recall': nan},
 '__label__date': {'f1score': 1.989071038251366,
                   'precision': 0.994535519125683,
                   'recall': nan},
 '__label__email': {'f1score': 1.7419354838709677,
                    'precision': 0.8709677419354839,
                    'recall': nan},
 '__label__identifier': {'f1score': 1.8571428571428572,
                         'precision': 0.9285714285714286,
                         'recall': nan},
 '__label__name': {'f1score': 1.9759519038076152,
                   'precision': 0.9879759519038076,
                   'recall': nan},
 '__label__phone': {'f1score': 2.0, 'precision': 1.0, 'recall': nan}}

$ echo "Micha Gorelick" | followthemoney-typepredict test-model ./model.ftq
[('__label__name', 1.000004768371582),
 ('__label__email', 1.3716477042180486e-05),
 ('__label__address', 1.1603669918258674e-05),
 ('__label__phone', 1.002274530037539e-05),
 ('__label__date', 1.0007415767177008e-05),
 ('__label__identifier', 1.0000146176025737e-05)]
```
