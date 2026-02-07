"""Unit tests for formatting utilities."""

from mcp_server_spira.features.formatting import (
    format_automation_host,
    format_capability,
    format_incident,
    format_milestone,
    format_product,
    format_product_template,
    format_program,
    format_release,
    format_requirement,
    format_risk,
    format_task,
    format_test_case,
    format_test_case_folder,
    format_test_run,
    format_test_set,
    format_test_set_folder,
)


class TestFormatTask:
    """Tests for format_task function."""

    def test_format_task_with_all_fields(self):
        """Test formatting a task with all fields populated."""
        task = {
            "TaskId": 123,
            "Name": "Fix login bug",
            "Description": "Users cannot log in with special characters",
            "TaskStatusName": "In Progress",
            "TaskTypeName": "Development",
            "TaskPriorityName": "Critical",
            "EndDate": "2024-01-16T17:00:00Z",
        }
        result = format_task(task)

        assert "TK:123" in result
        assert "Fix login bug" in result
        assert "Users cannot log in with special characters" in result
        assert "In Progress" in result
        assert "Development" in result
        assert "Critical" in result
        assert "2024-01-16T17:00:00Z" in result

    def test_format_task_with_none_description(self):
        """Test formatting a task with None description."""
        task = {
            "TaskId": 456,
            "Name": "Test task",
            "Description": None,
            "TaskStatusName": "New",
            "TaskTypeName": "Bug",
            "TaskPriorityName": "High",
            "EndDate": "2024-02-01T00:00:00Z",
        }
        result = format_task(task)

        assert "TK:456" in result
        assert "Test task" in result
        assert "New" in result


class TestFormatIncident:
    """Tests for format_incident function."""

    def test_format_incident_with_all_fields(self):
        """Test formatting an incident with all fields populated."""
        incident = {
            "IncidentId": 789,
            "Name": "Login page crashes",
            "Description": "The login page crashes on mobile",
            "IncidentStatusName": "New",
            "IncidentTypeName": "Bug",
            "PriorityName": "1 - Critical",
            "SeverityName": "1 - Critical",
            "StartDate": "2024-01-15T09:00:00Z",
            "DetectedReleaseId": 8,
            "ResolvedReleaseId": 10,
            "VerifiedReleaseId": 11,
        }
        result = format_incident(incident)

        assert "IN:789" in result
        assert "Login page crashes" in result
        assert "The login page crashes on mobile" in result
        assert "New" in result
        assert "Bug" in result
        assert "1 - Critical" in result
        assert "**Detected in Release:** 8" in result
        assert "**Planned for Release:** 10" in result
        assert "**Verified in Release:** 11" in result

    def test_format_incident_with_none_releases(self):
        """Test formatting an incident with None release fields."""
        incident = {
            "IncidentId": 999,
            "Name": "Test incident",
            "Description": None,
            "IncidentStatusName": "Open",
            "IncidentTypeName": "Enhancement",
            "PriorityName": "3 - Medium",
            "SeverityName": "3 - Medium",
            "StartDate": "2024-02-01T00:00:00Z",
            "DetectedReleaseId": None,
            "ResolvedReleaseId": None,
            "VerifiedReleaseId": None,
        }
        result = format_incident(incident)

        assert "IN:999" in result
        assert "Test incident" in result
        assert "Detected in Release" not in result
        assert "Planned for Release" not in result
        assert "Verified in Release" not in result


class TestFormatRequirement:
    """Tests for format_requirement function."""

    def test_format_requirement_with_all_fields(self):
        """Test formatting a requirement with all fields populated."""
        requirement = {
            "RequirementId": 101,
            "Name": "User Authentication",
            "Description": "System must support user authentication",
            "StatusName": "Accepted",
            "RequirementTypeName": "Feature",
            "ImportanceName": "Critical",
            "ReleaseVersionNumber": "1.5.0",
        }
        result = format_requirement(requirement)

        assert "RQ:101" in result
        assert "User Authentication" in result
        assert "System must support user authentication" in result
        assert "Accepted" in result
        assert "Feature" in result
        assert "Critical" in result
        assert "1.5.0" in result

    def test_format_requirement_with_none_description(self):
        """Test formatting a requirement with None description."""
        requirement = {
            "RequirementId": 202,
            "Name": "Test requirement",
            "Description": None,
            "StatusName": "Draft",
            "RequirementTypeName": "Need",
            "ImportanceName": "High",
            "ReleaseVersionNumber": "2.0.0",
        }
        result = format_requirement(requirement)

        assert "RQ:202" in result
        assert "Test requirement" in result


