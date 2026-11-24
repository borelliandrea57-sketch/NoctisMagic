# Creates a personal resource pack; never uploads your audio.
param([string]$Audio,[string]$Resourcepacks)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
if(-not $Audio){
  $dlg=New-Object System.Windows.Forms.OpenFileDialog
  $dlg.Title='Scegli la musica One Winged Angel'
  $dlg.Filter='Audio (*.mp3;*.ogg;*.wav)|*.mp3;*.ogg;*.wav'
  if($dlg.ShowDialog() -ne 'OK'){return}; $Audio=$dlg.FileName
}
if(-not $Resourcepacks){
  $dlg=New-Object System.Windows.Forms.FolderBrowserDialog
  $dlg.Description='Seleziona la cartella resourcepacks del tuo profilo CurseForge'
  if($dlg.ShowDialog() -ne 'OK'){return}; $Resourcepacks=$dlg.SelectedPath
}
if(-not (Test-Path -LiteralPath $Audio)){throw 'File audio non trovato'}
$temp=Join-Path ([IO.Path]::GetTempPath()) ('NoctisMusic-'+[Guid]::NewGuid().ToString())
try{
  $sounds=Join-Path $temp 'assets\noctismagic\sounds'
  New-Item -ItemType Directory -Path $sounds -Force | Out-Null
  $dest=Join-Path $sounds 'fallen_angel_theme.ogg'
  if([IO.Path]::GetExtension($Audio) -ieq '.ogg'){Copy-Item -LiteralPath $Audio -Destination $dest}
  else{
    $ff=Get-Command ffmpeg -ErrorAction SilentlyContinue
    if(-not $ff){throw 'FFmpeg non trovato. Converti il brano in OGG Vorbis con VLC o Audacity, oppure installa FFmpeg e riprova.'}
    & $ff.Source -hide_banner -loglevel error -y -i $Audio -vn -c:a libvorbis -q:a 5 $dest
    if($LASTEXITCODE -ne 0){throw 'Conversione audio fallita'}
  }
  [IO.File]::WriteAllText((Join-Path $temp 'pack.mcmeta'),'{"pack":{"pack_format":15,"description":"Noctis Magic - musica personale del boss"}}')
  New-Item -ItemType Directory -Path $Resourcepacks -Force | Out-Null
  $pack=Join-Path $Resourcepacks 'Noctis-Personal-Boss-Music.zip'
  Compress-Archive -Path (Join-Path $temp '*') -DestinationPath $pack -Force
  Write-Host "Creato: $pack"
  Write-Host 'Attiva il pacchetto in Minecraft, Opzioni > Pacchetti di risorse.'
}finally{if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Recurse -Force}}
