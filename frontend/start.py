#!/usr/bin/env python3
"""
RKLLM Frontend + Backend Launcher
Manages startup and shutdown of both services
"""
import os
import sys
import subprocess
import signal
import time
import requests
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent  # rkllm-openai directory
        self.processes = []
        self.running = False

    def start_backend(self):
        """Start RKLLM backend server"""
        print("\n[1/2] Starting RKLLM Backend Server...")
        
        backend_dir = self.base_dir
        cmd = [
            'conda', 'run', '-n', 'llm_api1',
            'python3', 'main.py'
        ]
        
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.processes.append(('Backend (main.py)', proc))
            print(f"  ✓ Backend started (PID: {proc.pid})")
            
            # Wait for backend to be ready
            print("  ⏳ Waiting for backend to be ready...", end='', flush=True)
            for i in range(30):  # 30 seconds timeout
                try:
                    response = requests.get('http://localhost:8080/v1/models', timeout=2)
                    if response.status_code == 200:
                        print(" ✓ Ready!")
                        return True
                except:
                    pass
                time.sleep(1)
                print('.', end='', flush=True)
            
            print(" ✗ Timeout!")
            return False
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return False

    def start_frontend(self):
        """Start Flask frontend server"""
        print("\n[2/2] Starting Frontend Server...")
        
        frontend_dir = self.base_dir / 'frontend'
        cmd = [
            'conda', 'run', '-n', 'llm_api1',
            'python3', 'app.py'
        ]
        
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.processes.append(('Frontend (app.py)', proc))
            print(f"  ✓ Frontend started (PID: {proc.pid})")
            
            # Wait for frontend to be ready
            print("  ⏳ Waiting for frontend to be ready...", end='', flush=True)
            for i in range(30):
                try:
                    response = requests.get('http://localhost:8000/', timeout=2)
                    if response.status_code == 200:
                        print(" ✓ Ready!")
                        return True
                except:
                    pass
                time.sleep(1)
                print('.', end='', flush=True)
            
            print(" ✗ Timeout!")
            return False
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return False

    def check_ports(self):
        """Check if ports are available"""
        print("\n[0/2] Checking ports...")
        
        # Check port 8080
        try:
            response = requests.get('http://localhost:8080/v1/models', timeout=2)
            print("  ⚠️  Port 8080 already in use (backend might be running)")
            return 'backend_running'
        except:
            print("  ✓ Port 8080 is free")
        
        # Check port 8000
        try:
            response = requests.get('http://localhost:8000/', timeout=2)
            print("  ⚠️  Port 8000 already in use (frontend might be running)")
            return 'frontend_running'
        except:
            print("  ✓ Port 8000 is free")
        
        return 'ready'

    def shutdown(self, signum=None, frame=None):
        """Gracefully shutdown all processes"""
        print("\n\n[Shutdown] Terminating services...")
        
        for name, proc in reversed(self.processes):
            try:
                print(f"  Stopping {name}...", end='', flush=True)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                    print(" ✓")
                except subprocess.TimeoutExpired:
                    print(" Force killing...", end='', flush=True)
                    proc.kill()
                    proc.wait(timeout=2)
                    print(" ✓")
            except Exception as e:
                print(f" ✗ {e}")
        
        print("\n  All services stopped\n")
        sys.exit(0)

    def run(self):
        """Main entry point"""
        print("\n" + "="*60)
        print("RKLLM Frontend + Backend Launcher")
        print("="*60)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        # Check ports
        port_status = self.check_ports()
        if port_status == 'backend_running':
            print("\n✓ Backend already running, starting only frontend...")
            if not self.start_frontend():
                self.shutdown()
                return
        elif port_status == 'frontend_running':
            print("\n✓ Frontend already running, starting only backend...")
            if not self.start_backend():
                self.shutdown()
                return
        else:
            if not self.start_backend():
                self.shutdown()
                return
            if not self.start_frontend():
                self.shutdown()
                return
        
        # Print summary
        print("\n" + "="*60)
        print("✓ All services started successfully!")
        print("="*60)
        print("\n📝 Access the frontend at:")
        print("  - Local:      http://localhost:8000")
        print("  - Network:    http://<your-ip>:8000")
        print("\n🔧 Backend API:")
        print("  - http://localhost:8080/v1/chat/completions")
        print("\n💡 Press Ctrl+C to stop all services")
        print("="*60 + "\n")
        
        self.running = True
        
        # Keep the script running and monitor processes
        try:
            while self.running:
                for name, proc in self.processes:
                    if proc.poll() is not None:  # Process has terminated
                        print(f"\n⚠️  {name} has stopped (exit code: {proc.returncode})")
                        self.running = False
                        break
                time.sleep(2)
        except KeyboardInterrupt:
            self.shutdown()

if __name__ == '__main__':
    manager = ServiceManager()
    manager.run()
