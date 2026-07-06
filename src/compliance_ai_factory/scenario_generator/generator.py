import random
from datetime import datetime
from typing import Any

from compliance_ai_factory.common.models.base import (
    Asset,
    CompanySize,
    Employee,
    Industry,
    MaturityLevel,
    Organization,
    Scenario,
)
from compliance_ai_factory.scenario_generator import ScenarioGenerator

INDUSTRY_TEMPLATES: dict[str, dict[str, Any]] = {
    "technology": {
        "departments": ["Engineering", "Product", "Security", "IT Operations", "HR", "Finance", "Legal", "Sales", "Marketing"],
        "roles": ["Software Engineer", "DevOps Engineer", "Security Analyst", "Product Manager", "CTO", "CISO", "IT Manager"],
        "assets": [("Source Code Repo", "data"), ("Cloud Infrastructure", "infrastructure"), ("API Gateway", "software"), ("Employee Laptops", "hardware"), ("CI/CD Pipeline", "software")],
        "applications": ["GitHub Enterprise", "Jira", "Confluence", "Slack", "AWS Console", "Datadog", "PagerDuty", "Okta"],
        "infrastructure": ["AWS EC2", "AWS S3", "AWS RDS", "Docker", "Kubernetes", "Cloudflare CDN"],
        "cloud_services": ["AWS", "Cloudflare", "SendGrid", "Auth0"],
        "suppliers": ["AWS", "GitHub", "Atlassian", "Datadog"],
        "processes": ["SDLC", "Incident Response", "Change Management", "Vulnerability Management"],
        "threats": ["Software vulnerability exploitation", "Cloud misconfiguration", "Insider threat", "Supply chain attack"],
        "risks": ["Data breach via vulnerable dependency", "Cloud credential leakage", "Unauthorized code changes"],
        "regulations": ["ISO 27001", "GDPR", "SOC 2"],
    },
    "finance": {
        "departments": ["Retail Banking", "Investment Banking", "Risk Management", "Compliance", "IT Security", "Operations", "HR", "Finance", "Legal"],
        "roles": ["Financial Analyst", "Risk Officer", "Compliance Officer", "Security Architect", "IT Director", "Branch Manager"],
        "assets": [("Core Banking System", "software"), ("Customer Database", "data"), ("Trading Platform", "software"), ("ATM Network", "hardware"), ("SWIFT Terminal", "software")],
        "applications": ["Core Banking Platform", "SWIFT", "Bloomberg Terminal", "SAP", "Salesforce", "ServiceNow"],
        "infrastructure": ["Mainframe", "VMware Cluster", "Cisco Network", "F5 Load Balancers"],
        "cloud_services": ["AWS", "Azure", "Salesforce Cloud"],
        "suppliers": ["SWIFT", "Bloomberg", "SAP", "Microsoft"],
        "processes": ["Transaction Processing", "Fraud Detection", "KYC", "AML Screening", "Audit Reporting"],
        "threats": ["Financial fraud", "Wire transfer fraud", "Data exfiltration", "Ransomware", "Insider trading"],
        "risks": ["Financial loss from fraud", "Regulatory fines", "Reputational damage", "Customer data breach"],
        "regulations": ["ISO 27001", "PCI DSS", "SOX", "GLBA", "Basel III"],
    },
    "healthcare": {
        "departments": ["Clinical", "Nursing", "Pharmacy", "Laboratory", "Radiology", "IT", "Compliance", "HR", "Finance", "Administration"],
        "roles": ["Physician", "Nurse", "Pharmacist", "Lab Technician", "HIPAA Officer", "IT Security Manager", "Hospital Administrator"],
        "assets": [("EHR System", "software"), ("Patient Records Database", "data"), ("Medical Imaging System", "software"), ("Pharmacy Management", "software"), ("IoT Medical Devices", "hardware")],
        "applications": ["Epic EHR", "Cerner", "PACS System", "Lab Information System", "SAP", "Active Directory"],
        "infrastructure": ["Server Room", "Network Switches", "Workstations", "PACS Storage"],
        "cloud_services": ["AWS HealthLake", "Azure Healthcare API", "Salesforce Health Cloud"],
        "suppliers": ["Epic Systems", "Cerner", "GE Healthcare", "Philips", "McKesson"],
        "processes": ["Patient Admission", "Clinical Documentation", "Medication Administration", "Discharge Planning", "Incident Reporting"],
        "threats": ["Patient data breach", "Ransomware on medical devices", "Insider data access", "Phishing targeting staff"],
        "risks": ["HIPAA violation", "Patient safety incident", "Data loss", "Medical device compromise"],
        "regulations": ["ISO 27001", "HIPAA", "HITECH", "GDPR"],
    },
    "manufacturing": {
        "departments": ["Production", "Supply Chain", "Quality Assurance", "Maintenance", "IT/OT", "HSE", "HR", "Finance"],
        "roles": ["Plant Manager", "Production Engineer", "Quality Inspector", "Supply Chain Analyst", "OT Security Engineer", "EHS Manager"],
        "assets": [("PLC Controllers", "hardware"), ("SCADA System", "software"), ("Assembly Line", "hardware"), ("Inventory Database", "data"), ("Robotic Arm", "hardware")],
        "applications": ["SAP ERP", "MES System", "SCADA", "AutoCAD", "ServiceNow", "Active Directory"],
        "infrastructure": ["Factory Network (OT)", "Corporate Network (IT)", "Firewalls (IT/OT boundary)", "Industrial Wi-Fi"],
        "cloud_services": ["AWS IoT Core", "Azure IoT Hub", "SAP Cloud"],
        "suppliers": ["Siemens", "Rockwell Automation", "SAP", "ABB", "Fanuc"],
        "processes": ["Production Planning", "Inventory Management", "Quality Control", "Equipment Maintenance", "Shipment Logistics"],
        "threats": ["OT network intrusion", "Ransomware affecting production", "Supply chain compromise", "IP theft"],
        "risks": ["Production downtime", "Quality defects", "Supply chain disruption", "Industrial espionage"],
        "regulations": ["ISO 27001", "NIST CSF", "IEC 62443"],
    },
    "retail": {
        "departments": ["Store Operations", "E-Commerce", "Supply Chain", "Merchandising", "IT", "Marketing", "HR", "Finance"],
        "roles": ["Store Manager", "E-Commerce Manager", "Supply Chain Analyst", "Marketing Manager", "IT Support", "POS Administrator"],
        "assets": [("POS System", "software"), ("E-Commerce Platform", "software"), ("Customer Database", "data"), ("Inventory System", "software"), ("Payment Terminal", "hardware")],
        "applications": ["Shopify", "Salesforce", "SAP ERP", "Oracle Retail", "Kibana", "Active Directory"],
        "infrastructure": ["Store Network", "Warehouse Network", "POS Terminals", "Barcode Scanners"],
        "cloud_services": ["AWS", "Shopify Cloud", "Salesforce Cloud"],
        "suppliers": ["Shopify", "Salesforce", "SAP", "Visa", "Mastercard", "FedEx"],
        "processes": ["Point of Sale", "Order Fulfillment", "Inventory Management", "Returns Processing", "Customer Support"],
        "threats": ["Payment card data theft", "E-commerce fraud", "Loyalty program abuse", "Supply chain disruption"],
        "risks": ["PCI DSS non-compliance", "Customer data breach", "Fraud losses", "Inventory shrinkage"],
        "regulations": ["ISO 27001", "PCI DSS", "GDPR", "CCPA"],
    },
    "energy": {
        "departments": ["Generation", "Transmission", "Distribution", "Trading", "HSE", "IT/OT", "Engineering", "HR", "Finance"],
        "roles": ["Plant Operator", "Grid Analyst", "Energy Trader", "Safety Engineer", "OT Security Lead", "Maintenance Manager"],
        "assets": [("SCADA System", "software"), ("Power Generation Unit", "hardware"), ("Substation", "hardware"), ("Energy Trading Platform", "software"), ("Grid Sensor Network", "hardware")],
        "applications": ["SCADA", "EMS", "SAP", "Energy Trading Platform", "PI Historian", "Active Directory"],
        "infrastructure": ["Control Center", "Substations", "Transmission Lines", "Generator Units", "OT Network"],
        "cloud_services": ["Azure", "AWS", "OSIsoft Cloud"],
        "suppliers": ["Siemens Energy", "GE", "ABB", "Schneider Electric", "OSIsoft"],
        "processes": ["Energy Generation", "Load Balancing", "Grid Monitoring", "Maintenance Scheduling", "Incident Response"],
        "threats": ["Grid cyber attack", "SCADA compromise", "Physical security breach", "Data exfiltration", "Ransomware"],
        "risks": ["Grid instability", "Power outage", "Safety incident", "Regulatory penalty"],
        "regulations": ["ISO 27001", "NERC CIP", "IEC 62443"],
    },
    "government": {
        "departments": ["Administration", "IT", "Security", "Legal", "Finance", "HR", "Public Services", "Compliance"],
        "roles": ["IT Director", "Security Officer", "Compliance Manager", "System Administrator", "Records Manager", "FOIA Officer"],
        "assets": [("Citizen Database", "data"), ("Document Management System", "software"), ("Network Infrastructure", "infrastructure"), ("Classified Systems", "hardware"), ("Public Portal", "software")],
        "applications": ["SharePoint", "ServiceNow", "Active Directory", "SAP", "Case Management System", "Email System"],
        "infrastructure": ["Government Network", "Data Center", "Secure Facilities", "VPN Infrastructure"],
        "cloud_services": ["Azure Government", "AWS GovCloud"],
        "suppliers": ["Microsoft", "Dell", "Cisco", "Palantir", "Booz Allen"],
        "processes": ["Records Management", "FOIA Processing", "Security Clearance", "Incident Response", "Procurement"],
        "threats": ["Nation-state APT", "Insider threat", "Social engineering", "Supply chain compromise"],
        "risks": ["Classified data leak", "Service disruption", "Compliance violation", "Reputational damage"],
        "regulations": ["ISO 27001", "FISMA", "NIST SP 800-53", "FedRAMP"],
    },
    "education": {
        "departments": ["Academic Affairs", "Student Services", "IT", "Library", "Research", "Finance", "HR", "Admissions"],
        "roles": ["Professor", "IT Director", "System Admin", "Security Analyst", "Registrar", "Research Administrator"],
        "assets": [("Student Records System", "data"), ("LMS Platform", "software"), ("Research Database", "data"), ("Network Infrastructure", "infrastructure"), ("Library System", "software")],
        "applications": ["Canvas", "Blackboard", "Banner", "Workday", "Office 365", "Zoom", "Active Directory"],
        "infrastructure": ["Campus Network", "Data Center", "Wi-Fi Infrastructure", "Computer Labs"],
        "cloud_services": ["Office 365", "AWS", "Azure", "Google Workspace"],
        "suppliers": ["Microsoft", "Google", "Instructure", "Ellucian", "Dell"],
        "processes": ["Student Enrollment", "Grade Management", "Research Administration", "Grant Management", "Incident Response"],
        "threats": ["Student data breach", "Ransomware", "Phishing targeting staff/students", "Research IP theft"],
        "risks": ["FERPA violation", "Research data loss", "Service outage during exams", "Financial fraud"],
        "regulations": ["ISO 27001", "FERPA", "GDPR", "CMMC"],
    },
    "telecommunications": {
        "departments": ["Network Operations", "Engineering", "Customer Service", "Security", "Regulatory", "Finance", "HR", "Sales"],
        "roles": ["Network Engineer", "Security Engineer", "NOC Manager", "Regulatory Affairs Manager", "Customer Support Lead", "RF Engineer"],
        "assets": [("Core Network", "infrastructure"), ("BSS/OSS Systems", "software"), ("Customer Database", "data"), ("Cell Towers", "hardware"), ("Fiber Network", "infrastructure")],
        "applications": ["OSS/BSS Platform", "Network Monitoring", "Billing System", "CRM", "SAP", "Active Directory"],
        "infrastructure": ["Core Network", "Radio Access Network", "Fiber Backbone", "Data Centers", "NOC"],
        "cloud_services": ["AWS", "Azure", "Google Cloud"],
        "suppliers": ["Ericsson", "Nokia", "Huawei", "Cisco", "Juniper", "Oracle"],
        "processes": ["Network Provisioning", "Service Assurance", "Billing", "Customer Support", "Network Maintenance"],
        "threats": ["SS7/Diameter protocol attacks", "DDoS", "Customer data breach", "Infrastructure sabotage"],
        "risks": ["Service outage", "Customer data exposure", "Regulatory fine", "Fraud"],
        "regulations": ["ISO 27001", "GDPR", "ePrivacy", "PCI DSS"],
    },
    "transportation": {
        "departments": ["Operations", "Fleet Management", "Safety", "IT/OT", "Logistics", "Maintenance", "HR", "Finance"],
        "roles": ["Fleet Manager", "Safety Officer", "Logistics Coordinator", "OT Security Engineer", "Maintenance Supervisor", "IT Manager"],
        "assets": [("Fleet Tracking System", "software"), ("Vehicle Telematics", "hardware"), ("Logistics Platform", "software"), ("Maintenance Database", "data"), ("Warehouse Management", "software")],
        "applications": ["SAP TM", "Fleet Management System", "WMS", "ServiceNow", "Geotab", "Active Directory"],
        "infrastructure": ["Warehouse Network", "GPS Infrastructure", "Server Room", "IoT Sensor Network"],
        "cloud_services": ["AWS", "Azure", "SAP Cloud"],
        "suppliers": ["Geotab", "SAP", "Oracle", "Daimler", "Volvo", "CAT"],
        "processes": ["Route Planning", "Fleet Maintenance", "Load Management", "Driver Management", "Incident Response"],
        "threats": ["GPS spoofing", "Ransomware on logistics systems", "Vehicle malware", "Cargo theft (insider)"],
        "risks": ["Fleet downtime", "Safety incident", "Cargo loss", "Regulatory non-compliance"],
        "regulations": ["ISO 27001", "FMCSA", "GDPR"],
    },
}

