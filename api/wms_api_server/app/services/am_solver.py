"""
am_solver.py — Sprint 116: Attention Model inference для VRP.

Загружает обученную модель из models/am_vrp.pt и строит маршрут.
Используется как solver="attention_model" в /planner/solve.
"""

import logging
import os
from typing import Any

log = logging.getLogger(__name__)

_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "../../../../models/am_vrp.pt"
)


def is_available() -> bool:
    """Проверить доступность модели и PyTorch."""
    try:
        import torch  # noqa: F401
        return os.path.exists(_MODEL_PATH)
    except ImportError:
        return False


def solve_am(
    lats: list[float],
    lons: list[float],
    pallets: list[int],
    max_stops: int = 30,
) -> list[int] | None:
    """
    Запустить AM-инференс. Возвращает список индексов в порядке объезда,
    или None если модель недоступна.
    """
    if not is_available():
        log.debug("AM model not available; falling back to OR-Tools")
        return None
    try:
        import torch
        import torch.nn as nn

        checkpoint = torch.load(_MODEL_PATH, map_location="cpu")
        D_MODEL: int = checkpoint.get("d_model", 128)
        N_HEADS: int = checkpoint.get("n_heads", 8)
        N_LAYERS: int = checkpoint.get("n_layers", 3)

        class AMEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.embed = nn.Linear(3, D_MODEL)
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
        encoder.load_state_dict(checkpoint["encoder"])
        decoder.load_state_dict(checkpoint["decoder"])
        encoder.eval(); decoder.eval()

        n = min(len(lats), max_stops)
        lat_min, lat_max = min(lats[:n]), max(lats[:n])
        lon_min, lon_max = min(lons[:n]), max(lons[:n])
        lat_r = max(lat_max - lat_min, 1e-6)
        lon_r = max(lon_max - lon_min, 1e-6)

        x = torch.tensor(
            [[(lats[i] - lat_min) / lat_r,
              (lons[i] - lon_min) / lon_r,
              min(pallets[i] / 20.0, 1.0)] for i in range(n)],
            dtype=torch.float32,
        ).unsqueeze(0)

        with torch.no_grad():
            h = encoder(x)
            visited = set()
            route: list[int] = []
            current = 0
            for _ in range(n):
                query = h[:, current:current+1, :]
                logits = decoder(h, query).view(-1)
                for v in visited:
                    logits[v] = -1e9
                nxt = int(logits.argmax().item())
                route.append(nxt)
                visited.add(nxt)
                current = nxt

        return route
    except Exception as exc:
        log.warning("AM inference failed: %s", exc)
        return None
