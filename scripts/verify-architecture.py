#!/usr/bin/env python3
"""
Co-Op OS v1.0.3 - Architecture Verification Script

This script verifies that the Co-Op OS implementation follows the documented
10-layer architecture. It checks for the presence and correctness of key
components in each layer.

Usage:
    python scripts/verify-architecture.py
"""

import sys
from pathlib import Path
import yaml

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class ArchitectureVerifier:
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
    
    def check(self, condition: bool, message: str, warning: bool = False):
        """Record a check result"""
        self.checks_total += 1
        if condition:
            self.checks_passed += 1
            print(f"  {GREEN}✓{RESET} {message}")
        else:
            if warning:
                self.warnings.append(message)
                print(f"  {YELLOW}⚠{RESET} {message}")
            else:
                self.errors.append(message)
                print(f"  {RED}✗{RESET} {message}")
    
    def verify_layer_1_infrastructure(self):
        """Layer 1: Docker Infrastructure & Resource Management"""
        print(f"\n{BLUE}Layer 1: Docker Infrastructure & Resource Management{RESET}")
        
        compose_file = self.root / "infrastructure" / "docker" / "docker-compose.yml"
        self.check(compose_file.exists(), "docker-compose.yml exists")
        
        if compose_file.exists():
            with open(compose_file) as f:
                content = f.read()
                compose = yaml.safe_load(content)
            
            # Check resource limits
            services_with_limits = []
            for service_name, service in compose.get('services', {}).items():
                deploy = service.get('deploy', {})
                resources = deploy.get('resources', {})
                if resources.get('limits'):
                    services_with_limits.append(service_name)
            
            self.check(len(services_with_limits) >= 5, 
                      f"Resource limits defined for {len(services_with_limits)} services")
            
            # Check security hardening
            services_with_cap_drop = []
            for service_name, service in compose.get('services', {}).items():
                if 'cap_drop' in service:
                    services_with_cap_drop.append(service_name)
            
            self.check(len(services_with_cap_drop) >= 5,
                      f"Security hardening (cap_drop) for {len(services_with_cap_drop)} services")
    
    def verify_layer_2_data_layer(self):
        """Layer 2: Data Layer (PostgreSQL, Redis, MinIO, Qdrant)"""
        print(f"\n{BLUE}Layer 2: Data Layer{RESET}")
        
        compose_file = self.root / "infrastructure" / "docker" / "docker-compose.yml"
        if compose_file.exists():
            with open(compose_file) as f:
                compose = yaml.safe_load(f.read())
            
            required_services = ['postgres', 'redis', 'minio']
            for service in required_services:
                exists = service in compose.get('services', {})
                self.check(exists, f"{service} service defined")
                
                if exists:
                    svc = compose['services'][service]
                    has_healthcheck = 'healthcheck' in svc
                    self.check(has_healthcheck, f"{service} has healthcheck")
                    
                    has_volumes = 'volumes' in svc or service == 'redis'
                    self.check(has_volumes, f"{service} has persistent volumes", warning=True)
    
    def verify_layer_3_api_layer(self):
        """Layer 3: API Layer (FastAPI)"""
        print(f"\n{BLUE}Layer 3: API Layer (FastAPI){RESET}")
        
        main_py = self.root / "services" / "api" / "app" / "main.py"
        self.check(main_py.exists(), "main.py exists")
        
        if main_py.exists():
            content = main_py.read_text()
            self.check('FastAPI' in content, "FastAPI app defined")
            self.check('lifespan' in content, "Lifespan context manager defined")
            self.check('CORS' in content, "CORS middleware configured")
        
        # Check for SSE streaming in chat router
        chat_router = self.root / "services" / "api" / "app" / "routers" / "chat.py"
        self.check(chat_router.exists(), "chat.py router exists")
        
        if chat_router.exists():
            content = chat_router.read_text()
            self.check('StreamingResponse' in content or 'text/event-stream' in content,
                      "SSE streaming implemented in chat")
    
    def verify_layer_4_data_access(self):
        """Layer 4: Data Access Layer"""
        print(f"\n{BLUE}Layer 4: Data Access Layer{RESET}")
        
        # Check Alembic migrations
        alembic_dir = self.root / "services" / "api" / "alembic"
        versions_dir = alembic_dir / "versions"
        self.check(alembic_dir.exists(), "Alembic directory exists")
        self.check(versions_dir.exists(), "Alembic versions directory exists")
        
        if versions_dir.exists():
            migrations = list(versions_dir.glob("*.py"))
            self.check(len(migrations) > 0, f"Database migrations exist ({len(migrations)} files)")
        
        # Check client implementations
        core_dir = self.root / "services" / "api" / "app" / "core"
        clients = {
            'redis_client.py': 'Redis client',
            'minio_client.py': 'MinIO client',
        }
        
        for filename, description in clients.items():
            client_file = core_dir / filename
            self.check(client_file.exists(), f"{description} exists")
        
        # Check Qdrant client
        qdrant_client = self.root / "services" / "api" / "app" / "db" / "qdrant_client.py"
        self.check(qdrant_client.exists(), "Qdrant client exists", warning=True)
    
    def verify_layer_5_security(self):
        """Layer 5: Security Layer"""
        print(f"\n{BLUE}Layer 5: Security Layer{RESET}")
        
        security_py = self.root / "services" / "api" / "app" / "core" / "security.py"
        self.check(security_py.exists(), "security.py exists")
        
        if security_py.exists():
            content = security_py.read_text()
            self.check('jwt' in content.lower() or 'JWT' in content,
                      "JWT implementation present")
            self.check('password' in content.lower() and 'hash' in content.lower(),
                      "Password hashing implementation present")
            self.check('verify' in content.lower(),
                      "Password verification present")
    
    def verify_layer_6_business_logic(self):
        """Layer 6: Business Logic Layer"""
        print(f"\n{BLUE}Layer 6: Business Logic Layer{RESET}")
        
        services_dir = self.root / "services" / "api" / "app" / "services"
        self.check(services_dir.exists(), "Services directory exists")
        
        if services_dir.exists():
            required_services = {
                'parser.py': 'Document parser',
                'chunker.py': 'Text chunker',
                'search.py': 'Search service',
            }
            
            for filename, description in required_services.items():
                service_file = services_dir / filename
                self.check(service_file.exists(), f"{description} exists")
        
        # Check embedder (can be in services or core)
        embedder_services = self.root / "services" / "api" / "app" / "services" / "embedder.py"
        embedder_core = self.root / "services" / "api" / "app" / "core" / "embedder.py"
        self.check(embedder_services.exists() or embedder_core.exists(), "Embedder service exists")
        
        # Check LangGraph implementation
        agent_dir = self.root / "services" / "api" / "app" / "agent"
        self.check(agent_dir.exists(), "Agent directory exists")
        
        if agent_dir.exists():
            graph_py = agent_dir / "graph.py"
            self.check(graph_py.exists(), "LangGraph implementation exists")
            
            if graph_py.exists():
                content = graph_py.read_text()
                self.check('StateGraph' in content or 'Graph' in content,
                          "StateGraph defined")
    
    def verify_layer_7_agent_orchestration(self):
        """Layer 7: Agent Orchestration Layer"""
        print(f"\n{BLUE}Layer 7: Agent Orchestration Layer{RESET}")
        
        nodes_py = self.root / "services" / "api" / "app" / "agent" / "nodes.py"
        self.check(nodes_py.exists(), "Agent nodes.py exists")
        
        if nodes_py.exists():
            content = nodes_py.read_text()
            required_nodes = ['retrieve', 'generate']
            for node in required_nodes:
                self.check(node in content.lower(),
                          f"'{node}' node implemented")
    
    def verify_layer_8_human_in_loop(self):
        """Layer 8: Human-in-the-Loop Layer"""
        print(f"\n{BLUE}Layer 8: Human-in-the-Loop Layer{RESET}")
        
        approvals_router = self.root / "services" / "api" / "app" / "routers" / "approvals.py"
        self.check(approvals_router.exists(), "Approvals router exists")
        
        models_py = self.root / "services" / "api" / "app" / "db" / "models.py"
        if models_py.exists():
            content = models_py.read_text()
            self.check('hitl' in content.lower() or 'approval' in content.lower(),
                      "HITL approval model defined", warning=True)
    
    def verify_layer_9_presentation(self):
        """Layer 9: Presentation Layer (Next.js)"""
        print(f"\n{BLUE}Layer 9: Presentation Layer (Next.js){RESET}")
        
        web_dir = self.root / "apps" / "web"
        self.check(web_dir.exists(), "Web app directory exists")
        
        if web_dir.exists():
            # Check Next.js structure
            app_dir = web_dir / "src" / "app"
            self.check(app_dir.exists(), "Next.js app directory exists")
            
            # Check key pages
            pages = {
                '(app)/dashboard/page.tsx': 'Dashboard page',
                '(app)/chat/page.tsx': 'Chat page',
                '(app)/documents/page.tsx': 'Documents page',
                '(app)/search/page.tsx': 'Search page',
                '(auth)/login/page.tsx': 'Login page',
            }
            
            for page_path, description in pages.items():
                page_file = app_dir / page_path
                self.check(page_file.exists(), f"{description} exists")
            
            # Check dark theme
            globals_css = app_dir / "globals.css"
            if globals_css.exists():
                content = globals_css.read_text()
                self.check('--bg-base' in content or 'dark' in content.lower(),
                          "Dark theme CSS variables defined")
    
    def verify_layer_10_observability(self):
        """Layer 10: Observability Layer"""
        print(f"\n{BLUE}Layer 10: Observability Layer{RESET}")
        
        health_router = self.root / "services" / "api" / "app" / "routers" / "health.py"
        self.check(health_router.exists(), "Health router exists")
        
        if health_router.exists():
            content = health_router.read_text()
            self.check('/health' in content, "Health endpoint defined")
            self.check('/ready' in content or 'ready' in content.lower(),
                      "Ready endpoint defined", warning=True)
            self.check('/metrics' in content or 'metrics' in content.lower(),
                      "Metrics endpoint defined", warning=True)
        
        # Check for system monitor
        crons_dir = self.root / "services" / "api" / "app" / "crons"
        if crons_dir.exists():
            system_monitor = crons_dir / "system_monitor.py"
            self.check(system_monitor.exists(), "System monitor exists", warning=True)
    
    def verify_configuration_modes(self):
        """Verify Hardware-adaptive and Minimalist mode configurations"""
        print(f"\n{BLUE}Configuration Modes{RESET}")
        
        compose_file = self.root / "infrastructure" / "docker" / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            
            # Check for resource limits (hardware-adaptive)
            self.check('limits:' in content and 'memory:' in content,
                      "Hardware-adaptive resource limits configured")
            
            # Check for minimal service set
            required_minimal = ['postgres', 'redis', 'minio', 'co-op-api', 'co-op-web']
            compose = yaml.safe_load(content)
            services = list(compose.get('services', {}).keys())
            
            has_minimal = all(svc in services for svc in required_minimal)
            self.check(has_minimal,
                      f"Minimalist mode services present ({len(services)} total services)")
    
    def run(self):
        """Run all verification checks"""
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Co-Op OS v1.0.3 - Architecture Verification{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        
        self.verify_layer_1_infrastructure()
        self.verify_layer_2_data_layer()
        self.verify_layer_3_api_layer()
        self.verify_layer_4_data_access()
        self.verify_layer_5_security()
        self.verify_layer_6_business_logic()
        self.verify_layer_7_agent_orchestration()
        self.verify_layer_8_human_in_loop()
        self.verify_layer_9_presentation()
        self.verify_layer_10_observability()
        self.verify_configuration_modes()
        
        # Print summary
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Verification Summary{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"Total checks: {self.checks_total}")
        print(f"{GREEN}Passed: {self.checks_passed}{RESET}")
        print(f"{RED}Failed: {len(self.errors)}{RESET}")
        print(f"{YELLOW}Warnings: {len(self.warnings)}{RESET}")
        
        if self.errors:
            print(f"\n{RED}Errors:{RESET}")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors:
            print(f"\n{GREEN}✓ Architecture verification passed!{RESET}")
            return 0
        else:
            print(f"\n{RED}✗ Architecture verification failed with {len(self.errors)} error(s){RESET}")
            return 1

if __name__ == '__main__':
    verifier = ArchitectureVerifier()
    sys.exit(verifier.run())
