#!/usr/bin/env python3
"""
Lab Instruments System Monitor Dashboard
リアルタイムシステム監視、接続統計、デバイス状態の可視化
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
from collections import deque
import json

# Add parent directory to path for running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lab_instruments


class SystemMonitor:
    """System monitoring and statistics collection"""
    
    def __init__(self, history_size=100):
        self.history_size = history_size
        self.connection_history = deque(maxlen=history_size)
        self.device_status_history = deque(maxlen=history_size)
        self.system_stats_history = deque(maxlen=history_size)
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 5.0  # seconds
        
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("📊 Background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("⏹️  Background monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                timestamp = datetime.now()
                
                # Collect system statistics
                stats = self._collect_system_stats(timestamp)
                self.system_stats_history.append(stats)
                
                # Collect device status
                device_status = self._collect_device_status(timestamp)
                self.device_status_history.append(device_status)
                
                # Update connection history from lab_instruments
                conn_stats = lab_instruments.get_connection_stats()
                self.connection_history.append({
                    'timestamp': timestamp,
                    'stats': conn_stats
                })
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                time.sleep(1.0)
    
    def _collect_system_stats(self, timestamp):
        """Collect general system statistics"""
        try:
            registry_stats = lab_instruments.registry.get_discovery_stats()
            stub_stats = lab_instruments.stub_manager.get_generation_stats()
            
            return {
                'timestamp': timestamp,
                'devices_count': len(lab_instruments.list_devices()),
                'registry_successful': registry_stats.get('successful', 0),
                'registry_failed': registry_stats.get('failed', 0),
                'stub_last_generated': stub_stats.get('generated_at'),
                'stub_success': stub_stats.get('success', False)
            }
        except Exception as e:
            return {
                'timestamp': timestamp,
                'error': str(e)
            }
    
    def _collect_device_status(self, timestamp):
        """Collect device validation status"""
        device_status = {'timestamp': timestamp, 'devices': {}}
        
        try:
            devices = lab_instruments.list_devices()
            validation_results = lab_instruments.validate_all_devices()
            
            for device in devices:
                is_valid, errors = validation_results.get(device, (False, ['Unknown error']))
                device_status['devices'][device] = {
                    'valid': is_valid,
                    'error_count': len(errors),
                    'errors': errors
                }
                
        except Exception as e:
            device_status['error'] = str(e)
        
        return device_status
    
    def get_summary(self):
        """Get current system summary"""
        if not self.system_stats_history:
            return None
        
        latest_stats = self.system_stats_history[-1]
        latest_conn = self.connection_history[-1] if self.connection_history else None
        latest_devices = self.device_status_history[-1] if self.device_status_history else None
        
        summary = {
            'timestamp': latest_stats['timestamp'],
            'devices_registered': latest_stats.get('devices_count', 0),
            'connection_stats': latest_conn['stats'] if latest_conn else {},
            'device_validation': {},
            'issues': []
        }
        
        # Device validation summary
        if latest_devices and 'devices' in latest_devices:
            total_devices = len(latest_devices['devices'])
            valid_devices = sum(1 for d in latest_devices['devices'].values() if d['valid'])
            summary['device_validation'] = {
                'total': total_devices,
                'valid': valid_devices,
                'invalid': total_devices - valid_devices
            }
            
            # Collect issues
            for device, status in latest_devices['devices'].items():
                if not status['valid']:
                    summary['issues'].extend([f"{device}: {error}" for error in status['errors']])
        
        return summary


class DashboardDisplay:
    """Dashboard display and formatting"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.last_update = None
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print dashboard header"""
        now = datetime.now()
        print("╔" + "═" * 78 + "╗")
        print("║" + " LAB INSTRUMENTS SYSTEM DASHBOARD".center(78) + "║")
        print("║" + f" {now.strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "║")
        print("╚" + "═" * 78 + "╝")
    
    def print_system_overview(self, summary):
        """Print system overview section"""
        print("\n📊 SYSTEM OVERVIEW")
        print("─" * 50)
        
        if not summary:
            print("⚠️  No monitoring data available")
            return
        
        devices_count = summary.get('devices_registered', 0)
        print(f"Registered Devices: {devices_count}")
        
        # Connection statistics
        conn_stats = summary.get('connection_stats', {})
        if conn_stats:
            total = conn_stats.get('total_connections', 0)
            successful = conn_stats.get('successful_connections', 0)
            active = conn_stats.get('active_connections', 0)
            pool_size = conn_stats.get('pool_size', 0)
            
            success_rate = (successful / total * 100) if total > 0 else 0
            
            print(f"Total Connections: {total}")
            print(f"Success Rate: {success_rate:.1f}%")
            print(f"Active Connections: {active}")
            print(f"Connection Pool: {pool_size}")
        
        # Device validation
        validation = summary.get('device_validation', {})
        if validation:
            total = validation.get('total', 0)
            valid = validation.get('valid', 0)
            invalid = validation.get('invalid', 0)
            
            print(f"Device Validation: {valid}/{total} valid")
            if invalid > 0:
                print(f"⚠️  {invalid} devices have configuration issues")
    
    def print_device_status(self):
        """Print device status section"""
        print("\n🔧 DEVICE STATUS")
        print("─" * 50)
        
        devices = lab_instruments.list_devices()
        if not devices:
            print("No devices registered")
            return
        
        validation_results = lab_instruments.validate_all_devices()
        
        for device in devices:
            is_valid, errors = validation_results.get(device, (False, ['Unknown']))
            status_icon = "✅" if is_valid else "❌"
            print(f"{status_icon} {device}")
            
            if not is_valid:
                for error in errors[:2]:  # Show first 2 errors
                    print(f"    • {error}")
                if len(errors) > 2:
                    print(f"    • ... and {len(errors) - 2} more")
    
    def print_connection_history(self, limit=10):
        """Print recent connection history"""
        print(f"\n📈 RECENT CONNECTIONS (Last {limit})")
        print("─" * 50)
        
        if not self.monitor.connection_history:
            print("No connection history available")
            return
        
        # Get recent connections from all history
        all_connections = []
        for entry in self.monitor.connection_history:
            conn_stats = entry['stats']
            history = conn_stats.get('connection_history', [])
            for conn in history:
                all_connections.append(conn)
        
        # Sort by start time and take most recent
        all_connections.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        recent = all_connections[:limit]
        
        if not recent:
            print("No connection attempts recorded")
            return
        
        for conn in recent:
            device = conn.get('device', 'raw')
            success = conn.get('success', False)
            duration = conn.get('duration', 0)
            start_time = conn.get('start_time', '')
            
            status_icon = "✅" if success else "❌"
            time_str = start_time.split('T')[1][:8] if 'T' in start_time else start_time
            
            print(f"{status_icon} {time_str} {device} ({duration:.3f}s)")
            
            if not success and conn.get('error'):
                error = conn['error'][:60] + "..." if len(conn['error']) > 60 else conn['error']
                print(f"    Error: {error}")
    
    def print_issues(self, summary):
        """Print current issues"""
        issues = summary.get('issues', []) if summary else []
        
        print(f"\n⚠️  CURRENT ISSUES ({len(issues)})")
        print("─" * 50)
        
        if not issues:
            print("✅ No issues detected")
            return
        
        for issue in issues[:10]:  # Show first 10 issues
            print(f"• {issue}")
        
        if len(issues) > 10:
            print(f"• ... and {len(issues) - 10} more issues")
    
    def print_controls(self):
        """Print control instructions"""
        print("\n🎮 CONTROLS")
        print("─" * 50)
        print("r - Refresh plugins and stubs")
        print("d - Run full diagnostics")
        print("c - Clear connection pool")  
        print("s - Show detailed statistics")
        print("q - Quit")
    
    def display_dashboard(self):
        """Display complete dashboard"""
        self.clear_screen()
        self.print_header()
        
        summary = self.monitor.get_summary()
        
        self.print_system_overview(summary)
        self.print_device_status()
        self.print_connection_history()
        self.print_issues(summary)
        self.print_controls()
        
        self.last_update = datetime.now()


def run_interactive_dashboard():
    """Run interactive dashboard"""
    monitor = SystemMonitor()
    display = DashboardDisplay(monitor)
    
    try:
        monitor.start_monitoring()
        
        print("🚀 Starting Lab Instruments Dashboard...")
        print("Press any key to continue...")
        input()
        
        while True:
            display.display_dashboard()
            
            print(f"\nLast update: {display.last_update.strftime('%H:%M:%S') if display.last_update else 'Never'}")
            print("Command (or Enter to refresh): ", end='', flush=True)
            
            # Non-blocking input with timeout
            import select
            if select.select([sys.stdin], [], [], 3.0)[0]:  # 3 second timeout
                command = input().strip().lower()
                
                if command == 'q':
                    break
                elif command == 'r':
                    print("🔄 Refreshing plugins...")
                    result = lab_instruments.refresh_plugins()
                    print(f"✅ Refresh completed. Added: {len(result['added_devices'])}, Removed: {len(result['removed_devices'])}")
                    input("Press Enter to continue...")
                elif command == 'd':
                    print("🔍 Running diagnostics...")
                    diagnosis = lab_instruments.diagnose_system()
                    issues = diagnosis.get('issues', [])
                    print(f"✅ Diagnostics completed. Issues found: {len(issues)}")
                    if issues:
                        for issue in issues[:5]:
                            print(f"  • {issue}")
                    input("Press Enter to continue...")
                elif command == 'c':
                    lab_instruments.clear_connection_pool()
                    print("✅ Connection pool cleared")
                    input("Press Enter to continue...")
                elif command == 's':
                    stats = lab_instruments.get_connection_stats()
                    print("\n📊 Detailed Statistics:")
                    print(json.dumps(stats, indent=2, default=str))
                    input("Press Enter to continue...")
    
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()
        print("\n👋 Dashboard stopped")


def run_simple_monitor(duration=60, interval=5):
    """Run simple monitoring for specified duration"""
    monitor = SystemMonitor()
    monitor.update_interval = interval
    
    print(f"🔍 Starting {duration}s monitoring session (update every {interval}s)")
    
    try:
        monitor.start_monitoring()
        
        end_time = datetime.now() + timedelta(seconds=duration)
        
        while datetime.now() < end_time:
            summary = monitor.get_summary()
            if summary:
                timestamp = summary['timestamp'].strftime('%H:%M:%S')
                devices = summary.get('devices_registered', 0)
                issues = len(summary.get('issues', []))
                
                conn_stats = summary.get('connection_stats', {})
                total_conn = conn_stats.get('total_connections', 0)
                active_conn = conn_stats.get('active_connections', 0)
                
                print(f"[{timestamp}] Devices: {devices}, Connections: {total_conn} (active: {active_conn}), Issues: {issues}")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted")
    finally:
        monitor.stop_monitoring()
        
        # Show final summary
        summary = monitor.get_summary()
        if summary:
            print("\n📊 Final Summary:")
            print(f"Devices: {summary.get('devices_registered', 0)}")
            conn_stats = summary.get('connection_stats', {})
            print(f"Total connections: {conn_stats.get('total_connections', 0)}")
            print(f"Success rate: {(conn_stats.get('successful_connections', 0) / max(conn_stats.get('total_connections', 1), 1) * 100):.1f}%")
            
            issues = summary.get('issues', [])
            print(f"Issues: {len(issues)}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Lab Instruments System Monitor Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/monitor.py                    # Interactive dashboard
  python scripts/monitor.py --simple 120 10   # Simple monitoring for 2 minutes, 10s interval
        """
    )
    
    parser.add_argument('--simple', nargs=2, metavar=('DURATION', 'INTERVAL'), type=int,
                       help='Run simple monitoring (duration in seconds, update interval)')
    
    args = parser.parse_args()
    
    try:
        if args.simple:
            duration, interval = args.simple
            run_simple_monitor(duration, interval)
        else:
            run_interactive_dashboard()
    
    except Exception as e:
        print(f"❌ Monitor failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()