# Öffnet den Word-Bericht mit Microsoft Word, aktualisiert Inhaltsverzeichnis und Felder,
# speichert ihn im Word-2013+-Format und exportiert ein Kontroll-PDF daneben.
# Aufruf aus der Repo-Wurzel:  powershell -ExecutionPolicy Bypass -File tools/finalize_report.ps1
#
# Erfahrungen (11.11.2026):
# - Word hängt unsichtbar, wenn es die Datei direkt in Dokumente öffnet -> Arbeitskopie in %TEMP%.
# - Save() hängt im Kompatibilitätsmodus -> SaveAs2. Den Modus selbst setzt make_report.py (15);
#   SaveAs2(CompatibilityMode=15) stellt ihn NICHT um.
# - foreach über $d.TablesOfContents schlägt fehl -> Item(i).
# - Ein Watchdog beendet die eigene Word-Instanz nach 120 s, damit nichts hängen bleibt.
$ErrorActionPreference = "Stop"
$docx = (Resolve-Path "$PSScriptRoot\..\documentation\final-report\GameBoy_Project_Engineering_Documentation.docx").Path
$pdf = [IO.Path]::ChangeExtension($docx, ".pdf")
$tmp = Join-Path $env:TEMP ("gbreport_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory $tmp | Out-Null
$tdocx = Join-Path $tmp "report.docx"
$tpdf = Join-Path $tmp "report.pdf"
Copy-Item $docx $tdocx

$before = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object Id)
$job = Start-Job -ArgumentList $tdocx, $tpdf -ScriptBlock {
    param($i, $o)
    $w = New-Object -ComObject Word.Application
    $w.Visible = $false
    $w.DisplayAlerts = 0
    try {
        $d = $w.Documents.Open($i, $false, $false)
        for ($k = 1; $k -le $d.TablesOfContents.Count; $k++) { $d.TablesOfContents.Item($k).Update() }
        $d.Fields.Update() | Out-Null
        $d.Repaginate()
        for ($k = 1; $k -le $d.TablesOfContents.Count; $k++) { $d.TablesOfContents.Item($k).UpdatePageNumbers() }
        $pages = $d.ComputeStatistics(2)
        $d.SaveAs2($i, 16, $false, "", $false, "", $false, $false, $false, $false, $false, 0, $false, $false, 15)
        $d.ExportAsFixedFormat($o, 17)
        $d.Close(0)
        "Seiten: $pages"
    } finally { $w.Quit() }
}
if (Wait-Job $job -Timeout 120) {
    Receive-Job $job
    Copy-Item $tdocx $docx -Force
    Copy-Item $tpdf $pdf -Force
    "OK: $docx"
    "    $pdf"
} else {
    Stop-Job $job
    # nur Word-Prozesse beenden, die während dieses Laufs entstanden sind
    Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object { $before -notcontains $_.Id } | Stop-Process -Force
    Write-Error "Word hat nicht innerhalb von 120 s geantwortet."
}
Remove-Job $job -Force
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