class TestFormatTestCase:
    """Tests for format_test_case function."""

    def test_format_test_case_with_all_fields(self):
        """Test formatting a test case with all fields populated."""
        test_case = {
            "TestCaseId": 303,
            "Name": "Login Test",
            "Description": "Test user login functionality",
            "TestCaseStatusName": "Ready",
            "TestCaseTypeName": "Functional",
            "TestCasePriorityName": "High",
            "ExecutionStatusName": "Passed",
            "ExecutionDate": "2024-01-20T10:00:00Z",
        }
        result = format_test_case(test_case)

        assert "TC:303" in result
        assert "Login Test" in result
        assert "Test user login functionality" in result
        assert "Ready" in result
        assert "Functional" in result
        assert "High" in result
        assert "Passed" in result
        assert "2024-01-20T10:00:00Z" in result

    def test_format_test_case_with_none_description(self):
        """Test formatting a test case with None description."""
        test_case = {
            "TestCaseId": 404,
            "Name": "Test case",
            "Description": None,
            "TestCaseStatusName": "Draft",
            "TestCaseTypeName": "Regression",
            "TestCasePriorityName": "Medium",
            "ExecutionStatusName": "Not Run",
            "ExecutionDate": None,
        }
        result = format_test_case(test_case)

        assert "TC:404" in result
        assert "Test case" in result


class TestFormatTestCaseFolder:
    """Tests for format_test_case_folder function."""

    def test_format_test_case_folder_with_description(self):
        """Test formatting a test case folder with description."""
        folder = {
            "Name": "Smoke Tests",
            "Description": "Critical smoke tests for deployment",
        }
        result = format_test_case_folder(folder)

        assert "Smoke Tests" in result
        assert "Critical smoke tests for deployment" in result

    def test_format_test_case_folder_with_none_description(self):
        """Test formatting a test case folder with None description."""
        folder = {
            "Name": "Regression Tests",
            "Description": None,
        }
        result = format_test_case_folder(folder)

        assert "Regression Tests" in result


class TestFormatTestSet:
    """Tests for format_test_set function."""

    def test_format_test_set_with_all_fields(self):
        """Test formatting a test set with all fields populated."""
        test_set = {
            "TestSetId": 505,
            "Name": "Sprint 1 Tests",
            "Description": "All tests for sprint 1",
            "TestSetStatusName": "In Progress",
            "ReleaseVersionNumber": "1.0.0",
            "RecurrenceName": "Daily",
            "PlannedDate": "2024-01-25T00:00:00Z",
        }
        result = format_test_set(test_set)

        assert "TX:505" in result
        assert "Sprint 1 Tests" in result
        assert "All tests for sprint 1" in result
        assert "In Progress" in result
        assert "1.0.0" in result
        assert "Daily" in result
        assert "2024-01-25T00:00:00Z" in result

    def test_format_test_set_with_none_description(self):
        """Test formatting a test set with None description."""
        test_set = {
            "TestSetId": 606,
            "Name": "Test set",
            "Description": None,
            "TestSetStatusName": "Not Started",
            "ReleaseVersionNumber": "2.0.0",
            "RecurrenceName": "Once",
            "PlannedDate": None,
        }
        result = format_test_set(test_set)

        assert "TX:606" in result
        assert "Test set" in result


class TestFormatTestSetFolder:
    """Tests for format_test_set_folder function."""

    def test_format_test_set_folder_with_description(self):
        """Test formatting a test set folder with description."""
        folder = {
            "Name": "Release Tests",
            "Description": "Tests for release validation",
        }
        result = format_test_set_folder(folder)

        assert "Release Tests" in result
        assert "Tests for release validation" in result

    def test_format_test_set_folder_with_none_description(self):
        """Test formatting a test set folder with None description."""
        folder = {
            "Name": "Sprint Tests",
            "Description": None,
        }
        result = format_test_set_folder(folder)

        assert "Sprint Tests" in result


class TestFormatProduct:
    """Tests for format_product function."""

    def test_format_product_with_all_fields(self):
        """Test formatting a product with all fields populated."""
        product = {
            "ProjectId": 55,
            "Name": "Web Application",
            "Description": "Main web application",
            "Website": "https://example.com",
            "ProjectTemplateId": 1,
            "ProjectGroupId": 10,
            "PercentComplete": 75,
            "StartDate": "2024-01-01T00:00:00Z",
            "EndDate": "2024-12-31T23:59:59Z",
        }
        result = format_product(product)

        assert "PR:55" in result
        assert "Web Application" in result
        assert "Main web application" in result
        assert "https://example.com" in result
        assert "PT:1" in result
        assert "PG:10" in result
        assert "75%" in result

    def test_format_product_with_none_description(self):
        """Test formatting a product with None description."""
        product = {
            "ProjectId": 66,
            "Name": "Test Product",
            "Description": None,
            "Website": "https://test.com",
            "ProjectTemplateId": 2,
            "ProjectGroupId": 20,
            "PercentComplete": 0,
            "StartDate": None,
            "EndDate": None,
        }
        result = format_product(product)

        assert "PR:66" in result
        assert "Test Product" in result


