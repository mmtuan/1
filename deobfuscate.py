name: Deep Deobfuscate Malware

on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Cho phép chạy thủ công

jobs:
  deobfuscate:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install pylzma base91 pybase64 pycrypto
    
    - name: Run full deobfuscation
      run: python deobfuscate.py
      continue-on-error: false
    
    - name: Upload all results
      uses: actions/upload-artifact@v4
      with:
        name: deobfuscated-payloads
        path: |
          payload_*.txt
          payload_*.py
          payload_*.bin
          deobfuscation_report.txt
          *.log
        retention-days: 7
    
    - name: Upload to VirusTotal (optional)
      if: success()
      uses: actions/upload-artifact@v4
      with:
        name: for-virustotal
        path: for_vt.txt