COMPANY_NAME_TEMPLATES = {
    "technology": ["TechCorp", "InnovateSoft", "DataFlow Inc", "CyberDynamics", "NexGen Solutions", "PixelPath", "CloudBridge", "QuantumStack"],
    "finance": ["FinTrust Bank", "CapitalGuard", "Meridian Finance", "Apex Financial", "Sterling Bancorp", "Pinnacle Wealth"],
    "healthcare": ["MediCare Health", "VitalSigns Medical", "Pinnacle Health", "CareFirst Systems", "NovaMed", "HealthBridge"],
    "manufacturing": ["IndustrialForge", "PrecisionMfg", "Atlas Manufacturing", "Titan Industries", "Vertex Production", "OmegaWorks"],
    "retail": ["ShopRight", "RetailMax", "UrbanMart", "FreshChain", "ValueStore", "MarketSphere"],
    "energy": ["PowerGrid Corp", "Energen", "VoltGen Energy", "Apex Power", "Skyline Energy", "Pulse Utilities"],
    "government": ["CityGov Digital", "StateServe", "PublicAdmin", "CivicTech", "GovWorks", "NationalServices"],
    "education": ["EduGlobal University", "ScholarNet Academy", "LearnSphere Institute", "CampusConnect College", "KnowledgeFirst"],
    "telecommunications": ["ConnectTel", "SkyWave Networks", "Pulse Telecom", "LinkGlobal", "NetStream Communications", "ApexTel"],
    "transportation": ["TransLogistix", "FreightFlow", "CargoLink", "RoadRunner Transport", "ShipMaster Logistics", "GlobalHaul"],
}