class TestFormatProductTemplate:
    """Tests for format_product_template function."""

    def test_format_product_template_with_description(self):
        """Test formatting a product template with description."""
        template = {
            "ProjectTemplateId": 1,
            "Name": "Agile Template",
            "Description": "Template for agile projects",
        }
        result = format_product_template(template)

        assert "PT:1" in result
        assert "Agile Template" in result
        assert "Template for agile projects" in result

    def test_format_product_template_with_none_description(self):
        """Test formatting a product template with None description."""
        template = {
            "ProjectTemplateId": 2,
            "Name": "Waterfall Template",
            "Description": None,
        }
        result = format_product_template(template)

        assert "PT:2" in result
        assert "Waterfall Template" in result


class TestFormatProgram:
    """Tests for format_program function."""

    def test_format_program_with_all_fields(self):
        """Test formatting a program with all fields populated."""
        program = {
            "ProgramId": 10,
            "Name": "Enterprise Program",
            "Description": "Main enterprise program",
            "Website": "https://enterprise.example.com",
            "ProjectTemplateId": 1,
            "PortfolioId": 5,
        }
        result = format_program(program)

        assert "PG:10" in result
        assert "Enterprise Program" in result
        assert "Main enterprise program" in result
        assert "https://enterprise.example.com" in result
        assert "PT:1" in result
        assert "PF:5" in result

    def test_format_program_with_none_description(self):
        """Test formatting a program with None description."""
        program = {
            "ProgramId": 20,
            "Name": "Test Program",
            "Description": None,
            "Website": "https://test.example.com",
            "ProjectTemplateId": 2,
            "PortfolioId": 6,
        }
        result = format_program(program)

        assert "PG:20" in result
        assert "Test Program" in result


class TestFormatMilestone:
    """Tests for format_milestone function."""

    def test_format_milestone_with_all_fields(self):
        """Test formatting a milestone with all fields populated."""
        milestone = {
            "MilestoneId": 15,
            "Name": "Q1 Release",
            "Description": "First quarter release",
            "StatusName": "In Progress",
            "TypeName": "Major",
            "PercentComplete": 60,
            "StartDate": "2024-01-01T00:00:00Z",
            "EndDate": "2024-03-31T23:59:59Z",
        }
        result = format_milestone(milestone)

        assert "GM:15" in result
        assert "Q1 Release" in result
        assert "First quarter release" in result
        assert "In Progress" in result
        assert "Major" in result
        assert "60%" in result

    def test_format_milestone_with_none_description(self):
        """Test formatting a milestone with None description."""
        milestone = {
            "MilestoneId": 25,
            "Name": "Test Milestone",
            "Description": None,
            "StatusName": "Planned",
            "TypeName": "Minor",
            "PercentComplete": 0,
            "StartDate": None,
            "EndDate": None,
        }
        result = format_milestone(milestone)

        assert "GM:25" in result
        assert "Test Milestone" in result


class TestFormatRelease:
    """Tests for format_release function."""

    def test_format_release_with_all_fields(self):
        """Test formatting a release with all fields populated."""
        release = {
            "ReleaseId": 12,
            "Name": "Version 1.5",
            "Description": "Major feature release",
            "VersionNumber": "1.5.0",
            "ReleaseStatusName": "In Progress",
            "ReleaseTypeName": "Major",
            "PercentComplete": 45,
            "StartDate": "2024-01-15T00:00:00Z",
            "EndDate": "2024-02-15T23:59:59Z",
        }
        result = format_release(release)

        assert "RL:12" in result
        assert "Version 1.5" in result
        assert "Major feature release" in result
        assert "1.5.0" in result
        assert "In Progress" in result
        assert "Major" in result
        assert "45%" in result

    def test_format_release_with_none_description(self):
        """Test formatting a release with None description."""
        release = {
            "ReleaseId": 22,
            "Name": "Test Release",
            "Description": None,
            "VersionNumber": "2.0.0",
            "ReleaseStatusName": "Planned",
            "ReleaseTypeName": "Minor",
            "PercentComplete": 0,
            "StartDate": None,
            "EndDate": None,
        }
        result = format_release(release)

        assert "RL:22" in result
        assert "Test Release" in result


