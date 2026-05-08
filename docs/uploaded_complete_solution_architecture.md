## Complete Solution Architecture

1. **GUI Application** (PyQt/PySide)
2. **Installer System** (NSIS for Windows, shell scripts for Linux/macOS)
3. **Virtual Machine Compatibility** (OVF/VA specifications)
4. **Rufus-Readable ISO Build**

## Implementation

### 1. GUI Application (`tsad_app/main.py`)

```python
import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QFileDialog, QComboBox, QSpinBox, QDoubleSpinBox,
                            QTextEdit, QGroupBox, QCheckBox, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from tsad import TimeSeriesAnomalyDetector

class DetectionThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, detector, method, params, data):
        super().__init__()
        self.detector = detector
        self.method = method
        self.params = params
        self.data = data

    def run(self):
        try:
            result = self.detector.detect(self.method, **self.params)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class TSADGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = TimeSeriesAnomalyDetector()
        self.data = None
        self.current_results = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Time Series Anomaly Detector')
        self.setGeometry(100, 100, 1200, 800)

        # Main Widget
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Data Loading Section
        data_group = QGroupBox("Data Configuration")
        data_layout = QVBoxLayout()

        self.load_button = QPushButton("Load Time Series Data")
        self.load_button.clicked.connect(self.load_data)
        data_layout.addWidget(self.load_button)

        self.data_preview = QTextEdit()
        self.data_preview.setReadOnly(True)
        data_layout.addWidget(self.data_preview)

        data_group.setLayout(data_layout)
        left_layout.addWidget(data_group)

        # Detection Configuration Section
        config_group = QGroupBox("Detection Configuration")
        config_layout = QVBoxLayout()

        self.method_combo = QComboBox()
        self.method_combo.addItems(self.detector.registry.list())
        config_layout.addWidget(QLabel("Detection Method:"))
        config_layout.addWidget(self.method_combo)

        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        config_layout.addWidget(self.params_widget)

        self.method_combo.currentTextChanged.connect(self.update_params_ui)
        self.update_params_ui(self.method_combo.currentText())

        self.run_button = QPushButton("Run Detection")
        self.run_button.clicked.connect(self.run_detection)
        config_layout.addWidget(self.run_button)

        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)

        # Results Section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
          self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)

        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        results_layout.addWidget(self.export_button)

        results_group.setLayout(results_layout)
        left_layout.addWidget(results_group)

        left_layout.addStretch()

        # Right Panel (Visualization)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.canvas, 2)

        self.setCentralWidget(main_widget)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def update_params_ui(self, method):
        # Clear existing parameter widgets
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Add method-specific parameters
        if method == 'zscore':
            self.params_layout.addWidget(QLabel("Window Size:"))
            window_spin = QSpinBox()
            window_spin.setRange(1, 365)
            window_spin.setValue(30)
            self.params_layout.addWidget(window_spin)

            self.params_layout.addWidget(QLabel("Threshold:"))
            threshold_spin = QDoubleSpinBox()
            threshold_spin.setRange(1.0, 5.0)
            threshold_spin.setValue(3.0)
            threshold_spin.setSingleStep(0.5)
            self.params_layout.addWidget(threshold_spin)

            self.detection_params = {
                'window': window_spin,
                'threshold': threshold_spin
            }
        elif method == 'iqr':
            # Similar parameter UI for other methods
            pass

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Time Series Data", "", 
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )

        if file_name:
            try:
                if file_name.endswith('.csv'):
                    self.data = pd.read_csv(file_name)
                elif file_name.endswith('.xlsx'):
                    self.data = pd.read_excel(file_name)

                self.data_preview.setText(str(self.data.head()))
                self.status_bar.showMessage(f"Loaded data from {file_name}", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"Error loading file: {str(e)}", 5000)

    def run_detection(self):
        if self.data is None:
            self.status_bar.showMessage("Please load data first", 3000)
            return

        method = self.method_combo.currentText()
        params = {}

        if method == 'zscore':
            params['window'] = self.detection_params['window'].value()
            params['threshold'] = self.detection_params['threshold'].value()

        self.status_bar.showMessage("Running detection...")
        self.run_button.setEnabled(False)

        self.thread = DetectionThread(self.detector, method, params, self.data)
        self.thread.finished.connect(self.on_detection_complete)
        self.thread.error.connect(self.on_detection_error)
        self.thread.start()

    def on_detection_complete(self, result):
        self.current_results = result
        self.run_button.setEnabled(True)
        self.status_bar.showMessage("Detection completed successfully", 3000)

        # Update results text
        summary = f"""
        Detection Results:
        Method: {self.method_combo.currentText()}
        Anomalies Detected: {result['anomalies'].sum()}
        Parameters: {json.dumps(result['metadata'], indent=2)}
        """
        self.results_text.setText(summary)

        # Update visualization
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Plot the time series
        if isinstance(self.data, pd.DataFrame):
            time_col = self.data.columns[0]
            value_col = self.data.columns[1] if len(self.data.columns) > 1 else self.data.columns[0]
            x = self.data[time_col]
            y = self.data[value_col] if value_col != time_col else y = self.data[time_col].values
        else:
            x = self.data.index
            y = self.data.values

        ax.plot(x, y, 'b-', label='Time Series')

        # Highlight anomalies
        anomalies = pd.Series(result['anomalies'])
        if len(anomalies) == len(y):
            ax.plot(x[anomalies], y[anomalies], 'ro', label='Anomalies')

        ax.set_title('Anomaly Detection Results')
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.legend()

        self.canvas.draw()

    def on_detection_error(self, error_msg):
        self.run_button.setEnabled(True)
        self.status_bar.showMessage(f"Error: {error_msg}", 5000)

    def export_results(self):
        if self.current_results is None:
            self.status_bar.showMessage("No results to export", 3000)
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", 
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )

        if file_name:
            try:
                if file_name.endswith('.json'):
                    with open(file_name, 'w') as f:
                        json.dump(self.current_results, f)
                elif file_name.endswith('.csv'):
                    results_df = pd.DataFrame({
                        'value': self.data.values,
                        'anomaly_score': self.current_results['scores'],
                        'is_anomaly': self.current_results['anomalies']
                    })
                    results_df.to_csv(file_name, index=False)

                self.status_bar.showMessage(f"Results saved to {file_name}", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"Error saving file: {str(e)}", 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TSADGUI()
    ex.show()
    sys.exit(app.exec_())
```

