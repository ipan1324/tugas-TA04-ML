$docxPath = (Resolve-Path "reports/Laporan_Tugas_TA04_LSTM_Time_Series.docx").Path
$pdfPath = [System.IO.Path]::ChangeExtension($docxPath, ".pdf")

Write-Host "Converting $docxPath to $pdfPath..."

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    # wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close()
    Write-Host "Conversion successful: $pdfPath"
} catch {
    Write-Host "Error during conversion: $($_.Exception.Message)"
} finally {
    $word.Quit()
}