class TestFormatRisk:
    """Tests for format_risk function."""

    def test_format_risk_with_all_fields(self):
        """Test formatting a risk with all fields populated."""
        risk = {
            "RiskId": 30,
            "Name": "Security Vulnerability",
            "Description": "Potential security issue in authentication",
            "RiskStatusName": "Open",
            "RiskTypeName": "Technical",
            "RiskProbabilityName": "High",
            "RiskImpactName": "Critical",
            "RiskExposure": 85,
            "ReviewDate": "2024-02-01T00:00:00Z",
        }
        result = format_risk(risk)

        assert "RK:30" in result
        assert "Security Vulnerability" in result
        assert "Potential security issue in authentication" in result
        assert "Open" in result
        assert "Technical" in result
        assert "High" in result
        assert "Critical" in result
        assert "85" in result

    def test_format_risk_with_none_description(self):
        """Test formatting a risk with None description."""
        risk = {
            "RiskId": 40,
            "Name": "Test Risk",
            "Description": None,
            "RiskStatusName": "Closed",
            "RiskTypeName": "Business",
            "RiskProbabilityName": "Low",
            "RiskImpactName": "Low",
            "RiskExposure": 10,
            "ReviewDate": None,
        }
        result = format_risk(risk)

        assert "RK:40" in result
        assert "Test Risk" in result


class TestFormatTestRun:
    """Tests for format_test_run function."""

    def test_format_test_run_with_all_fields(self):
        """Test formatting a test run with all fields populated."""
        test_run = {
            "TestRunId": 707,
            "Name": "Login Test Run",
            "ExecutionStatusId": 2,
            "TestCaseId": 303,
            "TestSetId": 505,
            "ReleaseVersionNumber": "1.5.0",
            "StartDate": "2024-01-20T10:00:00Z",
            "EndDate": "2024-01-20T10:30:00Z",
        }
        result = format_test_run(test_run)

        assert "TR:707" in result
        assert "Login Test Run" in result
        assert "Passed" in result  # ExecutionStatusId 2 = Passed
        assert "TC:303" in result
        assert "TX:505" in result
        assert "1.5.0" in result

    def test_format_test_run_with_failed_status(self):
        """Test formatting a test run with failed status."""
        test_run = {
            "TestRunId": 808,
            "Name": "Failed Test Run",
            "ExecutionStatusId": 1,  # Failed
            "TestCaseId": 404,
            "TestSetId": 606,
            "ReleaseVersionNumber": "2.0.0",
            "StartDate": "2024-01-21T10:00:00Z",
            "EndDate": "2024-01-21T10:15:00Z",
        }
        result = format_test_run(test_run)

        assert "TR:808" in result
        assert "Failed" in result


class TestFormatAutomationHost:
    """Tests for format_automation_host function."""

    def test_format_automation_host_with_all_fields(self):
        """Test formatting an automation host with all fields populated."""
        host = {
            "AutomationHostId": 50,
            "Name": "Jenkins Server",
            "Description": "Main CI/CD server",
            "Token": "abc123xyz",
            "Active": True,
            "LastContactDate": "2024-01-20T15:30:00Z",
        }
        result = format_automation_host(host)

        assert "AH:50" in result
        assert "Jenkins Server" in result
        assert "Main CI/CD server" in result
        assert "abc123xyz" in result
        assert "True" in result
        assert "2024-01-20T15:30:00Z" in result

    def test_format_automation_host_with_none_description(self):
        """Test formatting an automation host with None description."""
        host = {
            "AutomationHostId": 60,
            "Name": "Test Host",
            "Description": None,
            "Token": "token456",
            "Active": False,
            "LastContactDate": None,
        }
        result = format_automation_host(host)

        assert "AH:60" in result
        assert "Test Host" in result


class TestFormatCapability:
    """Tests for format_capability function."""

    def test_format_capability_with_all_fields(self):
        """Test formatting a capability with all fields populated."""
        capability = {
            "CapabilityId": 70,
            "Name": "User Management",
            "Description": "Capability to manage users",
            "StatusName": "In Progress",
            "TypeName": "Feature",
            "PriorityName": "High",
            "PercentComplete": 65,
            "MilestoneName": "Q1 Release",
            "RequirementCount": 12,
        }
        result = format_capability(capability)

        assert "CP:70" in result
        assert "User Management" in result
        assert "Capability to manage users" in result
        assert "In Progress" in result
        assert "Feature" in result
        assert "High" in result
        assert "65%" in result
        assert "Q1 Release" in result
        assert "12" in result

    def test_format_capability_with_none_description(self):
        """Test formatting a capability with None description."""
        capability = {
            "CapabilityId": 80,
            "Name": "Test Capability",
            "Description": None,
            "StatusName": "Planned",
            "TypeName": "Enhancement",
            "PriorityName": "Medium",
            "PercentComplete": 0,
            "MilestoneName": "Q2 Release",
            "RequirementCount": 5,
        }
        result = format_capability(capability)

        assert "CP:80" in result
        assert "Test Capability" in result