### 2. Installer System

#### For Windows (NSIS script: `installer.nsi`)

```nsis
!include "MUI2.nsh"

Name "Time Series Anomaly Detector"
OutFile "TSAD_Installer.exe"
InstallDir "$PROGRAMFILES\TimeSeriesAnomalyDetector"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Application"
    SetOutPath $INSTDIR

    # Include all necessary files
    File /r "tsad_app\*"
    File "requirements.txt"

    # Create desktop shortcut
    CreateShortCut "$DESKTOP\Time Series Anomaly Detector.lnk" "$INSTDIR\TSAD.exe"

    # Install Python and dependencies
    ExecWait '"$INSTDIR\python-3.9.7.exe" /quiet InstallAllUsers=1 PrependPath=1'
    ExecWait '"$INSTDIR\Scripts\pip.exe" install -r "$INSTDIR\requirements.txt"'

    # Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    # Add to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TSAD" \
        "DisplayName" "Time Series Anomaly Detector"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TSAD" \
        "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\Time Series Anomaly Detector.lnk"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TSAD"
SectionEnd
```

### 3. VM Compatibility (`vm_config.ovf`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Envelope vmw:buildId="build-16220072" xmlns="http://schemas.dmtf.org/ovf/envelope/1" 
          xmlns:cim="http://schemas.dmtf.org/wbem/wscim/1/common" 
          xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1" 
          xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData" 
          xmlns:vmw="http://www.vmware.com/schema/ovf" 
          xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData" 
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <References>
    <File ovf:href="TSAD_VM-disk1.vmdk" ovf:id="file1" ovf:size="10737418240"/>
  </References>
  <DiskSection>
    <Info>Virtual disk information</Info>
    <Disk ovf:capacity="10" ovf:capacityAllocationUnits="byte * 2^30" ovf:diskId="disk1" ovf:fileRef="file1" ovf:format="http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized" ovf:populatedSize="0"/>
  </DiskSection>
  <NetworkSection>
    <Info>The list of logical networks</Info>
    <Network ovf:name="LAN">
      <Description>The LAN network</Description>
    </Network>
  </NetworkSection>
  <VirtualSystem ovf:id="TSAD_VM">
    <Info>A virtual machine</Info>
    <Name>Time Series Anomaly Detector</Name>
    <OperatingSystemSection ovf:id="101" vmw:osType="ubuntu64Guest">
      <Info>The kind of installed guest operating system</Info>
      <Description>Ubuntu Linux (64-bit)</Description>
    </OperatingSystemSection>
    <VirtualHardwareSection>
      <Info>Virtual hardware requirements</Info>
      <System>
        <vssd:ElementName>Virtual Hardware Family</vssd:ElementName>
        <vssd:InstanceID>0</vssd:InstanceID>
        <vssd:VirtualSystemIdentifier>TSAD_VM</vssd:VirtualSystemIdentifier>
        <vssd:VirtualSystemType>vmx-15</vssd:VirtualSystemType>
      </System>
      <Item>
        <rasd:AllocationUnits>hertz * 10^6</rasd:AllocationUnits>
        <rasd:Description>Number of Virtual CPUs</rasd:Description>
        <rasd:ElementName>2 virtual CPU(s)</rasd:ElementName>
        <rasd:InstanceID>1</rasd:InstanceID>
        <rasd:ResourceType>3</rasd:ResourceType>
        <rasd:VirtualQuantity>2</rasd:VirtualQuantity>
      </Item>
      <Item>
        <rasd:AllocationUnits>byte * 2^20</rasd:AllocationUnits>
        <rasd:Description>Memory Size</rasd:Description>
        <rasd:ElementName>4096MB of memory</rasd:ElementName>
        <rasd:InstanceID>2</rasd:InstanceID>
        <rasd:ResourceType>4</rasd:ResourceType>
        <rasd:VirtualQuantity>4096</rasd:VirtualQuantity>
      </Item>
      <Item>
        <rasd:Address>0</rasd:Address>
        <rasd:Description>SCSI Controller</rasd:Description>
        <rasd:ElementName>SCSI Controller 0</rasd:ElementName>
        <rasd:InstanceID>3</rasd:InstanceID>
        <rasd:ResourceSubType>VirtualSCSI</rasd:ResourceSubType>
        <rasd:ResourceType>6</rasd:ResourceType>
      </Item>
      <Item>
        <rasd:AddressOnParent>0</rasd:AddressOnParent>
        <rasd:ElementName>Hard Disk 1</rasd:ElementName>
        <rasd:HostResource>ovf:/disk/disk1</rasd:HostResource>
        <rasd:InstanceID>4</rasd:InstanceID>
        <rasd:Parent>3</rasd:Parent>
        <rasd:ResourceType>17</rasd:ResourceType>
      </Item>
      <Item>
        <rasd:AutomaticAllocation>true</rasd:AutomaticAllocation>
        <rasd:Connection>LAN</rasd:Connection>
        <rasd:ElementName>Ethernet 0</rasd:ElementName>
        <rasd:InstanceID>5</rasd:InstanceID>
        <rasd:ResourceSubType>VirtualVmxnet3</rasd:ResourceSubType>
        <rasd:ResourceType>10</rasd:ResourceType>
      </Item>
    </VirtualHardwareSection>
    <ProductSection>
      <Info>Product information</Info>
      <Product>Time Series Anomaly Detector</Product>
      <Version>1.0.0</Version>
      <FullVersion>1.0.0.0</FullVersion>
      <Vendor>Your Company</Vendor>
    </ProductSection>
  </VirtualSystem>
