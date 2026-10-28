# Cole em uma célula do Colab (GPU não é necessária). Gera MyDrive/tcc_politicos/real_nativo.zip
# a partir dos ORIGINAIS do Wikimedia Commons: recorte central 512x512 alinhado à grade 8x8 do JPEG,
# sem reamostragem, salvo em PNG. Retoma de onde parou (pula o que já está em real_nativo/).
import os, io, time, zipfile, urllib.parse, requests, pandas as pd
from PIL import Image
from tqdm.auto import tqdm
from google.colab import drive; drive.mount('/content/drive')
Image.MAX_IMAGE_PIXELS = None
ROOT = "/content/drive/MyDrive/tcc_politicos"; DEST = f"{ROOT}/real_nativo"; os.makedirs(DEST, exist_ok=True)

CSV = next((p for p in (f"{ROOT}/dataset_politicos_br.csv", "/content/dataset_politicos_br.csv") if os.path.exists(p)), None)
if CSV is None:   # envie dataset/dataset_politicos_br.csv do seu computador
    from google.colab import files; files.upload(); CSV = "/content/dataset_politicos_br.csv"
D = pd.read_csv(CSV)
D = D[(D.rotulo == "real") & D.arquivo_local.str.startswith("real_oficial/")].reset_index(drop=True)
print(len(D), "reais no CSV")

S = requests.Session(); S.headers["User-Agent"] = "tcc-pesquisa-detectores/1.0 (pesquisa academica; Colab)"
API = "https://commons.wikimedia.org/w/api.php"
def get(url, **kw):
    for t in range(5):
        r = S.get(url, timeout=120, **kw)
        if r.status_code == 429 or r.status_code >= 500: time.sleep(5 * (t + 1)); continue
        r.raise_for_status(); return r
    raise RuntimeError(f"falhou: {url}")
def original_url(page_url):
    title = urllib.parse.unquote(page_url.split("/wiki/", 1)[1])
    j = get(API, params=dict(action="query", titles=title, prop="imageinfo", iiprop="url|size", redirects=1, format="json")).json()
    ii = next(iter(j["query"]["pages"].values()))["imageinfo"][0]
    return ii["url"], ii["width"], ii["height"]

logp = f"{ROOT}/real_nativo_log.csv"
log = pd.read_csv(logp).to_dict("records") if os.path.exists(logp) else []
feitas = {r["base"] for r in log}
for _, r in tqdm(D.iterrows(), total=len(D)):
    base = os.path.splitext(os.path.basename(r.arquivo_local))[0]
    if base in feitas or os.path.exists(f"{DEST}/{base}.png"): continue
    try:
        url, w, h = original_url(r.fonte_url)
        if min(w, h) < 512: log.append(dict(base=base, largura_orig=w, altura_orig=h, x="", y="", url=url, status="menor_que_512")); continue
        im = Image.open(io.BytesIO(get(url).content)); im.load()
        orient = im.getexif().get(274, 1)            # orientação EXIF registrada, sem aplicar (mantém a grade de blocos do JPEG)
        w, h = im.size; im = im.convert("RGB")
        x, y = ((w - 512) // 2 // 8) * 8, ((h - 512) // 2 // 8) * 8
        im.crop((x, y, x + 512, y + 512)).save(f"{DEST}/{base}.png")
        log.append(dict(base=base, largura_orig=w, altura_orig=h, x=x, y=y, url=url, status="ok", exif_orient=orient))
    except Exception as e:
        log.append(dict(base=base, largura_orig="", altura_orig="", x="", y="", url=r.fonte_url, status=f"erro: {e}"[:200]))
    pd.DataFrame(log).to_csv(logp, index=False); time.sleep(0.5)

L = pd.DataFrame(log); print(L.status.str[:12].value_counts())
pngs = sorted(f for f in os.listdir(DEST) if f.endswith(".png"))
with zipfile.ZipFile(f"{ROOT}/real_nativo.zip", "w", zipfile.ZIP_STORED) as z:
    for f in pngs: z.write(f"{DEST}/{f}", f"real_nativo/{f}")
print(len(pngs), "recortes ->", f"{ROOT}/real_nativo.zip")
