import torch
import pandas as pd
import numpy as np
from database.mongo import get_collection
from ..preprocess import preprocess_data, preprocess_input


def predict(model, scaler, le, mac):
    cursor = get_collection().find({"mac": mac}).sort("timestamp", -1).limit(model.passo)
    dados = list(cursor)
    if len(dados) < model.passo:
        raise ValueError("Não há dados suficientes para esse MAC.")
    
    dados = sorted(dados, key=lambda x: x['timestamp'])
    df = pd.DataFrame(dados)

    X_seq = preprocess_input(df, scaler, le, model.passo, future_steps=1)
    model.eval()

    predictions = []
    with torch.no_grad():
        for _ in range(model.future_steps):
            out = model(X_seq)
            next_pred = out[:, -1:, :]
            original_value = scaler.inverse_transform(next_pred.squeeze().cpu().numpy().reshape(-1, 1)).flatten()[0]
            predictions.append(original_value)
            new_input = next_pred.cpu()
            X_seq = X_seq[:, 1:, :]
            X_seq = torch.cat([X_seq, new_input], dim=1)

    return np.array(predictions)