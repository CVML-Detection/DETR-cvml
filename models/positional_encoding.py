import torch
from torch import nn
import math


class PositionalEncoding(nn.Module):
    def __init__(self):
        super().__init__()
        self.num_pos_feats = 128    # (hidden dim // 2)
        self.temperature = 10000
        self.normalize = True
        self.scale = 2 * math.pi

    def forward(self, feat):
        b = feat.shape[0]
        w = feat.shape[2]
        h = feat.shape[3]
        not_mask = torch.zeros(b, w, h, dtype=torch.bool).to(feat.device)
        # not_mask = ~mask
        y_embed = not_mask.cumsum(1, dtype=torch.float32)
        x_embed = not_mask.cumsum(2, dtype=torch.float32)
        if self.normalize:
            eps = 1e-6
            y_embed = y_embed / (y_embed[:, -1:, :] + eps) * self.scale     # Normalize, 2π가 scale로 ?
            x_embed = x_embed / (x_embed[:, :, -1:] + eps) * self.scale
        dim_t = torch.arange(self.num_pos_feats, dtype=torch.float32, device=feat.device)
        dim_t = self.temperature ** (2 * (dim_t // 2) / self.num_pos_feats)

        pos_x = x_embed[:, :, :, None] / dim_t
        pos_y = y_embed[:, :, :, None] / dim_t
        pos_x = torch.stack((pos_x[:, :, :, 0::2].sin(), pos_x[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos_y = torch.stack((pos_y[:, :, :, 0::2].sin(), pos_y[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos = torch.cat((pos_y, pos_x), dim=3).permute(0, 3, 1, 2)
        return pos