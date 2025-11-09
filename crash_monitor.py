"""
Battlefield 6 Crash Monitor - GUI Version
AMD & NVIDIA GPU + Windows 11 Enhanced Edition with Real-Time Monitoring Display
"""

import psutil
import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess
import traceback
import winreg
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class BF6CrashMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BF6 Crash Monitor - AMD/NVIDIA GPU Edition")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.log_dir = Path("crash_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.bf6_process_names = ["bf6.exe", "bf2042.exe", "Battlefield2042.exe"]
        self.anticheat_process_names = ["JavelinAC.exe", "Javelin.exe", "EAAntiCheat.GameService.exe", "EAAntiCheat.GameServiceLauncher.exe"]
        self.anticheat_path = r"C:\Program Files\EA\AC"
        self.crash_count = 0
        self.bf6_running = False
        self.last_snapshot = None
        
        # Initialize psutil CPU monitoring
        try:
            psutil.cpu_percent(interval=0.1)  # Prime the pump
        except:
            pass
        
        self.setup_ui()
        self.update_system_info_once()  # Show initial values
        self.update_system_info()
        
    def setup_ui(self):
        """Setup the GUI layout"""
        # Title
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title = tk.Label(title_frame, text="🎮 Battlefield 6 Crash Monitor", 
                        font=('Arial', 18, 'bold'), bg='#1e1e1e', fg='#00ff00')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="AMD & NVIDIA GPU + Windows 11 Edition", 
                           font=('Arial', 10), bg='#1e1e1e', fg='#888888')
        subtitle.pack()
        
        # Status Frame
        status_frame = tk.LabelFrame(self.root, text="System Status", 
                                     bg='#2e2e2e', fg='white', font=('Arial', 10, 'bold'))
        status_frame.pack(fill='x', padx=10, pady=5)
        
        # Create grid for status info
        self.status_labels = {}
        status_items = [
            ('bf6_status', 'BF6 Status:', 'Waiting...'),
            ('anticheat_status', 'EA Javelin:', 'Checking...'),
            ('gpu_status', 'GPU:', 'Detecting...'),
            ('cpu_usage', 'CPU Usage:', '0%'),
            ('ram_usage', 'RAM Usage:', '0%'),
            ('crashes', 'Crashes Detected:', '0')
        ]
        
        for idx, (key, label_text, default_value) in enumerate(status_items):
            row = idx // 2
            col = (idx % 2) * 2
            
            label = tk.Label(status_frame, text=label_text, bg='#2e2e2e', 
                           fg='#aaaaaa', font=('Arial', 9))
            label.grid(row=row, column=col, sticky='w', padx=10, pady=5)
            
            value = tk.Label(status_frame, text=default_value, bg='#2e2e2e', 
                           fg='white', font=('Arial', 9, 'bold'))
            value.grid(row=row, column=col+1, sticky='w', padx=10, pady=5)
            
            self.status_labels[key] = value
        
        # Control Frame
        control_frame = tk.Frame(self.root, bg='#1e1e1e')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button = tk.Button(control_frame, text="▶ Start Monitoring", 
                                      command=self.start_monitoring,
                                      bg='#00aa00', fg='white', font=('Arial', 10, 'bold'),
                                      width=20, height=2)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(control_frame, text="⏸ Stop Monitoring", 
                                     command=self.stop_monitoring,
                                     bg='#aa0000', fg='white', font=('Arial', 10, 'bold'),
                                     width=20, height=2, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.clear_button = tk.Button(control_frame, text="🗑 Clear Log", 
                                      command=self.clear_log,
                                      bg='#555555', fg='white', font=('Arial', 10),
                                      width=15, height=2)
        self.clear_button.pack(side='left', padx=5)
        
        # Log Frame
        log_frame = tk.LabelFrame(self.root, text="Activity Log", 
                                 bg='#2e2e2e', fg='white', font=('Arial', 10, 'bold'))
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                   bg='#1e1e1e', fg='#00ff00',
                                                   font=('Consolas', 9),
                                                   insertbackground='white')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure tags for colored text
        self.log_text.tag_config('INFO', foreground='#00ff00')
        self.log_text.tag_config('WARNING', foreground='#ffaa00')
        self.log_text.tag_config('CRITICAL', foreground='#ff0000')
        self.log_text.tag_config('ERROR', foreground='#ff0000')
        
    def log(self, message, level="INFO"):
        """Log a message to the GUI and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}\n"
        
        # Write to GUI
        self.log_text.insert(tk.END, log_msg, level)
        self.log_text.see(tk.END)
        
        # Write to file
        log_file = self.log_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg)
    
    def update_status(self, key, value, color='white'):
        """Update a status label"""
        if key in self.status_labels:
            self.status_labels[key].config(text=value, fg=color)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared", "INFO")
    
    def update_system_info_once(self):
        """Update system info once (before monitoring starts)"""
        try:
            # Get basic system info
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.5)
            
            self.update_status('cpu_usage', f"{cpu:.1f}%")
            self.update_status('ram_usage', f"{mem.percent:.1f}% ({mem.used/1024**3:.1f}GB)")
            
            # Get GPU
            gpu = self.get_gpu_info()
            if gpu:
                gpu_name = gpu.get('Name', 'Unknown')[:30]
                self.update_status('gpu_status', gpu_name)
            
            # Check EA Javelin
            javelin = self.check_ea_javelin_installation()
            if javelin and javelin.get('installed'):
                self.update_status('anticheat_status', '✓ Installed', '#00ff00')
            else:
                self.update_status('anticheat_status', '✗ Not Found', '#ff0000')
                
        except Exception as e:
            self.log(f"Error in initial update: {e}", "WARNING")
    
    def check_ea_javelin_installation(self):
        """Check if EA Javelin anticheat is properly installed"""
        try:
            javelin_info = {
                'installed': False,
                'path': None,
                'version': None,
                'service_exists': False
            }
            
            if os.path.exists(self.anticheat_path):
                javelin_info['installed'] = True
                javelin_info['path'] = self.anticheat_path
                
                game_service = os.path.join(self.anticheat_path, "EAAntiCheat.GameService.exe")
                if os.path.exists(game_service):
                    javelin_info['service_exists'] = True
                    
                    try:
                        result = subprocess.run(
                            ['powershell', '-Command',
                             f'(Get-Item "{game_service}").VersionInfo.FileVersion'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.stdout.strip():
                            javelin_info['version'] = result.stdout.strip()
                    except:
                        pass
            
            return javelin_info
        except Exception as e:
            return None

    def check_hardware_accelerated_gpu_scheduling(self):
        """Check if Hardware-Accelerated GPU Scheduling is enabled"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers")
            hags, _ = winreg.QueryValueEx(key, "HwSchMode")
            winreg.CloseKey(key)
            return hags == 2
        except:
            return None

    def get_gpu_info(self):
        """Get GPU information (AMD or NVIDIA)"""
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get',
                 'Name,DriverVersion', '/format:list'],
                capture_output=True,
                text=True,
                timeout=5
            )

            gpu_data = {}
            current_gpu = {}

            for line in result.stdout.split('\n'):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    current_gpu[key.strip()] = value.strip()
                elif current_gpu:
                    # Check for AMD or NVIDIA GPU
                    gpu_name = current_gpu.get('Name', '')
                    if any(brand in gpu_name for brand in ['AMD', 'Radeon', 'NVIDIA', 'GeForce', 'RTX', 'GTX']):
                        gpu_data = current_gpu
                        # Identify GPU vendor
                        if 'NVIDIA' in gpu_name or 'GeForce' in gpu_name or 'RTX' in gpu_name or 'GTX' in gpu_name:
                            gpu_data['Vendor'] = 'NVIDIA'
                        elif 'AMD' in gpu_name or 'Radeon' in gpu_name:
                            gpu_data['Vendor'] = 'AMD'
                    current_gpu = {}

            return gpu_data if gpu_data else None
        except Exception as e:
            return None

    def get_process_info(self, process_name):
        """Get detailed info about a process"""
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    return {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                        'running_time': time.time() - proc.info['create_time']
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def get_system_snapshot(self):
        """Get current system state snapshot"""
        # Get CPU usage (non-blocking, uses previous interval)
        cpu_percent = psutil.cpu_percent(interval=None)
        # If first call returns 0, do a blocking call
        if cpu_percent == 0.0:
            cpu_percent = psutil.cpu_percent(interval=1)
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory': {
                'total_gb': psutil.virtual_memory().total / 1024**3,
                'available_gb': psutil.virtual_memory().available / 1024**3,
                'used_gb': psutil.virtual_memory().used / 1024**3,
                'percent': psutil.virtual_memory().percent
            },
            'gpu_info': self.get_gpu_info(),
            'bf6_process': None,
            'anticheat_process': None,
            'ea_javelin': self.check_ea_javelin_installation(),
            'hags_enabled': self.check_hardware_accelerated_gpu_scheduling()
        }

        # Check for BF6 process
        for proc_name in self.bf6_process_names:
            proc_info = self.get_process_info(proc_name)
            if proc_info:
                snapshot['bf6_process'] = proc_info
                break

        # Check for anticheat process
        for proc_name in self.anticheat_process_names:
            proc_info = self.get_process_info(proc_name)
            if proc_info:
                snapshot['anticheat_process'] = proc_info
                break

        return snapshot

    def check_windows_event_logs(self):
        """Check Windows Event Logs for recent crashes"""
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-EventLog -LogName Application -EntryType Error -Newest 30 | ' +
                 'Where-Object {$_.TimeGenerated -gt (Get-Date).AddMinutes(-10)} | ' +
                 'Select-Object TimeGenerated, Source, Message, EventID | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.stdout.strip():
                events = json.loads(result.stdout)
                if isinstance(events, dict):
                    events = [events]
                return events
            return []
        except Exception as e:
            return []

    def analyze_crash(self, pre_crash, event_logs):
        """Quick crash analysis"""
        issues = []
        recommendations = []
        
        # Get GPU vendor
        gpu_info = pre_crash.get('gpu_info', {})
        gpu_vendor = gpu_info.get('Vendor', 'Unknown')
        
        # Check HAGS
        if pre_crash.get('hags_enabled'):
            issues.append("⚠️ HAGS is ENABLED - disable it!")
            if gpu_vendor == 'AMD':
                recommendations.append("AMD + HAGS = frequent crashes")
        
        # Check anticheat
        if not pre_crash.get('anticheat_process'):
            issues.append("⚠️ EA Javelin was NOT running")
            recommendations.append("Game needs EA Javelin to run")
        
        # Check memory
        if pre_crash['memory']['percent'] > 90:
            issues.append(f"⚠️ High RAM usage: {pre_crash['memory']['percent']:.0f}%")
            recommendations.append("Close background apps or add more RAM")
        
        # Check event logs for specific errors
        for event in event_logs:
            msg = event.get('Message', '').lower()
            
            if 'tdr' in msg or 'timeout' in msg:
                issues.append("⚠️ GPU Timeout (TDR) detected")
                recommendations.append("Increase TDR timeout in registry")
                
            if gpu_vendor == 'AMD':
                if 'amduw' in msg or 'atikmdag' in msg or 'amdvlk' in msg:
                    issues.append("⚠️ AMD driver crash detected")
                    recommendations.append("Clean reinstall AMD drivers with DDU")
            elif gpu_vendor == 'NVIDIA':
                if 'nvlddmkm' in msg or 'nvidia' in msg:
                    issues.append("⚠️ NVIDIA driver crash detected")
                    recommendations.append("Update/rollback NVIDIA drivers")
            
            if 'eaanticheat' in msg or 'javelin' in msg:
                issues.append("⚠️ EA Javelin error detected")
                recommendations.append("Reinstall EA Javelin anticheat")
        
        # Add vendor-specific general tips
        if gpu_vendor == 'AMD':
            recommendations.append("AMD: Disable Anti-Lag, Boost, Enhanced Sync")
        elif gpu_vendor == 'NVIDIA':
            recommendations.append("NVIDIA: Check for shader cache issues")
        
        result = {
            'issues': issues if issues else ["ℹ️ No obvious issues detected"],
            'recommendations': recommendations if recommendations else ["Check full crash report for details"]
        }
        
        return result

    def save_crash_report(self, pre_crash_data):
        """Save crash report"""
        self.crash_count += 1
        crash_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_file = self.log_dir / f"crash_report_{crash_time}.json"

        event_logs = self.check_windows_event_logs()

        report = {
            'crash_number': self.crash_count,
            'crash_time': crash_time,
            'pre_crash_snapshot': pre_crash_data,
            'windows_event_logs': event_logs,
            'quick_analysis': self.analyze_crash(pre_crash_data, event_logs)
        }

        with open(crash_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        return crash_file, report

    def update_system_info(self):
        """Update system info display"""
        if not self.monitoring:
            return
            
        try:
            snapshot = self.get_system_snapshot()
            
            # Debug: Check if we got valid data
            if snapshot['cpu_percent'] == 0.0 and snapshot['memory']['percent'] == 0.0:
                self.log("⚠️ Debug: Getting zero values from psutil", "WARNING")
            
            # Update CPU/RAM
            cpu_val = snapshot['cpu_percent']
            ram_pct = snapshot['memory']['percent']
            ram_used = snapshot['memory']['used_gb']
            
            self.update_status('cpu_usage', f"{cpu_val:.1f}%", 
                             '#ff0000' if cpu_val > 90 else '#ffaa00' if cpu_val > 70 else 'white')
            self.update_status('ram_usage', 
                             f"{ram_pct:.1f}% ({ram_used:.1f}GB)",
                             '#ff0000' if ram_pct > 90 else '#ffaa00' if ram_pct > 70 else 'white')
            
            # Update GPU
            gpu = snapshot.get('gpu_info')
            if gpu:
                gpu_name = gpu.get('Name', 'Unknown')[:30]
                self.update_status('gpu_status', gpu_name)
            
            # Update crashes
            self.update_status('crashes', str(self.crash_count), 
                             '#ff0000' if self.crash_count > 0 else 'white')
            
            # Check BF6 status
            if snapshot['bf6_process']:
                if not self.bf6_running:
                    self.bf6_running = True
                    self.log("═" * 50, "INFO")
                    self.log("🎮 BF6 DETECTED - Monitoring active!", "INFO")
                    self.log("═" * 50, "INFO")
                    
                    proc = snapshot['bf6_process']
                    self.log(f"Process: {proc['name']} (PID: {proc['pid']})", "INFO")
                    self.log(f"Memory: {proc['memory_mb']:.0f}MB", "INFO")
                    
                    if snapshot['anticheat_process']:
                        ac = snapshot['anticheat_process']
                        self.log(f"✓ EA Javelin: {ac['name']} running", "INFO")
                    else:
                        self.log("⚠️ WARNING: EA Javelin NOT running!", "WARNING")
                    
                    if snapshot.get('hags_enabled'):
                        self.log("⚠️ WARNING: HAGS is ENABLED - may cause crashes!", "WARNING")
                
                self.update_status('bf6_status', '🟢 Running', '#00ff00')
                
                # Update anticheat status
                if snapshot['anticheat_process']:
                    self.update_status('anticheat_status', '✓ Running', '#00ff00')
                else:
                    self.update_status('anticheat_status', '✗ Not Running', '#ff0000')
                
                self.last_snapshot = snapshot
                
            else:
                if self.bf6_running:
                    # BF6 just crashed
                    self.bf6_running = False
                    self.log("═" * 50, "CRITICAL")
                    self.log("💥 BF6 CRASHED!", "CRITICAL")
                    self.log("═" * 50, "CRITICAL")
                    
                    if self.last_snapshot:
                        crash_file, report = self.save_crash_report(self.last_snapshot)
                        
                        analysis = report['quick_analysis']
                        
                        self.log(f"\n🔍 Issues Found:", "WARNING")
                        for issue in analysis['issues']:
                            self.log(f"  {issue}", "WARNING")
                        
                        self.log(f"\n💡 Recommendations:", "INFO")
                        for rec in analysis['recommendations']:
                            self.log(f"  • {rec}", "INFO")
                        
                        self.log(f"\n💾 Full report saved: {crash_file.name}", "INFO")
                        self.log("═" * 50, "INFO")
                    
                    self.last_snapshot = None
                
                self.update_status('bf6_status', '⚫ Not Running', '#888888')
                self.update_status('anticheat_status', '⚫ Idle', '#888888')
        
        except Exception as e:
            self.log(f"Error updating system info: {e}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
        
        # Schedule next update
        if self.monitoring:
            self.root.after(2000, self.update_system_info)
    
    def monitor_loop(self):
        """Background monitoring thread"""
        self.log("🚀 Monitor started - waiting for BF6...", "INFO")
        
        # Initialize CPU monitoring (first call to start tracking)
        psutil.cpu_percent(interval=1)
        
        # Initial system check
        snapshot = self.get_system_snapshot()
        
        gpu = snapshot.get('gpu_info')
        if gpu:
            self.log(f"GPU: {gpu.get('Name', 'Unknown')}", "INFO")
            self.log(f"Driver: {gpu.get('DriverVersion', 'Unknown')}", "INFO")
        
        javelin = snapshot.get('ea_javelin', {})
        if javelin.get('installed'):
            self.log(f"✓ EA Javelin installed: {javelin.get('path')}", "INFO")
            if javelin.get('version'):
                self.log(f"  Version: {javelin['version']}", "INFO")
        else:
            self.log("⚠️ EA Javelin NOT installed!", "WARNING")
        
        if snapshot.get('hags_enabled'):
            self.log("⚠️ WARNING: HAGS is enabled - may cause crashes!", "WARNING")
        
        # Log system resources
        self.log(f"System: CPU {snapshot['cpu_percent']:.1f}% | RAM {snapshot['memory']['percent']:.1f}% ({snapshot['memory']['used_gb']:.1f}GB used)", "INFO")
        
        self.log("─" * 50, "INFO")
        
        # Update GUI immediately with initial values
        self.root.after(10, lambda: self.update_status('cpu_usage', f"{snapshot['cpu_percent']:.1f}%", 'white'))
        self.root.after(10, lambda: self.update_status('ram_usage', 
                                                        f"{snapshot['memory']['percent']:.1f}% ({snapshot['memory']['used_gb']:.1f}GB)", 
                                                        'white'))
        
        # Start GUI updates
        self.root.after(100, self.update_system_info)
    
    def start_monitoring(self):
        """Start the monitoring process"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.log("⏸ Monitoring stopped", "WARNING")
        self.update_status('bf6_status', 'Monitoring Stopped', '#ffaa00')

def main():
    # Check if running as admin
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("⚠️  WARNING: Not running as Administrator - some features may be limited")
            messagebox.showwarning("Not Administrator", 
                                  "Not running as Administrator.\nSome features may be limited.\n\nRight-click and 'Run as Administrator' for best results.")
    except:
        pass
    
    root = tk.Tk()
    app = BF6CrashMonitorGUI(root)
    
    # Handle window close
    def on_closing():
        if app.monitoring:
            if messagebox.askokcancel("Quit", "Monitoring is active. Do you want to quit?"):
                app.monitoring = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()