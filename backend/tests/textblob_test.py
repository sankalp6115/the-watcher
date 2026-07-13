from textblob import TextBlob
incorrect = "ceertain conditionaas durring seveal ggeneratioons aree modiffied in thhe sae maner"
txtBlb = TextBlob(incorrect)
print(txtBlb.correct().string)
