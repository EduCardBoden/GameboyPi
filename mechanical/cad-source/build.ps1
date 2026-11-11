# GameboyPi Gehäuse: Kollisionsprüfung + STL-Export + Vorschaubilder (OpenSCAD 2021.01)
#   -SkipCheck  nur STLs und Vorschaubilder (die Kollisionsprüfung dauert ~1 min pro Bauteil)
param([switch]$SkipCheck)
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$o = "C:\Program Files\OpenSCAD\openscad.com"
$scad = "gameboy_pi_case.scad"
$stl = Resolve-Path "..\stl"
$prev = Resolve-Path "..\previews"
New-Item -ItemType Directory -Force build | Out-Null

function Part($name) {
    # OpenSCAD unter PowerShell 5.1: Anführungszeichen im -D-Wert escapen
    & $o -o "$stl\$name.stl" -D "part=\`"$name\`"" $scad 2>&1 | Select-String "ERROR|WARNING|Volumes"
}

# 1) Kollisionsprüfung: jeder Bauteil-Hüllkörper gegen beide Schalen (leer = OK)
$n = if ($SkipCheck) { 0 } else { (Select-String -Path $scad -Pattern '^\s+\["[^"]+",\s*\[').Count }
$report = @("# Kollisionspruefung $(Get-Date -Format s)", "")
$fail = 0
# parallel, je ein OpenSCAD-Prozess pro Bauteil (max. 8 gleichzeitig)
$jobs = @()
for ($i = 0; $i -lt $n; $i++) {
    while (@($jobs | Where-Object State -eq "Running").Count -ge 8) { Start-Sleep -Milliseconds 500 }
    $jobs += Start-Job -ArgumentList $o, $i, $PSScriptRoot, $scad -ScriptBlock {
        param($o, $i, $dir, $scad)
        Set-Location $dir
        $out = & $o -o "build\check_$i.stl" -D "part=\`"check\`"" -D "check_idx=$i" $scad 2>&1 | Out-String
        Remove-Item "build\check_$i.stl" -ErrorAction SilentlyContinue
        $name = ([regex]::Match($out, 'CHECK ([^"]+)')).Groups[1].Value
        [pscustomobject]@{ i = $i; name = $name; ok = ($out -match "top level object is empty|No top level geometry") }
    }
}
foreach ($r in ($jobs | Wait-Job | Receive-Job | Sort-Object i)) {
    if ($r.ok) { $report += "OK         $($r.name)" } else { $report += "KOLLISION  $($r.name)"; $fail++ }
}
$jobs | Remove-Job
if (-not $SkipCheck) {
    $report += "", "Ergebnis: $fail Kollision(en) bei $n Bauteilen"
    $report | Set-Content build\collision_report.txt -Encoding utf8
    $report | Write-Host
}

# 2) STL-Export
foreach ($p in "front", "front_logo_silver", "front_logo_purple", "back", "back_logo_silver", "back_logo_purple",
               "dpad", "ab", "startselect", "knob", "spacers") { Write-Host "STL $p"; Part $p }

# 3) Vorschaubilder
& $o -o "$prev\front.png" -D "part=\`"front\`"" --render --imgsize=900,1200 --camera=42,70,0,180,0,180,320 --colorscheme=Tomorrow $scad 2>&1 | Out-Null
& $o -o "$prev\back_inside.png" -D "part=\`"back\`"" --render --imgsize=1000,1100 --camera=42,70,0,35,0,20,330 --colorscheme=Tomorrow $scad 2>&1 | Out-Null
& $o -o "$prev\back_outside.png" -D "part=\`"back\`"" --render --imgsize=900,1200 --camera=42,70,0,180,0,180,320 --colorscheme=Tomorrow $scad 2>&1 | Out-Null
# Farbvorschau im GBX-Design (Vorschau-Modus, damit die Farben sichtbar bleiben)
& $o -o "$prev\design_front.png" -D "part=\`"showcase\`"" --imgsize=900,1200 --camera=42,70,0,180,0,180,320 --colorscheme=Tomorrow $scad 2>&1 | Out-Null
& $o -o "$prev\design_back.png" -D "part=\`"showcase_back\`"" --imgsize=900,1200 --camera=42,70,28,0,0,0,320 --colorscheme=Tomorrow $scad 2>&1 | Out-Null
# 4) Bestellpaket (bestellung\3_3d_druck) aktuell halten
$order = Resolve-Path "..\..\bestellung\3_3d_druck"
Copy-Item "$stl\*.stl", "$prev\design_front.png", "$prev\design_back.png" $order -Force
Write-Host "fertig."
