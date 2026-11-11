# GameboyPi: Schaltplan -> Platine -> Autorouting -> Pruefungen -> Fertigungs- und Montagedaten
$ErrorActionPreference = "Continue"  # stderr-Warnungen von kicad-cli nicht als Abbruch werten; Run() prueft Exit-Codes
Set-Location $PSScriptRoot
$kicad = "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin"
$py = "$kicad\python.exe"
$cli = "$kicad\kicad-cli.exe"
$el = Resolve-Path ".."

function Run($exe, [string[]]$a) { & $exe @a; if ($LASTEXITCODE) { throw "$exe $a fehlgeschlagen" } }

Run $py @("make_sch.py")
Run $py @("check_netlist.py")
Run $py @("make_pcb.py")
Run $py @("route.py", "60")

# Pruefungen (Berichte in build\, Zusammenfassung in documentation\testing.md)
& $cli sch erc --severity-all -o build\erc.rpt GameboyPi.kicad_sch
& $cli pcb drc --schematic-parity --severity-all -o build\drc.rpt GameboyPi.kicad_pcb
foreach ($r in "build\erc.rpt", "build\drc.rpt") {
    Select-String -Path $r -Pattern "ERC messages|Found \d+ (DRC violations|unconnected)" | ForEach-Object { Write-Host "$r : $($_.Line.Trim(' *'))" }
}
if (Select-String -Path build\drc.rpt -Pattern "; error" -Quiet) { Write-Warning "DRC meldet Fehler (nicht nur Warnungen) - build\drc.rpt lesen" }

# Fertigungsdaten: Gerber + Bohrdaten (JLCPCB/PCBWay/Aisler)
$g = "$el\gerber"
Get-ChildItem $g -File -ErrorAction SilentlyContinue | Remove-Item
Run $cli @("pcb", "export", "gerbers", "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts", "-o", "$g\", "GameboyPi.kicad_pcb")
Run $cli @("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map", "--map-format", "pdf", "-o", "$g\", "GameboyPi.kicad_pcb")
Compress-Archive -Path "$g\*.g*", "$g\*.drl" -DestinationPath "$g\GameboyPi_Gerber.zip" -Force
Copy-Item "$g\GameboyPi_Gerber.zip" "$el\..\bestellung\1_platine_JLCPCB\" -Force  # Bestellpaket aktuell halten

# Montage: Pick-and-Place (beide Seiten), BOM aus dem Schaltplan, Bestueckungsplaene
$a = "$el\assembly"
Run $cli @("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "-o", "$a\GameboyPi_pick_and_place.csv", "GameboyPi.kicad_pcb")
Run $cli @("sch", "export", "bom", "--fields", "Reference,Value,Footprint,`${QUANTITY}", "--group-by", "Value,Footprint", "-o", "$a\GameboyPi_bom_kicad.csv", "GameboyPi.kicad_sch")
Run $cli @("pcb", "export", "pdf", "--layers", "F.Fab,F.SilkS,Edge.Cuts", "--mode-single", "-o", "$a\Bestueckung_vorne.pdf", "GameboyPi.kicad_pcb")
Run $cli @("pcb", "export", "pdf", "--layers", "B.Fab,B.SilkS,Edge.Cuts", "--mirror", "--mode-single", "-o", "$a\Bestueckung_hinten.pdf", "GameboyPi.kicad_pcb")

# Doku: Schaltplan-PDF, 3D-Ansichten, STEP
Run $cli @("sch", "export", "pdf", "-o", "$el\schematics\GameboyPi_Schaltplan.pdf", "GameboyPi.kicad_sch")
Run $cli @("pcb", "render", "--side", "top", "--width", "1200", "--height", "1600", "--quality", "high", "-o", "$a\Platine_vorne.png", "GameboyPi.kicad_pcb")
Run $cli @("pcb", "render", "--side", "bottom", "--width", "1200", "--height", "1600", "--quality", "high", "-o", "$a\Platine_hinten.png", "GameboyPi.kicad_pcb")
Run $cli @("pcb", "export", "step", "--subst-models", "-f", "-o", "$a\GameboyPi.step", "GameboyPi.kicad_pcb")
Write-Host "fertig."
