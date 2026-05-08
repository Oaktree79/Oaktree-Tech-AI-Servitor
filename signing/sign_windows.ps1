param([Parameter(Mandatory=$true)][string]$InstallerPath,[Parameter(Mandatory=$true)][string]$CertificateThumbprint)
signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /sha1 $CertificateThumbprint $InstallerPath
signtool verify /pa $InstallerPath