class ConcreteScenarioGenerator(ScenarioGenerator):
    version = "1.0"

    def generate(self, seed: int | None = None) -> Scenario:
        rng = random.Random(seed)
        industry_names = list(INDUSTRY_TEMPLATES.keys())
        ind_name = rng.choice(industry_names)
        template = INDUSTRY_TEMPLATES[ind_name]

        industry = Industry(ind_name)
        company_names = COMPANY_NAME_TEMPLATES[ind_name]
        company_name = rng.choice(company_names)

        org = self._build_organization(company_name, industry, template, rng)

        scenario_id = f"SCN-{rng.randint(10000000, 99999999)}"

        return Scenario(
            id=scenario_id,
            version=self.version,
            created_at=datetime.utcnow(),
            organization=org,
        )

    def _build_organization(
        self, name: str, industry: Industry, template: dict[str, Any], rng: random.Random
    ) -> Organization:
        departments = template["departments"]
        size = rng.choices(
            list(CompanySize),
            weights=[0.1, 0.15, 0.35, 0.25, 0.15],
            k=1,
        )[0]

        size_multiplier = {
            CompanySize.STARTUP: (10, 50),
            CompanySize.SMALL: (50, 200),
            CompanySize.MEDIUM: (200, 1000),
            CompanySize.LARGE: (1000, 5000),
            CompanySize.ENTERPRISE: (5000, 50000),
        }[size]
        employee_count = rng.randint(*size_multiplier)

        maturity = rng.choices(
            list(MaturityLevel),
            weights=[0.1, 0.25, 0.35, 0.2, 0.1],
            k=1,
        )[0]

        employees = self._generate_employees(employee_count, departments, template["roles"], rng)
        assets = self._generate_assets(template["assets"], departments, rng)

        regs = template["regulations"]
        regulations = regs if "ISO 27001" in regs else ["ISO 27001"] + regs

        return Organization(
            name=name,
            industry=industry,
            size=size,
            maturity=maturity,
            description=f"{name} is a {industry.value} company operating in the compliance auditing space. "
                       f"With approximately {employee_count} employees across {len(departments)} departments, "
                       f"the organization maintains a {maturity.value} security maturity level.",
            departments=departments,
            employees=employees,
            assets=assets,
            applications=template["applications"],
            infrastructure=template["infrastructure"],
            cloud_services=template["cloud_services"],
            suppliers=template["suppliers"],
            processes=template["processes"],
            threats=template["threats"],
            risks=template["risks"],
            regulations=regulations or ["ISO 27001"],
        )

    def _generate_employees(
        self, count: int, departments: list[str], roles: list[str], rng: random.Random
    ) -> list[Employee]:
        employees: list[Employee] = []
        for i in range(min(count, 20)):
            dept = rng.choice(departments)
            role = rng.choice(roles)
            seniority = rng.choice(["junior", "mid", "senior", "lead", "manager", "director"])
            employees.append(Employee(
                id=f"EMP-{i + 1:04d}",
                name=f"Employee {i + 1}",
                role=role,
                department=dept,
                seniority=seniority,
            ))
        return employees

    def _generate_assets(
        self, asset_templates: list[tuple[str, str]], departments: list[str], rng: random.Random
    ) -> list[Asset]:
        assets: list[Asset] = []
        for i, (asset_name, asset_type) in enumerate(asset_templates):
            dept = rng.choice(departments)
            classification = rng.choice(["public", "internal", "confidential", "restricted"])
            assets.append(Asset(
                id=f"AST-{i + 1:04d}",
                name=asset_name,
                type=asset_type,
                owner=f"EMP-{rng.randint(1, 20):04d}",
                department=dept,
                classification=classification,
            ))
        return assets

    def list_industries(self) -> list[str]:
        return list(INDUSTRY_TEMPLATES.keys())
