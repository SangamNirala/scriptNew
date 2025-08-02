"""
Legal Workflow Automation System
Provides comprehensive workflow automation for legal practices using free tools
Integrates with n8n, Apache Airflow, and custom workflow engines
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of legal workflows"""
    CLIENT_ONBOARDING = "client_onboarding"
    CONTRACT_REVIEW = "contract_review"
    DOCUMENT_GENERATION = "document_generation"
    LEGAL_RESEARCH = "legal_research"
    CASE_MANAGEMENT = "case_management"
    COMPLIANCE_CHECK = "compliance_check"
    BILLING_AUTOMATION = "billing_automation"
    DOCUMENT_REVIEW = "document_review"
    CLIENT_COMMUNICATION = "client_communication"
    MATTER_OPENING = "matter_opening"
    CONFLICT_CHECK = "conflict_check"
    TIME_TRACKING = "time_tracking"

class WorkflowStatus(Enum):
    """Workflow execution statuses"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Individual task statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowPriority(Enum):
    """Workflow priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    task_id: str
    name: str
    description: str
    task_type: str  # "manual", "automated", "approval", "notification"
    parameters: Dict[str, Any]
    dependencies: List[str]  # List of task_ids that must complete first
    estimated_duration: int  # minutes
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.result_data is None:
            self.result_data = {}

class LegalWorkflow(BaseModel):
    """Legal workflow definition and execution state"""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    workflow_type: WorkflowType
    law_firm_id: str
    client_id: Optional[str] = None
    matter_id: Optional[str] = None
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    tasks: List[WorkflowTask] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.CREATED
    progress_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str
    current_task: Optional[str] = None
    automation_engine: str = "internal"  # "internal", "n8n", "airflow"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sla_hours: Optional[int] = None
    escalation_rules: List[Dict[str, Any]] = Field(default_factory=list)