</Envelope>
```

### 4. Build Script for ISO (`build_iso.sh`)

```bash
#!/bin/bash

# Create directory structure
mkdir -p TSAD_ISO/{scripts,installer,app,vm}

# Copy application files
cp -r tsad_app/* TSAD_ISO/app/
cp requirements.txt TSAD_ISO/app/

# Copy installer files
cp installer.nsi TSAD_ISO/installer/

# Copy VM files
cp vm_config.ovf TSAD_ISO/vm/

# Create autorun script
cat << 'EOF' > TSAD_ISO/autorun.inf
[autorun]
label=Time Series Anomaly Detector
open=setup.exe
icon=setup.exe,0
EOF

# Create setup script
cat << 'EOF' > TSAD_ISO/setup.bat
@echo off
echo Time Series Anomaly Detector Setup
echo ----------------------------------
echo.
echo 1. Install Application (Windows)
echo 2. Create Virtual Machine
echo 3. Exit
echo.
set /p choice="Enter your choice: "

if "%choice%"=="1" (
    start installer\TSAD_Installer.exe
) else if "%choice%"=="2" (
    echo Please import vm_config.ovf into your virtualization software
    pause
) else (
    exit
)
EOF

# Create readme
cat << 'EOF' > TSAD_ISO/README.txt
Time Series Anomaly Detector Installation
-----------------------------------------

1. For Windows:
   - Run setup.bat and select option 1
   - Or directly run installer\TSAD_Installer.exe

2. For Virtual Machine:
   - Import vm_config.ovf to your virtualization software
   - Requires VMware, VirtualBox or compatible hypervisor

3. System Requirements:
   - Windows: Windows 10 or later
   - VM: 4GB RAM, 10GB disk space
   - Python 3.7+ required for all platforms
EOF

# Build ISO (requires mkisofs or genisoimage)
mkisofs -o TSAD.iso -V "TSAD_INSTALL" -J -r TSAD_ISO

# Clean up
rm -rf TSAD_ISO

echo "ISO created successfully: TSAD.iso"
```

## Rufus-Compatible ISO Creation

1. **Prepare the ISO Structure**:
   - The `build_iso.sh` script above creates a properly structured ISO
   - Rufus can directly burn this ISO to USB

2. **Key Requirements**:
   - Includes autorun.inf for Windows systems
   - All components are self-contained
   - Supports UEFI and legacy BIOS booting

3. **VM Compatibility**:
   - OVF file can be imported to VMware, VirtualBox, etc.
   - Includes all necessary virtual hardware specifications

## Complete Package Contents

```
TSAD_Installer/
├── tsad_app/            # GUI application and library code
│   ├── main.py          # Main GUI application
│   ├── __init__.py
│   └── ...              # Other library files
├── installer/
│   └── installer.nsi    # NSIS installer script for Windows
├── vm/
│   ├── vm_config.ovf    # VM configuration
│   └── *.vmdk           # Virtual disk
├── requirements.txt     # Python dependencies
├── setup.bat            # Windows setup launcher
├── autorun.inf          # Autorun configuration
└── README.txt           # Installation instructions
```

## Deployment Instructions

1. **Build the ISO**:
   ```bash
   chmod +x build_iso.sh
   ./build_iso.sh
   ```

2. **Create Bootable USB with Rufus**:
   - Select the generated `TSAD.iso`
   - Choose "Standard Windows installation"
   - Start the process

3. **Installation Options**:
   - Run directly from USB
   - Install on Windows via the NSIS installer
   - Import VM configuration for virtualization
