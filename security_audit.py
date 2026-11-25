"""Read-only repository audit. Heuristic indicators, not a malware certification."""
from pathlib import Path
import ast,re,zipfile,hashlib,stat
root=Path(__file__).resolve().parent
rules={
 "network":r'\b(?:java\.net|javax\.net|HttpClient|URLConnection|SocketChannel|ServerSocket|InetAddress|urllib\.request|requests\.(?:get|post)|socket\.socket)\b',
 "process":r'\b(?:Runtime\s*\.\s*getRuntime|ProcessBuilder|os\.system|os\.popen|subprocess\.(?:run|Popen|call|check_output|check_call))\b',
 "file access":r'\b(?:java\.nio\.file|java\.io\.(?:FileOutputStream|FileInputStream|RandomAccessFile)|shutil\.rmtree|Files\.(?:delete|move|write))\b',
 "crypto":r'\b(?:javax\.crypto|Cipher\.getInstance|cryptography\.fernet)\b',
 "dynamic code":r'\b(?:URLClassLoader|defineClass|System\.loadLibrary|eval\s*\(|exec\s*\(|pickle\.loads|marshal\.loads)\b',
 "credentials and persistence":r'\b(?:System\.getenv|os\.environ|winreg|schtasks|CurrentVersion\\Run|Login Data|CryptUnprotectData|discord(?:app)?\.com/api/webhooks)\b',
}
scripts=sorted(root.glob('*.py'));count=0
for p in scripts:
 if p.name==Path(__file__).name:continue
 data=p.read_text(encoding='utf-8',errors='replace')
 try:ast.parse(data)
 except SyntaxError as exc:print('PYTHON SYNTAX REVIEW',p.name,exc)
 count+=1
 for i,line in enumerate(data.splitlines(),1):
  for k,pat in rules.items():
   if re.search(pat,line,re.I):
    print('SCRIPT REVIEW',p.name,i,k,line.strip()[:220])
print('Repository Python scripts inspected:',count)
for p in root.glob('*.zip'):
 print('ARCHIVE',p.name,'SHA256',hashlib.sha256(p.read_bytes()).hexdigest())
 with zipfile.ZipFile(p) as z:
  for i in z.infolist():
   n=i.filename
   if n.startswith(('/','\\')) or '..' in Path(n.replace('\\','/')).parts or re.match(r'^[A-Za-z]:',n) or stat.S_ISLNK(i.external_attr>>16):
    raise RuntimeError('Unsafe archive member: '+n)
   if n.lower().endswith(('.exe','.dll','.so','.dylib','.bat','.cmd','.ps1','.sh','.jar')):
    print('ARCHIVE REVIEW',n)
   if n.endswith(('.java','.gradle','.properties','.sh','.bat','.ps1')):
    if i.file_size>4_000_000:print('OVERSIZE REVIEW',n);continue
    for line_no,line in enumerate(z.read(i).decode('utf-8',errors='replace').splitlines(),1):
     for k,pat in rules.items():
      if re.search(pat,line,re.I):print('BASE SOURCE REVIEW',n,line_no,k,line.strip()[:220])
print('Audit complete; third-party dependencies and runtime behavior require separate verification.')
