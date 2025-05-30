# -*- coding: utf-8 -*-
"""Model_Notebook.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18QHN5UcKLTK7Za9vOI1PRj1zRqsCmH3j

# Importing Needed Liberaries
"""

!pip install transformers datasets scikit-learn

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from transformers import BertTokenizer, BertForSequenceClassification, get_scheduler
from torch.optim import AdamW
from tqdm import tqdm
import kagglehub
import datasets
from datasets import load_dataset
import shutil
from google.colab import files

import transformers
print(transformers.__version__)

"""# Loading the dataset"""

kagglehub.dataset_download("lakshmi25npathi/imdb-dataset-of-50k-movie-reviews")
path = os.path.join("/kaggle", "input", "imdb-dataset-of-50k-movie-reviews", "IMDB Dataset.csv")
print("Path to dataset files:", path)

df = pd.read_csv(path, encoding='latin-1')

len(df)

print(df.columns)

print(df['sentiment'].unique())

df['label'] = df['sentiment'].map({'positive': 1, 'negative': 0})

print(df.columns)

train_texts, test_texts, train_labels, test_labels = train_test_split(
    df['review'].values, df['label'].values, test_size=0.2, random_state=42)

len(train_texts)

len(test_texts)

"""# Tockenization and Bert Model"""

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length=512)
test_encodings = tokenizer(list(test_texts), truncation=True, padding=True, max_length=512)

class IMDbDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            'input_ids': torch.tensor(self.encodings['input_ids'][idx]),
            'attention_mask': torch.tensor(self.encodings['attention_mask'][idx]),
            'labels': torch.tensor(self.labels[idx])
        }

train_dataset = IMDbDataset(train_encodings, train_labels)
test_dataset = IMDbDataset(test_encodings, test_labels)

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs.")
    model = torch.nn.DataParallel(model)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

"""# Training the Model on the training data"""

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=8)

optimizer = AdamW(model.parameters(), lr=5e-5)
num_epochs = 40
num_training_steps = num_epochs * len(train_loader)
lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

model.train()
for epoch in range(5):
    print(f"Epoch {epoch+1}")
    loop = tqdm(train_loader, leave=True)
    for batch in loop:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss = loss.mean()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        loop.set_description(f"Epoch {epoch+1}")
        loop.set_postfix(loss=loss.item())

model.train()
for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}")
    loop = tqdm(train_loader, leave=True)
    for batch in loop:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss = loss.mean()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        loop.set_description(f"Epoch {epoch+1}")
        loop.set_postfix(loss=loss.item())

"""# Evaluating the Model on the testing data"""

model.eval()
preds, true_labels = [], []
with torch.no_grad():
    for batch in test_loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        preds.extend(predictions.cpu().numpy())
        true_labels.extend(batch['labels'].cpu().numpy())

print(classification_report(true_labels, preds))

"""# Saving the Model Files to use locally"""

model.save_pretrained("./bert_model")
tokenizer.save_pretrained("./bert_model")
print("Model saved to 'bert_model'")

shutil.make_archive('bert_model', 'zip', 'bert_model')
files.download('bert_model.zip')

model.module.save_pretrained("/kaggle/working/bert_model")
tokenizer.save_pretrained("/kaggle/working/bert_model")
print("Model saved to '/kaggle/working/bert_model'")

shutil.make_archive("/kaggle/working/bert_model", 'zip', "/kaggle/working/bert_model")
print("Zipped model saved to '/kaggle/working/bert_model.zip'")