class WorkflowTemplate(BaseModel):
    """Reusable workflow template"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    workflow_type: WorkflowType
    category: str
    task_templates: List[Dict[str, Any]] = Field(default_factory=list)
    default_sla_hours: int = 24
    required_roles: List[str] = Field(default_factory=list)
    automation_level: str = "semi_automated"  # "manual", "semi_automated", "fully_automated"
    industry_specific: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class WorkflowIntegration(BaseModel):
    """External workflow automation integration"""
    integration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    engine_type: str  # "n8n", "airflow", "zapier", "custom"
    api_endpoint: str
    authentication: Dict[str, str] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LegalWorkflowAutomation:
    """
    Comprehensive legal workflow automation system
    Supports multiple free automation engines and legal-specific workflows
    """
    
    def __init__(self):
        self.workflows: Dict[str, LegalWorkflow] = {}
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.integrations: Dict[str, WorkflowIntegration] = {}
        self.task_handlers: Dict[str, Callable] = {}
        
        # Initialize workflow templates and integrations
        self.initialize_workflow_templates()
        self.initialize_automation_integrations()
        self.register_task_handlers()
    
    def initialize_workflow_templates(self):
        """Initialize legal workflow templates"""
        
        # Client Onboarding Workflow Template
        client_onboarding_template = WorkflowTemplate(
            template_id="client_onboarding",  # Set specific template ID
            name="Client Onboarding Process",
            description="Comprehensive client onboarding workflow for new legal matters",
            workflow_type=WorkflowType.CLIENT_ONBOARDING,
            category="Client Management",
            task_templates=[
                {
                    "name": "Conflict Check",
                    "description": "Check for potential conflicts of interest",
                    "task_type": "automated",
                    "parameters": {"check_type": "comprehensive", "databases": ["internal", "external"]},
                    "estimated_duration": 15,
                    "dependencies": []
                },
                {
                    "name": "Client Information Collection",
                    "description": "Gather client information and documentation",
                    "task_type": "manual",
                    "parameters": {"forms": ["client_intake", "engagement_agreement", "billing_information"]},
                    "estimated_duration": 60,
                    "dependencies": ["conflict_check"]
                },
                {
                    "name": "Matter Opening",
                    "description": "Create new matter in practice management system",
                    "task_type": "automated",
                    "parameters": {"template": "default", "billing_arrangements": ["hourly", "flat_fee", "contingency"]},
                    "estimated_duration": 10,
                    "dependencies": ["client_information_collection"]
                },
                {
                    "name": "Initial Document Preparation",
                    "description": "Prepare initial legal documents",
                    "task_type": "automated",
                    "parameters": {"document_types": ["engagement_letter", "fee_agreement", "privacy_notice"]},
                    "estimated_duration": 30,
                    "dependencies": ["matter_opening"]
                },
                {
                    "name": "Client Welcome Package",
                    "description": "Send welcome package to client",
                    "task_type": "automated",
                    "parameters": {"delivery_method": "email", "include_portal_access": True},
                    "estimated_duration": 5,
                    "dependencies": ["initial_document_preparation"]
                }
            ],
            default_sla_hours=48,
            required_roles=["intake_coordinator", "attorney", "paralegal"],
            automation_level="semi_automated",
            industry_specific=["law_firm", "corporate_legal", "solo_practice"],
            compliance_requirements=["attorney_client_privilege", "bar_rules", "conflict_check_rules"]
        )
        
        # Contract Review Workflow Template
        contract_review_template = WorkflowTemplate(
            template_id="contract_review",  # Set specific template ID
            name="Contract Review and Analysis",
            description="Comprehensive contract review workflow with AI assistance",
            workflow_type=WorkflowType.CONTRACT_REVIEW,
            category="Document Review",
            task_templates=[
                {
                    "name": "Initial Contract Intake",
                    "description": "Receive and catalog contract for review",
                    "task_type": "manual",
                    "parameters": {"intake_form": "contract_review_request", "priority_assessment": True},
                    "estimated_duration": 10,
                    "dependencies": []
                },
                {
                    "name": "AI-Powered Initial Analysis",
                    "description": "Automated contract analysis using AI",
                    "task_type": "automated",
                    "parameters": {"analysis_type": "comprehensive", "risk_assessment": True, "clause_extraction": True},
                    "estimated_duration": 5,
                    "dependencies": ["initial_contract_intake"]
                },
                {
                    "name": "Attorney Review",
                    "description": "Legal professional review of contract and AI analysis",
                    "task_type": "manual",
                    "parameters": {"review_checklist": True, "redlining_required": True},
                    "estimated_duration": 120,
                    "dependencies": ["ai_powered_initial_analysis"]
                },
                {
                    "name": "Client Communication",
                    "description": "Communicate findings and recommendations to client",
                    "task_type": "manual",
                    "parameters": {"communication_method": "email", "summary_report": True},
                    "estimated_duration": 30,
                    "dependencies": ["attorney_review"]
                },
                {
                    "name": "Final Documentation",
                    "description": "Prepare final review documentation and billing",
                    "task_type": "automated",
                    "parameters": {"time_tracking": True, "billing_entry": True, "document_storage": True},
                    "estimated_duration": 15,
                    "dependencies": ["client_communication"]
                }
            ],
            default_sla_hours=72,
            required_roles=["attorney", "paralegal"],
            automation_level="semi_automated",
            industry_specific=["business_law", "corporate_law", "commercial_law"],
            compliance_requirements=["attorney_client_privilege", "professional_liability", "conflict_check"]
        )
        
        # Legal Research Workflow Template
        legal_research_template = WorkflowTemplate(
            template_id="legal_research",  # Set specific template ID
            name="Comprehensive Legal Research",
            description="Systematic legal research workflow with AI enhancement",
            workflow_type=WorkflowType.LEGAL_RESEARCH,
            category="Legal Research",
            task_templates=[
                {
                    "name": "Research Request Analysis",
                    "description": "Analyze and scope the legal research request",
                    "task_type": "manual",
                    "parameters": {"scope_definition": True, "jurisdiction_identification": True, "timeline_assessment": True},
                    "estimated_duration": 30,
                    "dependencies": []
                },
                {
                    "name": "AI-Assisted Research Planning",
                    "description": "Use AI to plan research strategy and identify sources",
                    "task_type": "automated",
                    "parameters": {"database_selection": True, "keyword_generation": True, "source_prioritization": True},
                    "estimated_duration": 15,
                    "dependencies": ["research_request_analysis"]
                },
                {
                    "name": "Primary Source Research",
                    "description": "Research primary legal sources (cases, statutes, regulations)",
                    "task_type": "automated",
                    "parameters": {"databases": ["courtlistener", "google_scholar", "legal_information_institute"], "comprehensive_search": True},
                    "estimated_duration": 60,
                    "dependencies": ["ai_assisted_research_planning"]
                },
                {
                    "name": "Secondary Source Analysis",
                    "description": "Analyze secondary sources and legal commentary",
                    "task_type": "manual",
                    "parameters": {"law_reviews": True, "practice_guides": True, "expert_commentary": True},
                    "estimated_duration": 90,
                    "dependencies": ["primary_source_research"]
                },
                {
                    "name": "Research Synthesis",
                    "description": "Synthesize findings into comprehensive research memorandum",
                    "task_type": "manual",
                    "parameters": {"memorandum_format": "professional", "citation_style": "bluebook", "executive_summary": True},
                    "estimated_duration": 120,
                    "dependencies": ["secondary_source_analysis"]
                }
            ],
            default_sla_hours=96,
            required_roles=["attorney", "law_clerk", "paralegal"],
            automation_level="semi_automated",
            industry_specific=["all_practice_areas"],
            compliance_requirements=["research_standards", "citation_accuracy", "professional_responsibility"]
        )
        
        # Document Generation Workflow Template
        document_generation_template = WorkflowTemplate(
            name="Automated Legal Document Generation",
            description="AI-powered legal document generation workflow",
            workflow_type=WorkflowType.DOCUMENT_GENERATION,
            category="Document Automation",
            task_templates=[
                {
                    "name": "Document Request Processing",
                    "description": "Process document generation request and gather requirements",
                    "task_type": "manual",
                    "parameters": {"document_type_selection": True, "client_information_gathering": True, "template_selection": True},
                    "estimated_duration": 20,
                    "dependencies": []
                },
                {
                    "name": "AI Document Generation",
                    "description": "Generate document using AI with legal templates",
                    "task_type": "automated",
                    "parameters": {"template_library": "comprehensive", "jurisdiction_compliance": True, "clause_optimization": True},
                    "estimated_duration": 10,
                    "dependencies": ["document_request_processing"]
                },
                {
                    "name": "Attorney Review and Approval",
                    "description": "Legal professional review of generated document",
                    "task_type": "manual",
                    "parameters": {"quality_checklist": True, "compliance_review": True, "customization_required": True},
                    "estimated_duration": 45,
                    "dependencies": ["ai_document_generation"]
                },
                {
                    "name": "Document Finalization",
                    "description": "Finalize document formatting and prepare for execution",
                    "task_type": "automated",
                    "parameters": {"formatting_standards": "professional", "signature_blocks": True, "version_control": True},
                    "estimated_duration": 15,
                    "dependencies": ["attorney_review_and_approval"]
                },
                {
                    "name": "Client Delivery",
                    "description": "Deliver final document to client with execution instructions",
                    "task_type": "automated",
                    "parameters": {"delivery_method": "secure_portal", "execution_instructions": True, "follow_up_scheduling": True},
                    "estimated_duration": 10,
                    "dependencies": ["document_finalization"]
                }
            ],
            default_sla_hours=24,
            required_roles=["attorney", "paralegal", "document_specialist"],
            automation_level="highly_automated",
            industry_specific=["business_law", "real_estate", "employment_law", "family_law"],
            compliance_requirements=["document_standards", "attorney_client_privilege", "professional_liability"]
        )
        
        # Case Management Workflow Template
        case_management_template = WorkflowTemplate(
            name="Litigation Case Management",
            description="Comprehensive litigation case management workflow",
            workflow_type=WorkflowType.CASE_MANAGEMENT,
            category="Litigation",
            task_templates=[
                {
                    "name": "Case Evaluation and Strategy",
                    "description": "Initial case evaluation and litigation strategy development",
                    "task_type": "manual",
                    "parameters": {"case_assessment": True, "strategy_development": True, "resource_planning": True},
                    "estimated_duration": 180,
                    "dependencies": []
                },
                {
                    "name": "Court Filing Preparation",
                    "description": "Prepare initial court filings and documentation",
                    "task_type": "manual",
                    "parameters": {"pleading_preparation": True, "evidence_compilation": True, "court_rules_compliance": True},
                    "estimated_duration": 240,
                    "dependencies": ["case_evaluation_and_strategy"]
                },
                {
                    "name": "Discovery Planning",
                    "description": "Plan and coordinate discovery process",
                    "task_type": "manual",
                    "parameters": {"discovery_strategy": True, "document_requests": True, "deposition_scheduling": True},
                    "estimated_duration": 120,
                    "dependencies": ["court_filing_preparation"]
                },
                {
                    "name": "Case Timeline Management",
                    "description": "Automated case timeline and deadline management",
                    "task_type": "automated",
                    "parameters": {"court_deadline_tracking": True, "reminder_system": True, "calendar_integration": True},
                    "estimated_duration": 15,
                    "dependencies": ["discovery_planning"]
                },
                {
                    "name": "Regular Case Reviews",
                    "description": "Scheduled case status reviews and strategy adjustments",
                    "task_type": "manual",
                    "parameters": {"weekly_reviews": True, "client_updates": True, "strategy_adjustments": True},
                    "estimated_duration": 60,
                    "dependencies": ["case_timeline_management"]
                }
            ],
            default_sla_hours=168,  # 1 week
            required_roles=["litigator", "paralegal", "case_manager"],
            automation_level="semi_automated",
            industry_specific=["litigation", "civil_law", "commercial_disputes"],
            compliance_requirements=["court_rules", "professional_responsibility", "discovery_rules", "attorney_client_privilege"]
        )
        
        # Store templates
        templates = [
            client_onboarding_template,
            contract_review_template,
            legal_research_template,
            document_generation_template,
            case_management_template
        ]
        
        for template in templates:
            self.workflow_templates[template.template_id] = template
        
        logger.info(f"Initialized {len(templates)} legal workflow templates")
    
    def initialize_automation_integrations(self):
        """Initialize free automation tool integrations"""
        
        # n8n Integration (Open Source Workflow Automation)
        n8n_integration = WorkflowIntegration(
            name="n8n Workflow Automation",
            engine_type="n8n",
            api_endpoint="http://localhost:5678/api/v1",
            authentication={
                "type": "bearer_token",
                "token": "N8N_API_TOKEN_PLACEHOLDER"
            },
            capabilities=[
                "workflow_creation",
                "webhook_triggers",
                "api_integrations",
                "email_automation",
                "database_operations",
                "file_operations",
                "scheduling",
                "conditional_logic"
            ]
        )
        
        # Apache Airflow Integration (Open Source Workflow Orchestration)
        airflow_integration = WorkflowIntegration(
            name="Apache Airflow Orchestration",
            engine_type="airflow",
            api_endpoint="http://localhost:8080/api/v1",
            authentication={
                "type": "basic_auth",
                "username": "admin",
                "password": "AIRFLOW_PASSWORD_PLACEHOLDER"
            },
            capabilities=[
                "dag_creation",
                "task_scheduling",
                "dependency_management",
                "monitoring",
                "error_handling",
                "parallel_processing",
                "resource_management",
                "logging"
            ]
        )
        
        # Custom Internal Engine
        internal_integration = WorkflowIntegration(
            name="Internal Workflow Engine",
            engine_type="custom",
            api_endpoint="http://localhost:8001/api/workflows",
            authentication={
                "type": "internal",
                "token": "internal"
            },
            capabilities=[
                "legal_specific_tasks",
                "ai_integration",
                "document_generation",
                "client_communication",
                "billing_integration",
                "time_tracking",
                "compliance_checking",
                "audit_trail"
            ]
        )
        
        # Store integrations
        integrations = [n8n_integration, airflow_integration, internal_integration]
        for integration in integrations:
            self.integrations[integration.integration_id] = integration
        
        logger.info(f"Initialized {len(integrations)} workflow automation integrations")
    
    def register_task_handlers(self):
        """Register handlers for different task types"""
        
        self.task_handlers = {
            "conflict_check": self._handle_conflict_check,
            "document_generation": self._handle_document_generation,
            "ai_analysis": self._handle_ai_analysis,
            "client_communication": self._handle_client_communication,
            "legal_research": self._handle_legal_research,
            "billing_entry": self._handle_billing_entry,
            "time_tracking": self._handle_time_tracking,
            "compliance_check": self._handle_compliance_check,
            "court_filing": self._handle_court_filing,
            "deadline_tracking": self._handle_deadline_tracking,
            "notification": self._handle_notification,
            "approval": self._handle_approval_task
        }
    
    def create_workflow_from_template(self, template_id: str, law_firm_id: str, 
                                     created_by: str, client_id: str = None, 
                                     matter_id: str = None, 
                                     custom_parameters: Dict[str, Any] = None) -> LegalWorkflow:
        """Create a new workflow instance from a template"""
        
        if template_id not in self.workflow_templates:
            raise ValueError(f"Workflow template {template_id} not found")
        
        template = self.workflow_templates[template_id]
        
        # Create workflow tasks from template
        workflow_tasks = []
        for i, task_template in enumerate(template.task_templates):
            task = WorkflowTask(
                task_id=f"task_{i+1}_{uuid.uuid4().hex[:8]}",
                name=task_template["name"],
                description=task_template["description"],
                task_type=task_template["task_type"],
                parameters=task_template["parameters"].copy(),
                dependencies=task_template.get("dependencies", []),
                estimated_duration=task_template.get("estimated_duration", 60)
            )
            
            # Apply custom parameters if provided
            if custom_parameters and task_template["name"] in custom_parameters:
                task.parameters.update(custom_parameters[task_template["name"]])
            
            workflow_tasks.append(task)
        
        # Create workflow instance
        workflow = LegalWorkflow(
            name=f"{template.name} - {datetime.utcnow().strftime('%Y%m%d_%H%M')}",
            description=template.description,
            workflow_type=template.workflow_type,
            law_firm_id=law_firm_id,
            client_id=client_id,
            matter_id=matter_id,
            tasks=workflow_tasks,
            created_by=created_by,
            sla_hours=template.default_sla_hours,
            metadata={
                "template_id": template_id,
                "automation_level": template.automation_level,
                "required_roles": template.required_roles,
                "compliance_requirements": template.compliance_requirements
            }
        )
        
        # Store workflow
        self.workflows[workflow.workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow.workflow_id} from template {template.name}")
        
        return workflow
    
    async def start_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Start executing a workflow"""
        
        if workflow_id not in self.workflows:
            return {
                "success": False,
                "error": "Workflow not found",
                "error_code": "WORKFLOW_NOT_FOUND"
            }
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.CREATED:
            return {
                "success": False,
                "error": f"Workflow is in {workflow.status.value} state, cannot start",
                "error_code": "INVALID_STATUS"
            }
        
        # Update workflow status
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        # Start first tasks (tasks with no dependencies)
        ready_tasks = [task for task in workflow.tasks if not task.dependencies]
        
        results = []
        for task in ready_tasks:
            result = await self._execute_task(workflow, task)
            results.append(result)
        
        # Update progress
        self._update_workflow_progress(workflow)
        
        logger.info(f"Started workflow {workflow_id} with {len(ready_tasks)} initial tasks")
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "started_tasks": len(ready_tasks),
            "initial_results": results
        }
    
    async def _execute_task(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Execute a single workflow task"""
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            # Determine task handler based on task type or name
            handler_key = task.name.lower().replace(" ", "_")
            if handler_key in self.task_handlers:
                handler = self.task_handlers[handler_key]
            elif task.task_type in self.task_handlers:
                handler = self.task_handlers[task.task_type]
            else:
                handler = self._handle_generic_task
            
            # Execute task
            result = await handler(workflow, task)
            
            # Update task status
            if result.get("success", False):
                task.status = TaskStatus.COMPLETED
                task.result_data = result.get("data", {})
            else:
                task.status = TaskStatus.FAILED
                task.error_message = result.get("error", "Task execution failed")
            
            task.completed_at = datetime.utcnow()
            
            # Check if this completion enables new tasks
            if task.status == TaskStatus.COMPLETED:
                await self._check_and_start_dependent_tasks(workflow, task.task_id)
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id
            }
    
    async def _check_and_start_dependent_tasks(self, workflow: LegalWorkflow, completed_task_id: str):
        """Check if any tasks can now be started due to dependency completion"""
        
        for task in workflow.tasks:
            if (task.status == TaskStatus.PENDING and 
                completed_task_id in task.dependencies and
                self._all_dependencies_completed(workflow, task)):
                
                # Start this task
                await self._execute_task(workflow, task)
        
        # Update workflow progress
        self._update_workflow_progress(workflow)
        
        # Check if workflow is complete
        if self._is_workflow_complete(workflow):
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            logger.info(f"Workflow {workflow.workflow_id} completed successfully")
    
    def _all_dependencies_completed(self, workflow: LegalWorkflow, task: WorkflowTask) -> bool:
        """Check if all task dependencies are completed"""
        
        if not task.dependencies:
            return True
        
        task_dict = {t.task_id: t for t in workflow.tasks}
        
        for dep_id in task.dependencies:
            if dep_id not in task_dict or task_dict[dep_id].status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _is_workflow_complete(self, workflow: LegalWorkflow) -> bool:
        """Check if all workflow tasks are completed"""
        
        for task in workflow.tasks:
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]:
                return False
        
        return True
    
    def _update_workflow_progress(self, workflow: LegalWorkflow):
        """Update workflow progress percentage"""
        
        total_tasks = len(workflow.tasks)
        if total_tasks == 0:
            workflow.progress_percentage = 100.0
            return
        
        completed_tasks = sum(1 for task in workflow.tasks 
                             if task.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED])
        
        workflow.progress_percentage = (completed_tasks / total_tasks) * 100.0
        
        # Update current task
        running_tasks = [task for task in workflow.tasks if task.status == TaskStatus.RUNNING]
        if running_tasks:
            workflow.current_task = running_tasks[0].name
        elif workflow.progress_percentage == 100.0:
            workflow.current_task = None
        else:
            pending_tasks = [task for task in workflow.tasks if task.status == TaskStatus.PENDING]
            if pending_tasks:
                workflow.current_task = f"Waiting for: {pending_tasks[0].name}"
    
    # Task Handler Methods
    async def _handle_conflict_check(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle conflict of interest checking"""
        
        try:
            # Simulate conflict checking process
            client_name = task.parameters.get("client_name", "Unknown Client")
            check_type = task.parameters.get("check_type", "basic")
            
            # In real implementation, this would check against conflict databases
            conflicts_found = []  # Simulate no conflicts
            
            result_data = {
                "conflict_check_id": str(uuid.uuid4()),
                "client_name": client_name,
                "check_type": check_type,
                "conflicts_found": conflicts_found,
                "status": "clear" if not conflicts_found else "conflicts_detected",
                "checked_at": datetime.utcnow().isoformat(),
                "databases_checked": ["internal_conflicts", "external_database"]
            }
            
            return {
                "success": True,
                "data": result_data,
                "message": f"Conflict check completed for {client_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_document_generation(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle automated document generation"""
        
        try:
            document_type = task.parameters.get("document_type", "generic")
            template_id = task.parameters.get("template_id", "default")
            
            # Simulate document generation
            document_data = {
                "document_id": str(uuid.uuid4()),
                "document_type": document_type,
                "template_used": template_id,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "generated",
                "file_path": f"/documents/{document_type}_{uuid.uuid4().hex[:8]}.pdf",
                "word_count": 1250,
                "pages": 3
            }
            
            return {
                "success": True,
                "data": document_data,
                "message": f"Document {document_type} generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_ai_analysis(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle AI-powered analysis tasks"""
        
        try:
            analysis_type = task.parameters.get("analysis_type", "general")
            content = task.parameters.get("content", "")
            
            # Simulate AI analysis
            analysis_result = {
                "analysis_id": str(uuid.uuid4()),
                "analysis_type": analysis_type,
                "content_analyzed": len(content) > 0,
                "confidence_score": 0.89,
                "key_findings": [
                    "Standard contract terms identified",
                    "No unusual risk factors detected",
                    "Compliant with jurisdiction requirements"
                ],
                "recommendations": [
                    "Review termination clauses",
                    "Consider adding force majeure provision"
                ],
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "data": analysis_result,
                "message": f"AI analysis ({analysis_type}) completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_client_communication(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle automated client communication"""
        
        try:
            communication_type = task.parameters.get("communication_type", "email")
            template = task.parameters.get("template", "default")
            client_id = workflow.client_id or "unknown"
            
            # Simulate client communication
            communication_data = {
                "communication_id": str(uuid.uuid4()),
                "client_id": client_id,
                "type": communication_type,
                "template_used": template,
                "sent_at": datetime.utcnow().isoformat(),
                "status": "sent",
                "delivery_confirmation": True
            }
            
            return {
                "success": True,
                "data": communication_data,
                "message": f"Client communication ({communication_type}) sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_legal_research(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle automated legal research tasks"""
        
        try:
            research_query = task.parameters.get("query", "")
            jurisdiction = task.parameters.get("jurisdiction", "US")
            databases = task.parameters.get("databases", ["courtlistener"])
            
            # Simulate legal research
            research_result = {
                "research_id": str(uuid.uuid4()),
                "query": research_query,
                "jurisdiction": jurisdiction,
                "databases_searched": databases,
                "results_found": 15,
                "relevant_cases": 5,
                "relevant_statutes": 3,
                "research_completed_at": datetime.utcnow().isoformat(),
                "confidence_score": 0.92
            }
            
            return {
                "success": True,
                "data": research_result,
                "message": "Legal research completed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_billing_entry(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle automated billing entries"""
        
        try:
            time_spent = task.parameters.get("time_spent", 60)  # minutes
            billing_rate = task.parameters.get("billing_rate", 300.0)  # per hour
            description = task.parameters.get("description", "Workflow task completion")
            
            # Calculate billing amount
            hours = time_spent / 60.0
            amount = hours * billing_rate
            
            billing_entry = {
                "entry_id": str(uuid.uuid4()),
                "matter_id": workflow.matter_id,
                "client_id": workflow.client_id,
                "time_spent_minutes": time_spent,
                "time_spent_hours": round(hours, 2),
                "billing_rate": billing_rate,
                "amount": round(amount, 2),
                "description": description,
                "entry_date": datetime.utcnow().isoformat(),
                "status": "recorded"
            }
            
            return {
                "success": True,
                "data": billing_entry,
                "message": f"Billing entry recorded: ${amount:.2f}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_time_tracking(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle automated time tracking"""
        
        try:
            start_time = task.started_at or datetime.utcnow()
            end_time = task.completed_at or datetime.utcnow()
            duration = (end_time - start_time).total_seconds() / 60  # minutes
            
            time_entry = {
                "entry_id": str(uuid.uuid4()),
                "task_id": task.task_id,
                "workflow_id": workflow.workflow_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": round(duration, 2),
                "activity": task.name,
                "billable": task.parameters.get("billable", True),
                "attorney": workflow.created_by
            }
            
            return {
                "success": True,
                "data": time_entry,
                "message": f"Time tracked: {duration:.1f} minutes"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_compliance_check(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle compliance checking tasks"""
        
        try:
            compliance_frameworks = task.parameters.get("frameworks", ["attorney_client_privilege"])
            
            # Simulate compliance check
            compliance_result = {
                "check_id": str(uuid.uuid4()),
                "frameworks_checked": compliance_frameworks,
                "compliance_status": "compliant",
                "issues_found": [],
                "recommendations": ["Continue following current procedures"],
                "checked_at": datetime.utcnow().isoformat(),
                "next_review_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
            }
            
            return {
                "success": True,
                "data": compliance_result,
                "message": "Compliance check completed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_court_filing(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle court filing preparation and submission"""
        
        try:
            document_type = task.parameters.get("document_type", "motion")
            court_name = task.parameters.get("court", "District Court")
            
            filing_result = {
                "filing_id": str(uuid.uuid4()),
                "document_type": document_type,
                "court": court_name,
                "filing_date": datetime.utcnow().isoformat(),
                "status": "prepared",  # In real implementation: "filed" after actual submission
                "confirmation_number": f"FILING_{uuid.uuid4().hex[:8].upper()}",
                "fees_required": 350.00,
                "next_deadline": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            return {
                "success": True,
                "data": filing_result,
                "message": f"Court filing ({document_type}) prepared successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_deadline_tracking(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle deadline and calendar management"""
        
        try:
            deadlines = task.parameters.get("deadlines", [])
            
            tracking_result = {
                "tracking_id": str(uuid.uuid4()),
                "deadlines_added": len(deadlines),
                "reminders_set": len(deadlines) * 3,  # Multiple reminders per deadline
                "calendar_updated": True,
                "next_deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() if deadlines else None,
                "tracking_activated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "data": tracking_result,
                "message": f"Deadline tracking activated for {len(deadlines)} deadlines"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_notification(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle notification and alert tasks"""
        
        try:
            notification_type = task.parameters.get("type", "email")
            recipients = task.parameters.get("recipients", [])
            message = task.parameters.get("message", "Workflow notification")
            
            notification_result = {
                "notification_id": str(uuid.uuid4()),
                "type": notification_type,
                "recipients_count": len(recipients),
                "message": message,
                "sent_at": datetime.utcnow().isoformat(),
                "delivery_status": "sent",
                "delivery_confirmation": True
            }
            
            return {
                "success": True,
                "data": notification_result,
                "message": f"Notification sent to {len(recipients)} recipients"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_approval_task(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle approval and review tasks"""
        
        try:
            approval_type = task.parameters.get("approval_type", "document_review")
            approver = task.parameters.get("approver", "supervising_attorney")
            
            # For automation demo, simulate automatic approval
            # In real implementation, this would wait for human approval
            approval_result = {
                "approval_id": str(uuid.uuid4()),
                "type": approval_type,
                "approver": approver,
                "status": "pending",  # In real implementation, would be "pending" until human action
                "requested_at": datetime.utcnow().isoformat(),
                "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat()
            }
            
            return {
                "success": True,
                "data": approval_result,
                "message": f"Approval request sent to {approver}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_generic_task(self, workflow: LegalWorkflow, task: WorkflowTask) -> Dict[str, Any]:
        """Handle generic workflow tasks"""
        
        try:
            # Generic task handling
            result_data = {
                "task_id": task.task_id,
                "task_name": task.name,
                "executed_at": datetime.utcnow().isoformat(),
                "parameters": task.parameters,
                "status": "completed"
            }
            
            return {
                "success": True,
                "data": result_data,
                "message": f"Generic task '{task.name}' completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        
        if workflow_id not in self.workflows:
            return {
                "success": False,
                "error": "Workflow not found",
                "error_code": "WORKFLOW_NOT_FOUND"
            }
        
        workflow = self.workflows[workflow_id]
        
        # Calculate task statistics
        task_stats = {
            "total": len(workflow.tasks),
            "pending": sum(1 for t in workflow.tasks if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in workflow.tasks if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in workflow.tasks if t.status == TaskStatus.FAILED),
            "skipped": sum(1 for t in workflow.tasks if t.status == TaskStatus.SKIPPED)
        }
        
        # Calculate estimated completion time
        remaining_tasks = [t for t in workflow.tasks if t.status == TaskStatus.PENDING]
        estimated_remaining_minutes = sum(t.estimated_duration for t in remaining_tasks)
        estimated_completion = None
        if estimated_remaining_minutes > 0:
            estimated_completion = (datetime.utcnow() + timedelta(minutes=estimated_remaining_minutes)).isoformat()
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "name": workflow.name,
            "type": workflow.workflow_type.value,
            "status": workflow.status.value,
            "progress_percentage": workflow.progress_percentage,
            "current_task": workflow.current_task,
            "task_statistics": task_stats,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "estimated_completion": estimated_completion,
            "sla_hours": workflow.sla_hours,
            "law_firm_id": workflow.law_firm_id,
            "client_id": workflow.client_id,
            "matter_id": workflow.matter_id,
            "created_by": workflow.created_by,
            "automation_engine": workflow.automation_engine,
            "metadata": workflow.metadata
        }
    
    def get_workflow_templates(self, workflow_type: WorkflowType = None) -> Dict[str, Any]:
        """Get available workflow templates"""
        
        templates = list(self.workflow_templates.values())
        
        if workflow_type:
            templates = [t for t in templates if t.workflow_type == workflow_type]
        
        return {
            "total_templates": len(templates),
            "templates": [
                {
                    "template_id": t.template_id,
                    "name": t.name,
                    "description": t.description,
                    "workflow_type": t.workflow_type.value,
                    "category": t.category,
                    "task_count": len(t.task_templates),
                    "default_sla_hours": t.default_sla_hours,
                    "automation_level": t.automation_level,
                    "required_roles": t.required_roles,
                    "industry_specific": t.industry_specific,
                    "compliance_requirements": t.compliance_requirements,
                    "is_active": t.is_active
                }
                for t in templates
            ]
        }
    
    def get_workflow_analytics(self, law_firm_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get workflow analytics and performance metrics"""
        
        # Filter workflows
        workflows = list(self.workflows.values())
        if law_firm_id:
            workflows = [w for w in workflows if w.law_firm_id == law_firm_id]
        
        # Filter by date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        workflows = [w for w in workflows if w.created_at >= cutoff_date]
        
        if not workflows:
            return {
                "period_days": days,
                "total_workflows": 0,
                "message": "No workflows found for the specified period"
            }
        
        # Calculate analytics
        total_workflows = len(workflows)
        completed_workflows = len([w for w in workflows if w.status == WorkflowStatus.COMPLETED])
        running_workflows = len([w for w in workflows if w.status == WorkflowStatus.RUNNING])
        failed_workflows = len([w for w in workflows if w.status == WorkflowStatus.FAILED])
        
        completion_rate = (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0
        
        # Average completion time for completed workflows
        completed_with_times = [
            w for w in workflows 
            if w.status == WorkflowStatus.COMPLETED and w.started_at and w.completed_at
        ]
        
        avg_completion_hours = 0
        if completed_with_times:
            total_hours = sum(
                (w.completed_at - w.started_at).total_seconds() / 3600 
                for w in completed_with_times
            )
            avg_completion_hours = total_hours / len(completed_with_times)
        
        # Workflow type distribution
        type_distribution = {}
        for w in workflows:
            wtype = w.workflow_type.value
            type_distribution[wtype] = type_distribution.get(wtype, 0) + 1
        
        # Priority distribution
        priority_distribution = {}
        for w in workflows:
            priority = w.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        return {
            "period_days": days,
            "law_firm_id": law_firm_id,
            "total_workflows": total_workflows,
            "workflow_status": {
                "completed": completed_workflows,
                "running": running_workflows,
                "failed": failed_workflows,
                "completion_rate_percentage": round(completion_rate, 2)
            },
            "performance_metrics": {
                "average_completion_hours": round(avg_completion_hours, 2),
                "workflows_completed_on_time": completed_workflows,  # Simplified
                "average_tasks_per_workflow": sum(len(w.tasks) for w in workflows) / len(workflows) if workflows else 0
            },
            "workflow_type_distribution": type_distribution,
            "priority_distribution": priority_distribution,
            "automation_insights": {
                "fully_automated_workflows": len([w for w in workflows if w.metadata.get("automation_level") == "fully_automated"]),
                "semi_automated_workflows": len([w for w in workflows if w.metadata.get("automation_level") == "semi_automated"]),
                "manual_workflows": len([w for w in workflows if w.metadata.get("automation_level") == "manual"])
            }
        }

# Global instance
legal_workflow_automation = LegalWorkflowAutomation()

def get_workflow_automation() -> LegalWorkflowAutomation:
    """Get the global workflow automation instance"""
    return legal_workflow_automation