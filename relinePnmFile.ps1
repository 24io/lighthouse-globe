#Requires -Version 7.0
Set-StrictMode -Version Latest

$filenamesPrefixes = @(
        "debug_image_equirectangular"
    )

foreach ($filenamePrefix in $filenamesPrefixes) {
    $inFile = "./" + $filenamePrefix + "_gimp_output.pnm"
    $outFile = "./" + $filenamePrefix + "_relined.pnm"
    
    Write-Host ("Loading file '" + $inFile + "'")
    $content = Get-Content -Path $inFile
    
    $newContentLength = (($content.Length - 3) / 3) + 3
    $newContent = [string[]]::new($newContentLength)
    
    foreach ($i in @(0, 1, 2)) {
        $newContent[$i] = $content[$i]
    }
    
    Write-Host ("Processing content of '" + $inFile + "'")
    $innerCounter = 0
    $outerCounter = 3
    $newLine = @(0, 0, 0)
    foreach ($line in $content[3..($content.Length - 1)]) {
        $newLine[$innerCounter] = $line
            $innerCounter += 1
        if ($innerCounter -ge 3) {
            $innerCounter = 0
            $newContent[$outerCounter] = $newLine
            $outerCounter += 1
        }
    }
    
    Write-Host ("Writing result to '" + $outFile + "'")
    Out-File -FilePath $outFile -InputObject $newContent
}

Write-Host ("All done!")

exit 0
