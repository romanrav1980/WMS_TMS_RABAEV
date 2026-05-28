"""
train_am.py — Sprint 115-116: Attention Model VRP training.

Упрощённая реализация Attention Model (трансформер) для задачи TSP/VRP.
Архитектура: Encoder (MHA + FFN) → Decoder (pointer) → маршрут.

Запуск:
    python scripts/attention_model/train_am.py \\
        --dataset data/vrp_dataset.json \\
        --epochs 100 \\
        --output models/am_vrp.pt

Требования:
    pip install torch numpy
"""

import argparse
import json
import os
import sys


def train(dataset_path: str, epochs: int, output: str) -> None:
    try:
        import torch
        import torch.nn as nn
        import numpy as np
    except ImportError:
        print("ERROR: PyTorch not installed. Run: pip install torch numpy")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Dataset: {len(dataset)} trips")
    if len(dataset) < 100:
        print("WARNING: Very small dataset — model will overfit. Need 1000+ trips.")

    # --- Simple Attention Model -----------------------------------------------
    D_MODEL = 128
    N_HEADS = 8
    N_LAYERS = 3
    MAX_STOPS = 30

    class AMEncoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embed = nn.Linear(3, D_MODEL)  # lat, lon, pallets
            layer = nn.TransformerEncoderLayer(D_MODEL, N_HEADS, dim_feedforward=512, batch_first=True)
            self.transformer = nn.TransformerEncoder(layer, N_LAYERS)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.transformer(self.embed(x))

    class AMDecoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.attn = nn.MultiheadAttention(D_MODEL, N_HEADS, batch_first=True)
            self.query_proj = nn.Linear(D_MODEL, D_MODEL)
            self.ptr = nn.Linear(D_MODEL, 1)

        def forward(self, h: "torch.Tensor", query: "torch.Tensor") -> "torch.Tensor":
            q = self.query_proj(query)
            attn_out, _ = self.attn(q, h, h)
            return self.ptr(attn_out).squeeze(-1)

    encoder = AMEncoder()
    decoder = AMDecoder()
    optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-4)

    def prepare_sample(trip: dict) -> "tuple[torch.Tensor, torch.Tensor]":
        stops = trip["stops"][:MAX_STOPS]
        n = len(stops)
        # Normalize lat/lon to [0,1] within the trip
        lats = [s["lat"] for s in stops]
        lons = [s["lon"] for s in stops]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)
        lat_range = max(lat_max - lat_min, 1e-6)
        lon_range = max(lon_max - lon_min, 1e-6)
        x = torch.tensor(
            [[(s["lat"] - lat_min) / lat_range,
              (s["lon"] - lon_min) / lon_range,
              min(s["pallets"] / 20.0, 1.0)] for s in stops],
            dtype=torch.float32,
        ).unsqueeze(0)  # (1, n, 3)
        # Target: current ORD as label (1-indexed → 0-indexed)
        target = torch.tensor([s["ord"] - 1 for s in stops], dtype=torch.long)
        return x, target

    print(f"Training for {epochs} epochs...")
    best_loss = float("inf")

    geo_trips = [t for t in dataset if len(t.get("stops", [])) >= 2]
    if not geo_trips:
        print("ERROR: No trips with coordinates found.")
        return

    for epoch in range(epochs):
        total_loss = 0.0
        np.random.shuffle(geo_trips)
        for trip in geo_trips[:min(len(geo_trips), 200)]:  # max 200 per epoch for speed
            x, target = prepare_sample(trip)
            if x.shape[1] < 2:
                continue
            optimizer.zero_grad()
            h = encoder(x)  # (1, n, D)
            query = h[:, :1, :]  # first node as query
            logits = decoder(h, query)  # (1, 1, n)
            logits = logits.view(1, -1)
            loss = nn.functional.cross_entropy(logits, target[:1])
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg = total_loss / max(len(geo_trips), 1)
        if epoch % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} — loss: {avg:.4f}")
        if avg < best_loss:
            best_loss = avg

    os.makedirs(os.path.dirname(output), exist_ok=True)
    torch.save({
        "encoder": encoder.state_dict(),
        "decoder": decoder.state_dict(),
        "d_model": D_MODEL,
        "n_heads": N_HEADS,
        "n_layers": N_LAYERS,
        "max_stops": MAX_STOPS,
        "best_loss": best_loss,
    }, output)
    print(f"Model saved to {output} (best loss: {best_loss:.4f})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/vrp_dataset.json")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--output", default="models/am_vrp.pt")
    args = parser.parse_args()
    train(args.dataset, args.epochs, args.output)
