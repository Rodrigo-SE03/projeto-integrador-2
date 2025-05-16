import torch
import torch.optim as optim
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.metrics import root_mean_squared_error
import joblib

from database.mongo import get_collection
from .preprocess import preprocess_data, preprocess_input
from .dataloader import create_dataloaders
from .LSTM import LSTM
from loguru import logger
import os

import matplotlib.pyplot as plt

N_EPOCHS = 500
BATCH_SIZE = 32
HIDDEN_SIZE = 128

#Leitura a cada 15 minutos
PASSO = 4*24  # 4 leituras por hora, 24 horas
N_STEPS = 4*1

def train_model(model, train_loader, loss_fn, optimizer, n_epochs):
    loss = []
    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            pred = model(X_batch)
            y_batch = y_batch.squeeze(-1)
            loss = loss_fn(pred, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            loss.append(loss.item())
        logger.info(f"Epoch {epoch+1}/{n_epochs} - Loss: {epoch_loss/len(train_loader):.4f}")
    
    plt.plot(loss)
    plt.title("Loss over epochs")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.savefig("ia_models/loss.png")
    plt.close()



def test_model(model, test_loader, scaler):
    model.eval()
    with torch.no_grad():
        preds = []
        truths = []
        for X_batch, y_batch in test_loader:
            pred = model(X_batch)
            preds.append(pred.numpy())
            truths.append(y_batch.numpy())

        preds = np.concatenate(preds)
        truths = np.concatenate(truths)

    
    y_test_original = scaler.inverse_transform(truths.squeeze(-1))
    y_pred_original = scaler.inverse_transform(preds)
    logger.info(f"Test RMSE: {root_mean_squared_error(y_test_original, y_pred_original)}")

    accuracy = np.mean(np.abs((y_test_original - y_pred_original) / y_test_original)) * 100
    logger.info(f"Test Accuracy: {accuracy:.2f}%")
    plt.plot(y_test_original, label='True')
    plt.plot(y_pred_original, label='Predicted')
    plt.title("True vs Predicted")
    plt.xlabel("Samples")
    plt.ylabel("Values")
    plt.legend()
    plt.savefig("ia_models/true_vs_predicted.png")
    plt.close()


def save_model(model, scaler, le):
    if not os.path.exists("ia_models"):
        os.makedirs("ia_models")

    torch.save(model, "ia_models/modelo.pt")
    joblib.dump(scaler, "ia_models/scaler.pkl")
    joblib.dump(le, "ia_models/le.pkl")


def load_model():
    model = torch.load("ia_models/modelo.pt", weights_only=False)
    model.eval()
    scaler = joblib.load("ia_models/scaler.pkl")
    le = joblib.load("ia_models/le.pkl")
    return model, scaler, le


def create_model(hidden_size=HIDDEN_SIZE, passo=PASSO, n_steps=N_STEPS, n_epochs=N_EPOCHS, batch_size=BATCH_SIZE):
    dados = list(get_collection().find())
    df = pd.DataFrame(dados)
    if df.empty:
        raise ValueError("Não há dados suficientes para treinar o modelo.")
    
    df.drop(columns=['_id'], inplace=True)
    df, X_train, X_test, y_train, y_test, scaler, le = preprocess_data(df, passo=passo, n_steps=n_steps)
    train_loader, test_loader = create_dataloaders(X_train, y_train, X_test, y_test, batch_size)

    input_size = X_train.shape[2]
    model = LSTM(input_size, n_steps=n_steps, passo=passo, hidden_size=hidden_size)
    loss_fn = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    train_model(model, train_loader, loss_fn, optimizer, n_epochs)
    test_model(model, test_loader, scaler)
    save_model(model, scaler, le)
    return model, scaler, le


def predict(model, scaler, le, mac):
    cursor = get_collection().find({"mac": mac}).sort("timestamp", -1).limit(model.n_steps)
    dados = list(cursor)
    if len(dados) < model.n_steps:
        raise ValueError("Não há dados suficientes para esse MAC.")
    
    dados = sorted(dados, key=lambda x: x['timestamp'])
    df = pd.DataFrame(dados)
    X_seq = preprocess_input(df, scaler, le, model.passo, model.n_steps)
    model.eval()
    with torch.no_grad():
        output = model(X_seq)
 
    # Reverter escala
    output_np = output.numpy().squeeze()
    output_original = scaler.inverse_transform(output_np.reshape(-1, 1)).flatten()

    return output_original[:model.passo]