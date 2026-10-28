# Roda no seu computador (PowerShell 5.1), a partir da pasta do projeto: .\3c_baixar_real_nativo_local.ps1
# Baixa os ORIGINAIS do Wikimedia Commons e salva o recorte central 512x512 alinhado a 8 px (PNG, sem reamostragem)
# em dataset\real_nativo\. Retoma de onde parou. No fim cria dataset\real_nativo.zip para enviar ao Drive.
param([int]$Limite = 0, [switch]$SoZip)   # -Limite 5 baixa so 5 (teste); 0 = todas. -SoZip so monta o zip com o que ja foi baixado

Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = "Stop"
$dest = Join-Path $PSScriptRoot "dataset\real_nativo"; New-Item -ItemType Directory -Force $dest | Out-Null
$tmp = Join-Path $env:TEMP "commons_original.tmp"; $tmpj = Join-Path $env:TEMP "commons_api.json"
$ua = "tcc-pesquisa-detectores/1.0 (pesquisa academica)"
$logp = Join-Path $PSScriptRoot "dataset\real_nativo_log_local.csv"

$D = Import-Csv (Join-Path $PSScriptRoot "dataset\dataset_politicos_br.csv") -Encoding UTF8 |
     Where-Object { $_.rotulo -eq "real" -and $_.arquivo_local -like "real_oficial/*" }
if ($Limite -gt 0) { $D = $D | Select-Object -First $Limite }
if ($SoZip) { $D = @() }
"$($D.Count) reais no CSV"

function Pede($url, $saida) {   # curl.exe; em 429/5xx espera o Retry-After que o Wikimedia manda (600 s nos originais) e tenta de novo
    for ($t = 1; $t -le 6; $t++) {
        $h = (& curl.exe -s -L -D - -A $ua -o $saida $url) -join "`n"
        $code = [int]([regex]::Matches($h, "HTTP/\S+ (\d+)") | Select-Object -Last 1).Groups[1].Value
        if ($code -eq 200) { return }
        if ($code -ne 429 -and $code -lt 500) { throw "HTTP $code" }
        $m = [regex]::Match($h, "(?im)^retry-after:\s*(\d+)"); $w = if ($m.Success) { [int]$m.Groups[1].Value + 5 } else { 15 * $t }
        Write-Host "  HTTP $code, espera ${w}s"; Start-Sleep $w
    }
    throw "falhou apos 6 tentativas"
}

$log = @(); $i = 0
foreach ($r in $D) {
    $i++; $base = [IO.Path]::GetFileNameWithoutExtension($r.arquivo_local); $out = Join-Path $dest "$base.png"
    if (Test-Path $out) { continue }
    try {
        $title = [uri]::UnescapeDataString($r.fonte_url.Substring($r.fonte_url.IndexOf("/wiki/") + 6))
        $api = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|size&redirects=1&format=json&titles=" + [uri]::EscapeDataString($title)
        Pede $api $tmpj; $j = Get-Content $tmpj -Raw -Encoding UTF8 | ConvertFrom-Json
        $ii = ($j.query.pages.PSObject.Properties | Select-Object -First 1).Value.imageinfo[0]
        if ([Math]::Min($ii.width, $ii.height) -lt 512) { $log += [pscustomobject]@{ base = $base; largura_orig = $ii.width; altura_orig = $ii.height; status = "menor_que_512"; url = $ii.url }; continue }
        Pede $ii.url $tmp
        $img = [System.Drawing.Bitmap]::FromFile($tmp)
        $w = $img.Width; $h = $img.Height
        $x = [Math]::Floor([Math]::Floor(($w - 512) / 2) / 8) * 8; $y = [Math]::Floor([Math]::Floor(($h - 512) / 2) / 8) * 8
        $c = $img.Clone((New-Object System.Drawing.Rectangle $x, $y, 512, 512), [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
        $c.Save($out, [System.Drawing.Imaging.ImageFormat]::Png); $c.Dispose(); $img.Dispose()
        $log += [pscustomobject]@{ base = $base; largura_orig = $w; altura_orig = $h; x = $x; y = $y; status = "ok"; url = $ii.url }
        Write-Host "[$i/$($D.Count)] $base ok"
    } catch {
        $log += [pscustomobject]@{ base = $base; status = "erro: $($_.Exception.Message)"; url = $r.fonte_url }
        Write-Host "[$i/$($D.Count)] $base ERRO: $($_.Exception.Message)"
    }
    Start-Sleep 25   # o Wikimedia limita download de originais; ~1 a cada 30 s foi o ritmo que passou na primeira rodada
}
if ($log.Count) { $log | Export-Csv $logp -NoTypeInformation -Encoding UTF8 }
Remove-Item $tmp -ErrorAction SilentlyContinue

$n = (Get-ChildItem $dest -Filter *.png).Count
$zip = Join-Path $PSScriptRoot "dataset\real_nativo.zip"; Remove-Item $zip -ErrorAction SilentlyContinue
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($dest, $zip, [IO.Compression.CompressionLevel]::NoCompression, $true)
"$n recortes -> $zip"
