#Requires -Version 5.1
<#
.SYNOPSIS
    Lance une VM VirtualBox pour voir Barbakaï OS sans se battre avec les réglages.

.EXAMPLE
    .\preview-barbakai.ps1
#>
$ErrorActionPreference = "Stop"

$VmName = "Barbakai"
$VBox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "         BARBAKAÏ OS  ·  aperçu VM" -ForegroundColor Cyan
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Utilisateur : barbakai"
Write-Host "  Mot de passe : Thegamecontrol!"
Write-Host ""

if (-not (Test-Path $VBox)) {
    Write-Host "VirtualBox n'est pas installé (VBoxManage introuvable)." -ForegroundColor Red
    Write-Host "Installe VirtualBox : https://www.virtualbox.org/wiki/Downloads"
    exit 1
}

$isoCandidates = @(
    (Join-Path $RepoRoot "output\bootiso\install.iso"),
    (Join-Path $RepoRoot "ISO\bootiso\install.iso"),
    (Join-Path $RepoRoot "NextOS-ISO\bootiso\install.iso"),
    (Join-Path $RepoRoot "artifact-anaconda-iso\bootiso\install.iso")
)
$Iso = $isoCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $Iso) {
    Write-Host "Aucune ISO trouvée." -ForegroundColor Yellow
    Write-Host "1. Pousse ce dépôt sur GitHub"
    Write-Host "2. Onglet Actions → 'Build container image' puis 'Build disk images'"
    Write-Host "3. Télécharge l'artifact anaconda-iso, dézippe-le ici"
    Write-Host "4. Relance .\preview-barbakai.ps1"
    exit 1
}

Write-Host "  ISO : $Iso"
Write-Host ""

function Invoke-VBox {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & $VBox @Args
    if ($LASTEXITCODE -ne 0) {
        throw "VBoxManage a échoué : $Args"
    }
}

$existing = & $VBox list vms
$vmExists = $existing -match "`"$VmName`""

$VmDir = Join-Path $RepoRoot "vm-barbakai"
New-Item -ItemType Directory -Force -Path $VmDir | Out-Null
$Disk = Join-Path $VmDir "barbakai.vdi"

if (-not $vmExists) {
    Write-Host "Création de la VM Barbakai..." -ForegroundColor Cyan
    Invoke-VBox createvm --name $VmName --ostype Fedora_64 --register
    Invoke-VBox modifyvm $VmName `
        --memory 8192 `
        --cpus 4 `
        --firmware efi `
        --vram 128 `
        --graphicscontroller vmsvga `
        --nic1 nat `
        --ioapic on `
        --rtcuseutc on `
        --mouse usbtablet `
        --audioout on `
        --clipboard-mode bidirectional
    Invoke-VBox storagectl $VmName --name "SATA" --add sata --controller IntelAhci --portcount 2 --bootable on
    if (-not (Test-Path $Disk)) {
        Invoke-VBox createmedium disk --filename $Disk --size 65536 --format VDI
    }
    Invoke-VBox storageattach $VmName --storagectl "SATA" --port 0 --device 0 --type hdd --medium $Disk
    Invoke-VBox storageattach $VmName --storagectl "SATA" --port 1 --device 0 --type dvddrive --medium $Iso
} else {
    Write-Host "VM déjà créée — mise à jour de l'ISO..." -ForegroundColor Cyan
    & $VBox storageattach $VmName --storagectl "SATA" --port 1 --device 0 --type dvddrive --medium $Iso 2>$null
}

Write-Host "Démarrage..." -ForegroundColor Green
Invoke-VBox startvm $VmName

Write-Host ""
Write-Host "Dans l'installateur : juste le disque. Le compte barbakai est déjà là."
Write-Host "Ensuite connecte-toi avec barbakai / Thegamecontrol!"
Write-Host ""
