"""Unit tests for formatting/common.py helper functions."""

from mcp_server_spira.features.formatting.common import (
    _format_description,
    _format_header,
    _format_optional_field,
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


class TestFormatDescription:
    """Tests for _format_description helper function."""

    def test_format_description_with_text(self):
        """Test formatting description with text."""
        result = _format_description("This is a description")
        assert result == "This is a description"

    def test_format_description_with_none(self):
        """Test formatting description with None."""
        result = _format_description(None)
        assert result == ""

    def test_format_description_with_empty_string(self):
        """Test formatting description with empty string."""
        result = _format_description("")
        assert result == ""


class TestFormatOptionalField:
    """Tests for _format_optional_field helper function."""

    def test_format_optional_field_with_value(self):
        """Test formatting optional field with value."""
        result = _format_optional_field("Release", "1.0.0")
        assert result == "- **Release:** 1.0.0\n"

    def test_format_optional_field_with_prefix(self):
        """Test formatting optional field with prefix."""
        result = _format_optional_field("Release", 123, "RL:")
        assert result == "- **Release:** RL:123\n"

    def test_format_optional_field_with_none(self):
        """Test formatting optional field with None value."""
        result = _format_optional_field("Release", None)
        assert result == ""

    def test_format_optional_field_with_zero(self):
        """Test formatting optional field with zero value."""
        result = _format_optional_field("Count", 0)
        assert result == "- **Count:** 0\n"


class TestFormatHeader:
    """Tests for _format_header helper function."""

    def test_format_header_basic(self):
        """Test formatting basic header."""
        result = _format_header("Task", 123, "Fix bug", "TK")
        assert result == "## Task [TK:123] - Fix bug\n"

    def test_format_header_with_special_characters(self):
        """Test formatting header with special characters in name."""
        result = _format_header("Task", 456, "Fix bug & test", "TK")
        assert result == "## Task [TK:456] - Fix bug & test\n"


class TestFormatIncidentEdgeCases:
    """Tests for edge cases in format_incident."""

    def test_format_incident_with_detected_release_id_fallback(self):
        """Test incident formatting with DetectedReleaseId fallback."""
        incident = {
            "IncidentId": 1,
            "Name": "Test",
            "Description": "Test",
            "IncidentStatusName": "New",
            "IncidentTypeName": "Bug",
            "PriorityName": "1 - Critical",
            "SeverityName": "1 - Critical",
            "StartDate": "2024-01-15",
            "DetectedReleaseId": 10,  # Fallback when version number not available
        }
        result = format_incident(incident)
        assert "Detected in Release:** 10" in result

    def test_format_incident_with_resolved_release_id_fallback(self):
        """Test incident formatting with ResolvedReleaseId fallback."""
        incident = {
            "IncidentId": 1,
            "Name": "Test",
            "Description": "Test",
            "IncidentStatusName": "New",
            "IncidentTypeName": "Bug",
            "PriorityName": "1 - Critical",
            "SeverityName": "1 - Critical",
            "StartDate": "2024-01-15",
            "ResolvedReleaseId": 11,
        }
        result = format_incident(incident)
        assert "Planned for Release:** 11" in result

    def test_format_incident_with_verified_release_id_fallback(self):
        """Test incident formatting with VerifiedReleaseId fallback."""
        incident = {
            "IncidentId": 1,
            "Name": "Test",
            "Description": "Test",
            "IncidentStatusName": "New",
            "IncidentTypeName": "Bug",
            "PriorityName": "1 - Critical",
            "SeverityName": "1 - Critical",
            "StartDate": "2024-01-15",
            "VerifiedReleaseId": 12,
        }
        result = format_incident(incident)
        assert "Verified in Release:** 12" in result


class TestFormatTestRun:
    """Tests for format_test_run function."""

    def test_format_test_run_basic(self):
        """Test basic test run formatting."""
        test_run = {
            "TestRunId": 1,
            "Name": "Test Run 1",
            "ExecutionStatusId": 2,
        }
        result = format_test_run(test_run)
        assert "TR:1" in result
        assert "Test Run 1" in result

    def test_format_test_run_with_all_optional_fields(self):
        """Test test run formatting with all optional fields."""
        test_run = {
            "TestRunId": 1,
            "Name": "Test Run 1",
            "ExecutionStatusId": 2,
            "TestCaseId": 123,
            "TestSetId": 456,
            "ReleaseVersionNumber": "1.0.0",
            "StartDate": "2024-01-15",
            "EndDate": "2024-01-16",
        }
        result = format_test_run(test_run)
        assert "TC:123" in result
        assert "TX:456" in result
        assert "1.0.0" in result
        assert "2024-01-15" in result
        assert "2024-01-16" in result


class TestFormatAutomationHost:
    """Tests for format_automation_host function."""

    def test_format_automation_host_basic(self):
        """Test basic automation host formatting."""
        host = {
            "AutomationHostId": 1,
            "Name": "Test Host",
            "Description": "Test description",
        }
        result = format_automation_host(host)
        assert "AH:1" in result
        assert "Test Host" in result

    def test_format_automation_host_with_all_fields(self):
        """Test automation host formatting with all fields."""
        host = {
            "AutomationHostId": 1,
            "Name": "Test Host",
            "Description": "Test description",
            "Token": "abc123",
            "Active": True,
            "LastContactDate": "2024-01-15",
        }
        result = format_automation_host(host)
        assert "Token:** abc123" in result
        assert "Active:** True" in result
        assert "Last Contact:** 2024-01-15" in result


class TestFormatCapability:
    """Tests for format_capability function."""

    def test_format_capability_basic(self):
        """Test basic capability formatting."""
        capability = {
            "CapabilityId": 1,
            "Name": "Test Capability",
            "Description": "Test description",
            "StatusName": "Active",
            "TypeName": "Feature",
            "PriorityName": "High",
        }
        result = format_capability(capability)
        assert "CP:1" in result
        assert "Test Capability" in result
        assert "Active" in result

    def test_format_capability_with_all_optional_fields(self):
        """Test capability formatting with all optional fields."""
        capability = {
            "CapabilityId": 1,
            "Name": "Test Capability",
            "Description": "Test description",
            "StatusName": "Active",
            "TypeName": "Feature",
            "PriorityName": "High",
            "PercentComplete": 75,
            "MilestoneName": "Sprint 1",
            "RequirementCount": 10,
        }
        result = format_capability(capability)
        assert "75%" in result
        assert "Sprint 1" in result
        assert "# Requirements:** 10" in result


class TestFormatMilestone:
    """Tests for format_milestone function."""

    def test_format_milestone_basic(self):
        """Test basic milestone formatting."""
        milestone = {
            "MilestoneId": 1,
            "Name": "Sprint 1",
            "Description": "First sprint",
            "StatusName": "Active",
            "TypeName": "Sprint",
        }
        result = format_milestone(milestone)
        assert "GM:1" in result
        assert "Sprint 1" in result

    def test_format_milestone_with_dates(self):
        """Test milestone formatting with dates."""
        milestone = {
            "MilestoneId": 1,
            "Name": "Sprint 1",
            "Description": "First sprint",
            "StatusName": "Active",
            "TypeName": "Sprint",
            "PercentComplete": 50,
            "StartDate": "2024-01-01",
            "EndDate": "2024-01-15",
        }
        result = format_milestone(milestone)
        assert "50%" in result
        assert "2024-01-01" in result
        assert "2024-01-15" in result


class TestFormatRelease:
    """Tests for format_release function."""

    def test_format_release_basic(self):
        """Test basic release formatting."""
        release = {
            "ReleaseId": 1,
            "Name": "Release 1.0",
            "Description": "First release",
            "VersionNumber": "1.0.0",
            "ReleaseStatusName": "Active",
            "ReleaseTypeName": "Major",
        }
        result = format_release(release)
        assert "RL:1" in result
        assert "Release 1.0" in result
        assert "1.0.0" in result


class TestFormatRisk:
    """Tests for format_risk function."""

    def test_format_risk_basic(self):
        """Test basic risk formatting."""
        risk = {
            "RiskId": 1,
            "Name": "Security Risk",
            "Description": "Potential security issue",
            "RiskStatusName": "Open",
            "RiskTypeName": "Technical",
            "RiskProbabilityName": "High",
            "RiskImpactName": "Critical",
        }
        result = format_risk(risk)
        assert "RK:1" in result
        assert "Security Risk" in result

    def test_format_risk_with_optional_fields(self):
        """Test risk formatting with optional fields."""
        risk = {
            "RiskId": 1,
            "Name": "Security Risk",
            "Description": "Potential security issue",
            "RiskStatusName": "Open",
            "RiskTypeName": "Technical",
            "RiskProbabilityName": "High",
            "RiskImpactName": "Critical",
            "RiskExposure": 85,
            "ReviewDate": "2024-01-15",
        }
        result = format_risk(risk)
        assert "Exposure:** 85" in result
        assert "Review Date:** 2024-01-15" in result


class TestFormatProduct:
    """Tests for format_product function."""

    def test_format_product_with_all_optional_fields(self):
        """Test product formatting with all optional fields."""
        product = {
            "ProjectId": 1,
            "Name": "Test Product",
            "Description": "Test description",
            "Website": "https://example.com",
            "ProjectTemplateId": 5,
            "ProjectGroupId": 10,
            "PercentComplete": 75,
            "StartDate": "2024-01-01",
            "EndDate": "2024-12-31",
        }
        result = format_product(product)
        assert "https://example.com" in result
        assert "PT:5" in result
        assert "PG:10" in result
        assert "75%" in result


class TestFormatProductTemplate:
    """Tests for format_product_template function."""

    def test_format_product_template_basic(self):
        """Test basic product template formatting."""
        template = {
            "ProjectTemplateId": 1,
            "Name": "Agile Template",
            "Description": "Template for agile projects",
        }
        result = format_product_template(template)
        assert "PT:1" in result
        assert "Agile Template" in result


class TestFormatProgram:
    """Tests for format_program function."""

    def test_format_program_with_all_optional_fields(self):
        """Test program formatting with all optional fields."""
        program = {
            "ProgramId": 1,
            "Name": "Test Program",
            "Description": "Test description",
            "Website": "https://example.com",
            "ProjectTemplateId": 5,
            "PortfolioId": 10,
        }
        result = format_program(program)
        assert "https://example.com" in result
        assert "PT:5" in result
        assert "PF:10" in result


class TestFormatTestCaseFolderAndTestSetFolder:
    """Tests for folder formatting functions."""

    def test_format_test_case_folder(self):
        """Test test case folder formatting."""
        folder = {
            "Name": "Smoke Tests",
            "Description": "Critical smoke tests",
        }
        result = format_test_case_folder(folder)
        assert "Test Folder: Smoke Tests" in result
        assert "Critical smoke tests" in result

    def test_format_test_case_folder_no_description(self):
        """Test test case folder formatting without description."""
        folder = {
            "Name": "Smoke Tests",
            "Description": None,
        }
        result = format_test_case_folder(folder)
        assert "Test Folder: Smoke Tests" in result

    def test_format_test_set_folder(self):
        """Test test set folder formatting."""
        folder = {
            "Name": "Sprint 1",
            "Description": "Test sets for sprint 1",
        }
        result = format_test_set_folder(folder)
        assert "Test Set Folder: Sprint 1" in result
        assert "Test sets for sprint 1" in result

    def test_format_test_set_folder_no_description(self):
        """Test test set folder formatting without description."""
        folder = {
            "Name": "Sprint 1",
            "Description": None,
        }
        result = format_test_set_folder(folder)
        assert "Test Set Folder: Sprint 1" in result


class TestFormatTaskEdgeCases:
    """Tests for edge cases in format_task."""

    def test_format_task_with_zero_estimated_effort(self):
        """Test task formatting with zero estimated effort."""
        task = {
            "TaskId": 1,
            "Name": "Test Task",
            "Description": "Test",
            "TaskStatusName": "New",
            "TaskTypeName": "Development",
            "TaskPriorityName": "High",
            "EndDate": "2024-01-16",
            "EstimatedEffort": 0,  # Zero should not show effort info
        }
        result = format_task(task)
        # Zero estimated effort should not display effort info
        assert "Effort:" not in result or "0/" in result


class TestFormatRequirementEdgeCases:
    """Tests for edge cases in format_requirement."""

    def test_format_requirement_with_all_optional_fields(self):
        """Test requirement formatting with all optional fields."""
        requirement = {
            "RequirementId": 1,
            "Name": "Test Requirement",
            "Description": "Test description",
            "StatusName": "Accepted",
            "RequirementTypeName": "Feature",
            "ImportanceName": "Critical",
            "ReleaseVersionNumber": "1.0.0",
            "OwnerName": "John Doe",
        }
        result = format_requirement(requirement)
        assert "1.0.0" in result
        assert "John Doe" in result


class TestFormatTestCaseEdgeCases:
    """Tests for edge cases in format_test_case."""

    def test_format_test_case_with_all_optional_fields(self):
        """Test test case formatting with all optional fields."""
        test_case = {
            "TestCaseId": 1,
            "Name": "Test Case",
            "Description": "Test description",
            "TestCaseStatusName": "Ready",
            "TestCaseTypeName": "Functional",
            "TestCasePriorityName": "High",
            "ExecutionStatusName": "Passed",
            "ExecutionDate": "2024-01-15",
            "OwnerName": "John Doe",
        }
        result = format_test_case(test_case)
        assert "2024-01-15" in result
        assert "John Doe" in result


class TestFormatTestSetEdgeCases:
    """Tests for edge cases in format_test_set."""

    def test_format_test_set_with_all_optional_fields(self):
        """Test test set formatting with all optional fields."""
        test_set = {
            "TestSetId": 1,
            "Name": "Test Set",
            "Description": "Test description",
            "TestSetStatusName": "In Progress",
            "ReleaseVersionNumber": "1.0.0",
            "RecurrenceName": "Daily",
            "PlannedDate": "2024-01-15",
            "OwnerName": "John Doe",
        }
        result = format_test_set(test_set)
        assert "1.0.0" in result
        assert "Daily" in result
        assert "2024-01-15" in result
        assert "John Doe" in result
