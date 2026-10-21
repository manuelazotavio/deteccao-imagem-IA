# Cole em uma célula do Colab (mesma sessão dos experimentos).
# Usa SÓ os CSVs que você já tem: nenhuma GPU necessária.
import pandas as pd, numpy as np
from sklearn.metrics import (roc_auc_score, average_precision_score, roc_curve,
                             precision_recall_curve, confusion_matrix)
import matplotlib.pyplot as plt

D = "/content/experimento_detectores/"
fsd = pd.read_csv(D + "resultados_fsd_512.csv")
uni = pd.read_csv(D + "resultados_univfd.csv")
print(fsd.columns.tolist()); print(uni.columns.tolist())  # confira os nomes abaixo

# >>> AJUSTE ESTES NOMES conforme o print acima <<<
FSD_SCORE, FSD_LABEL = "z_score", "label"        # label: 1 = fake, 0 = real
UNI_SCORE, UNI_LABEL = "score_univfd", "label"

# FSD: score MAIS NEGATIVO = mais fake (limiar -2). Inverter para "maior = mais fake".
y_f, s_f = fsd[FSD_LABEL].values, -fsd[FSD_SCORE].values
y_u, s_u = uni[UNI_LABEL].values, uni[UNI_SCORE].values

def boot_ci(y, s, fn, n=2000, seed=0):
    rng = np.random.default_rng(seed); v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(set(y[i])) == 2: v.append(fn(y[i], s[i]))
    return np.percentile(v, [2.5, 97.5])

rows = []
for nome, y, s in [("FSD", y_f, s_f), ("UnivFD", y_u, s_u)]:
    auc, ap = roc_auc_score(y, s), average_precision_score(y, s)
    lo, hi = boot_ci(y, s, roc_auc_score)
    rows.append([nome, auc, lo, hi, ap]);
res = pd.DataFrame(rows, columns=["detector", "AUC", "IC95_inf", "IC95_sup", "AP"])
print(res.round(3)); res.to_csv(D + "auc_ap.csv", index=False)

# Limiar ótimo (Youden) e desempenho nele — mostra se o problema é o LIMIAR ou o MODELO
for nome, y, s in [("FSD", y_f, s_f), ("UnivFD", y_u, s_u)]:
    fpr, tpr, th = roc_curve(y, s); k = np.argmax(tpr - fpr)
    pred = s >= th[k]; tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    print(f"{nome}: limiar Youden={th[k]:.3f} recall={tp/(tp+fn):.2f} "
          f"especificidade={tn/(tn+fp):.2f} acurácia={(tp+tn)/len(y):.2f}")

# Curvas ROC e PR
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for nome, y, s in [("FSD", y_f, s_f), ("UnivFD", y_u, s_u)]:
    fpr, tpr, _ = roc_curve(y, s); ax[0].plot(fpr, tpr, label=f"{nome} (AUC={roc_auc_score(y,s):.2f})")
    p, r, _ = precision_recall_curve(y, s); ax[1].plot(r, p, label=nome)
ax[0].plot([0, 1], [0, 1], "k--"); ax[0].set(xlabel="Falso positivo", ylabel="Recall (fake)", title="ROC"); ax[0].legend()
ax[1].set(xlabel="Recall", ylabel="Precisão", title="Precisão-Recall"); ax[1].legend()
plt.tight_layout(); plt.savefig(D + "roc_pr.png", dpi=200)

# Varredura de limiares do UnivFD (tabela para o TCC)
sw = []
for t in np.arange(0.05, 1.0, 0.05):
    pred = s_u >= t; tn, fp, fn, tp = confusion_matrix(y_u, pred, labels=[0, 1]).ravel()
    sw.append([round(t, 2), (tp+tn)/len(y_u), tp/(tp+fn), tn/(tn+fp), tp/(tp+fp) if tp+fp else np.nan])
sw = pd.DataFrame(sw, columns=["limiar", "acuracia", "recall_fake", "especificidade", "precisao_fake"])
print(sw.round(2)); sw.to_csv(D + "varredura_limiar_univfd.csv", index=False)

# McNemar: FSD vs UnivFD têm diferença real de acerto? (b=37, c=31 no seu registro)
from scipy.stats import binomtest
print("McNemar exato p =", binomtest(31, 31 + 37, 0.5).pvalue)
